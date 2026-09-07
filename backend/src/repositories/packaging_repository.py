import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.packaging_material import PackagingMaterial
from src.models.packaging_rule import PackagingRule
from src.schemas.packaging import PackagingMaterialCreate, PackagingRuleCreate

class PackagingRepository:
    def __init__(self, db: Session):
        self.db = db

    # Materials
    def get_material_by_id(self, material_id: uuid.UUID) -> Optional[PackagingMaterial]:
        return self.db.query(PackagingMaterial).filter(PackagingMaterial.id == material_id).first()

    def get_material_by_code(self, code: str) -> Optional[PackagingMaterial]:
        return self.db.query(PackagingMaterial).filter(PackagingMaterial.code == code.strip().upper()).first()

    def get_all_materials(self, is_active_only: bool = True) -> List[PackagingMaterial]:
        query = self.db.query(PackagingMaterial)
        if is_active_only:
            query = query.filter(PackagingMaterial.is_active.is_(True))
        return query.order_by(PackagingMaterial.name).all()

    def create_material(self, mat_in: PackagingMaterialCreate) -> PackagingMaterial:
        mat = PackagingMaterial(
            code=mat_in.code.strip().upper(),
            name=mat_in.name.strip(),
            material_type=mat_in.material_type,
            capacity_size=mat_in.capacity_size,
            protection_level=mat_in.protection_level,
            temperature_suitability=mat_in.temperature_suitability,
            is_active=mat_in.is_active
        )
        self.db.add(mat)
        self.db.commit()
        self.db.refresh(mat)
        return mat

    # Rules
    def get_rule_by_id(self, rule_id: uuid.UUID) -> Optional[PackagingRule]:
        return self.db.query(PackagingRule).filter(PackagingRule.id == rule_id).first()

    def get_all_rules(self, is_active_only: bool = True) -> List[PackagingRule]:
        query = self.db.query(PackagingRule)
        if is_active_only:
            query = query.filter(PackagingRule.is_active.is_(True))
        return query.order_by(PackagingRule.severity.desc(), PackagingRule.rule_code).all()

    def create_rule(self, rule_in: PackagingRuleCreate) -> PackagingRule:
        rule = PackagingRule(
            rule_code=rule_in.rule_code.strip().upper(),
            name=rule_in.name.strip(),
            description=rule_in.description.strip(),
            rule_type=rule_in.rule_type,
            condition_json=rule_in.condition_json,
            required_material_type=rule_in.required_material_type,
            min_protection_level=rule_in.min_protection_level,
            severity=rule_in.severity,
            deduction_points=rule_in.deduction_points,
            is_active=rule_in.is_active
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
