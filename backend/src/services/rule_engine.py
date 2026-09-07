import json
from typing import List, Dict, Any, Tuple
from src.models.order import Order, OrderItem
from src.models.packaging_material import PackagingMaterial
from src.schemas.packing_verification import RuleViolationResponse

class RuleEngine:
    """
    SmartPack AI Deterministic Rule-Based Packing Quality Verification Engine.
    Evaluates order items and product physical sensitivity flags against declared packaging materials.
    Produces deterministic Packing Score (0-100), Status (PASS/WARNING/FAIL), violations list, and recommendations.
    """

    @staticmethod
    def evaluate_packing(
        order: Order,
        selected_materials: List[PackagingMaterial],
        has_valid_image: bool = True
    ) -> Tuple[int, str, List[RuleViolationResponse], List[str]]:
        """
        Executes rule validation checks on order and selected packaging materials.
        """
        violations: List[RuleViolationResponse] = []
        recommendations: List[str] = []

        items = order.items or []
        has_fragile = any(item.product.is_fragile for item in items if item.product)
        has_cold = any(item.product.temperature_req in ["FROZEN", "COLD"] for item in items if item.product)
        has_liquid = any(item.product.is_liquid for item in items if item.product)
        has_crush = any(item.product.is_crush_sensitive for item in items if item.product)
        total_weight = sum(item.product.weight * item.quantity for item in items if item.product)
        total_qty = sum(item.quantity for item in items)

        material_types = [m.material_type for m in selected_materials]
        protection_levels = [m.protection_level for m in selected_materials]
        temp_suitabilities = [m.temperature_suitability for m in selected_materials]

        # 1. Fragile Protection Rule
        if has_fragile:
          has_fragile_protection = (
              any(pt in ["HIGH", "MAXIMUM"] for pt in protection_levels) or
              any(mt in ["BUBBLE_WRAP", "PROTECTIVE_SLEEVE"] for mt in material_types)
          )
          if not has_fragile_protection:
              violations.append(RuleViolationResponse(
                  rule_code="RULE-FRAGILE-01",
                  rule_name="Fragile Cushioning Mandatory",
                  severity="CRITICAL",
                  description="Fragile item(s) packed without required protective bubble wrap or sleeve.",
                  detected_value="No bubble wrap or protective sleeve selected",
                  expected_value="BUBBLE_WRAP or HIGH protection carton",
                  deduction=40
              ))
              recommendations.append("Wrap fragile items in bubble wrap or protective sleeve before sealing package.")

        # 2. Cold Chain / Frozen Temperature Rule
        if has_cold:
            has_cold_protection = (
                any(ts == "COLD_CHAIN" for ts in temp_suitabilities) or
                any(mt == "ICE_PACK" for mt in material_types)
            )
            if not has_cold_protection:
                violations.append(RuleViolationResponse(
                    rule_code="RULE-COLD-01",
                    rule_name="Cold-Chain Thermal Isolation",
                    severity="CRITICAL",
                    description="Perishable / frozen item(s) packed without thermal ice pack or insulated packaging.",
                    detected_value="Standard ambient packaging",
                    expected_value="ICE_PACK or COLD_CHAIN thermal bag",
                    deduction=40
                ))
                recommendations.append("Add thermal ice pack and place perishable items in an insulated pouch.")

        # 3. Liquid and Fragile Separation Rule
        if has_liquid and has_fragile:
            has_separation = (
                "PROTECTIVE_SLEEVE" in material_types or
                "PLASTIC_BAG" in material_types or
                any(pt in ["HIGH", "MAXIMUM"] for pt in protection_levels)
            )
            if not has_separation:
                violations.append(RuleViolationResponse(
                    rule_code="RULE-LIQUID-01",
                    rule_name="Liquid & Fragile Isolation",
                    severity="HIGH",
                    description="Liquid containers and fragile items packed together without protective leak barrier.",
                    detected_value="Unsealed co-packed liquid and fragile goods",
                    expected_value="Sealed leak barrier / protective sleeve",
                    deduction=25
                ))
                recommendations.append("Enclose liquid containers in a sealed bag to protect fragile items from leakage.")

        # 4. Heavy & Crush Sensitivity Rule
        if has_crush and total_weight > 2.0:
            has_rigid = "CARTON" in material_types
            if not has_rigid:
                violations.append(RuleViolationResponse(
                    rule_code="RULE-CRUSH-01",
                    rule_name="Crush-Sensitive Protection",
                    severity="MEDIUM",
                    description="Crush-sensitive items packed in non-rigid bag under heavy load.",
                    detected_value="Flexible bag used for heavy order",
                    expected_value="Rigid CARTON packaging",
                    deduction=15
                ))
                recommendations.append("Use a rigid corrugated carton and place crush-sensitive goods on top.")

        # 5. Capacity Fit Rule
        if total_qty > 5 or total_weight > 5.0:
            has_adequate_capacity = any(m.capacity_size in ["MEDIUM", "LARGE"] for m in selected_materials)
            if not has_adequate_capacity:
                violations.append(RuleViolationResponse(
                    rule_code="RULE-CAPACITY-01",
                    rule_name="Package Capacity Fit",
                    severity="LOW",
                    description="Package volume capacity is small for order size.",
                    detected_value="Small capacity packaging",
                    expected_value="MEDIUM or LARGE container capacity",
                    deduction=10
                ))
                recommendations.append("Upgrade packaging capacity to MEDIUM or LARGE size.")

        # Image validation deduction if image missing
        if not has_valid_image:
            violations.append(RuleViolationResponse(
                rule_code="RULE-IMG-01",
                rule_name="Packing Image Verification Required",
                severity="MEDIUM",
                description="Packing proof image is missing or invalid.",
                detected_value="No image uploaded",
                expected_value="Valid packing verification photograph",
                deduction=15
            ))
            recommendations.append("Upload a clear photograph of packed items before dispatch.")

        # Calculate final deterministic score
        total_deductions = sum(v.deduction for v in violations)
        packing_score = max(0, 100 - total_deductions)

        # Status mapping
        if packing_score >= 80:
            status = "PASS"
        elif packing_score >= 60:
            status = "WARNING"
        else:
            status = "FAIL"

        if status == "PASS" and not recommendations:
            recommendations.append("Packaging complies with all SmartPack quality standards. Ready for dispatch.")

        return packing_score, status, violations, recommendations
