import sys
import os
import uuid
import json
import random
from datetime import datetime, timedelta, timezone

# Add backend directory to python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from sqlalchemy.orm import Session
from src.database.connection import engine, SessionLocal
from src.models.role import Role
from src.models.user import User
from src.models.store import Store
from src.models.product import Product
from src.models.packaging_material import PackagingMaterial
from src.models.packaging_rule import PackagingRule
from src.models.order import Order, OrderItem
from src.models.packing_verification import PackingVerification, RuleViolation
from src.security.hashing import get_password_hash
from src.services.rule_engine import RuleEngine

def seed_demo_dataset():
    random.seed(42)
    session = SessionLocal()

    print("==================================================")
    print(" SmartPack AI - Generating Reproducible Synthetic Dataset")
    print("==================================================")

    try:
        # 1. Fetch Roles
        admin_role = session.query(Role).filter_by(name="ADMIN").first()
        supervisor_role = session.query(Role).filter_by(name="SUPERVISOR").first()
        operator_role = session.query(Role).filter_by(name="OPERATOR").first()

        if not admin_role or not supervisor_role or not operator_role:
            print("ERROR: Roles must be seeded first via Alembic migration.")
            return

        # 2. Seed Demo Admin User
        admin_email = "admin@smartpack.ai"
        existing_admin = session.query(User).filter_by(email=admin_email).first()
        if not existing_admin:
            demo_admin = User(
                full_name="SmartPack System Administrator",
                email=admin_email,
                password_hash=get_password_hash("SmartPackAdmin123!"),
                role_id=admin_role.id,
                is_active=True,
                is_verified=True
            )
            session.add(demo_admin)
            session.commit()
            session.refresh(demo_admin)
            print(f"[OK] Seeded Demo Admin: {admin_email}")

        # 3. Seed Stores (10 Stores)
        print("Seeding Dark Stores...")
        store_configs = [
            ("STR-BLR-01", "Indiranagar Dark Store", "Bangalore, KA"),
            ("STR-BLR-02", "Koramangala Dark Store", "Bangalore, KA"),
            ("STR-BLR-03", "HSR Layout Fulfillment Center", "Bangalore, KA"),
            ("STR-BOM-01", "Bandra West Micro-Fulfillment", "Mumbai, MH"),
            ("STR-BOM-02", "Andheri East Operations Center", "Mumbai, MH"),
            ("STR-DEL-01", "Connaught Place Express Hub", "Delhi, DL"),
            ("STR-DEL-02", "Gurgaon CyberHub Facility", "Gurgaon, HR"),
            ("STR-HYD-01", "Gachibowli Dark Store", "Hyderabad, TS"),
            ("STR-MAA-01", "T. Nagar Fulfillment Hub", "Chennai, TN"),
            ("STR-CCU-01", "Salt Lake City Operations", "Kolkata, WB"),
        ]

        stores = []
        for code, name, loc in store_configs:
            store = session.query(Store).filter_by(store_code=code).first()
            if not store:
                store = Store(store_code=code, store_name=name, location=loc, is_active=True)
                session.add(store)
                session.commit()
                session.refresh(store)
            stores.append(store)
        print(f"[OK] Total Stores: {len(stores)}")

        # 4. Seed Operators & Supervisors (30 Users)
        print("Seeding Operators & Supervisors...")
        first_names = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Neha", "Rahul", "Sneha", "Karan", "Kavya", "Arjun", "Meera", "Aditya", "Pooja", "Siddharth"]
        last_names = ["Sharma", "Verma", "Patel", "Rao", "Nair", "Gupta", "Singh", "Mukherjee", "Reddy", "Joshi", "Iyer", "Deshmukh", "Chopra", "Kulkarni", "Mehta"]

        operators = []
        for i in range(30):
            fn = first_names[i % len(first_names)]
            ln = last_names[i % len(last_names)]
            email = f"operator.{fn.lower()}.{ln.lower()}{i+1}@smartpack.ai"
            user = session.query(User).filter_by(email=email).first()
            if not user:
                assigned_role = supervisor_role if i < 5 else operator_role
                assigned_store = stores[i % len(stores)]
                user = User(
                    full_name=f"{fn} {ln}",
                    email=email,
                    password_hash=get_password_hash("OperatorPass123!"),
                    role_id=assigned_role.id,
                    store_id=assigned_store.id,
                    is_active=True,
                    is_verified=True,
                    last_login_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            operators.append(user)
        print(f"[OK] Total Operators & Supervisors: {len(operators)}")

        # 5. Seed Packaging Materials (12 Materials)
        print("Seeding Packaging Materials...")
        materials_data = [
            ("MAT-BOX-S", "Small Corrugated Carton", "CARTON", "SMALL", "MEDIUM", "AMBIENT"),
            ("MAT-BOX-M", "Medium Heavy-Duty Carton", "CARTON", "MEDIUM", "HIGH", "AMBIENT"),
            ("MAT-BOX-L", "Large Extra-Strength Carton", "CARTON", "LARGE", "MAXIMUM", "AMBIENT"),
            ("MAT-BUBBLE-01", "Air Bubble Cushioning Wrap", "BUBBLE_WRAP", "SMALL", "HIGH", "ALL"),
            ("MAT-SLEEVE-01", "Protective Bottle Sleeve", "PROTECTIVE_SLEEVE", "SMALL", "HIGH", "ALL"),
            ("MAT-BAG-PLASTIC", "Heavy-Gauge Plastic Courier Bag", "PLASTIC_BAG", "MEDIUM", "LOW", "AMBIENT"),
            ("MAT-BAG-PAPER", "Recycled Eco Paper Bag", "PAPER_BAG", "MEDIUM", "LOW", "AMBIENT"),
            ("MAT-ICE-PACK", "Thermal Cold Gel Ice Pack", "ICE_PACK", "SMALL", "MEDIUM", "COLD_CHAIN"),
            ("MAT-THERMAL-POUCH", "Insulated Cold-Chain Pouch", "INSULATED_POUCH", "MEDIUM", "HIGH", "COLD_CHAIN"),
            ("MAT-FOAM-WRAP", "Anti-Scratch Foam Sheet", "FOAM_WRAP", "SMALL", "MEDIUM", "ALL"),
            ("MAT-KRAFT-PAPER", "Kraft Cushioning Filler", "KRAFT_FILLER", "MEDIUM", "LOW", "ALL"),
            ("MAT-HEAVY-CARTON", "Double-Wall Rigid Heavy Box", "CARTON", "LARGE", "MAXIMUM", "ALL"),
        ]

        materials = []
        for code, name, m_type, cap, prot, temp in materials_data:
            mat = session.query(PackagingMaterial).filter_by(code=code).first()
            if not mat:
                mat = PackagingMaterial(
                    code=code,
                    name=name,
                    material_type=m_type,
                    capacity_size=cap,
                    protection_level=prot,
                    temperature_suitability=temp,
                    is_active=True
                )
                session.add(mat)
                session.commit()
                session.refresh(mat)
            materials.append(mat)
        print(f"[OK] Total Packaging Materials: {len(materials)}")

        # 6. Seed Packaging Rules (40 Rules)
        print("Seeding Packaging Rules...")
        rules_data = [
            ("RULE-FRAGILE-01", "Fragile Cushioning Mandatory", "Fragile glass/ceramic items require bubble wrap or protective sleeve.", "FRAGILE_PROTECTION", "BUBBLE_WRAP", "HIGH", "CRITICAL", 40),
            ("RULE-COLD-01", "Cold-Chain Thermal Isolation", "Perishable or frozen products require gel ice pack and thermal pouch.", "COLD_CHAIN_REQUIRED", "ICE_PACK", "HIGH", "CRITICAL", 40),
            ("RULE-LIQUID-01", "Liquid & Fragile Isolation", "Liquid containers must be sealed in leak barriers away from fragile goods.", "LIQUID_SEPARATION", "PROTECTIVE_SLEEVE", "HIGH", "HIGH", 25),
            ("RULE-CRUSH-01", "Crush-Sensitive Protection", "Soft or bakery items must be packed in a rigid carton on top.", "CRUSH_PROTECTION", "CARTON", "MEDIUM", "MEDIUM", 15),
            ("RULE-CAPACITY-01", "Package Capacity Fit", "Multi-item orders require appropriate volume carton.", "CAPACITY_FIT", "CARTON", "MEDIUM", "LOW", 10),
        ]
        # Generate 35 additional granular sub-rules for quality assurance metrics
        for idx in range(6, 41):
            rules_data.append((
                f"RULE-QA-{idx:02d}",
                f"Quality Rule #{idx:02d} Integrity Check",
                f"Quality control specification for dark store packaging compliance rule {idx}.",
                "QUALITY_ASSURANCE",
                None,
                "MEDIUM",
                "LOW",
                10
            ))

        rules = []
        for code, name, desc, r_type, req_mat, min_prot, sev, ded in rules_data:
            r = session.query(PackagingRule).filter_by(rule_code=code).first()
            if not r:
                r = PackagingRule(
                    rule_code=code,
                    name=name,
                    description=desc,
                    rule_type=r_type,
                    required_material_type=req_mat,
                    min_protection_level=min_prot,
                    severity=sev,
                    deduction_points=ded,
                    is_active=True
                )
                session.add(r)
                session.commit()
                session.refresh(r)
            rules.append(r)
        print(f"[OK] Total Packaging Rules: {len(rules)}")

        # 7. Seed Products (200 Products)
        print("Seeding Catalog Products...")
        categories = [
            ("Beverages & Liquids", True, "AMBIENT", False, False),
            ("Dairy & Cold Goods", False, "COLD", False, False),
            ("Frozen Foods", False, "FROZEN", False, False),
            ("Bakery & Confectionery", False, "AMBIENT", False, True),
            ("Glass Bottled Preserves", True, "AMBIENT", True, False),
            ("Personal Care & Cosmetics", True, "AMBIENT", False, False),
            ("Household Cleaners", True, "AMBIENT", False, False),
            ("Snacks & Cereals", False, "AMBIENT", False, True),
            ("Fresh Produce & Fruits", False, "COLD", True, True),
            ("Electronics & Accessories", False, "AMBIENT", True, False),
        ]

        products = []
        prod_count = session.query(Product).count()
        if prod_count < 200:
            for i in range(1, 201):
                sku = f"SKU-PRD-{i:04d}"
                p_existing = session.query(Product).filter_by(sku=sku).first()
                if not p_existing:
                    cat_name, is_liq, temp_req, is_frag, is_crush = categories[i % len(categories)]
                    prod_name = f"{cat_name[:-1] if cat_name.endswith('s') else cat_name} Item #{i:03d}"
                    weight = round(random.uniform(0.1, 4.5), 2)
                    dims = f"{random.randint(5, 30)}x{random.randint(5, 20)}x{random.randint(5, 15)} cm"

                    product = Product(
                        sku=sku,
                        name=prod_name,
                        category=cat_name,
                        weight=weight,
                        dimensions=dims,
                        is_fragile=is_frag or (i % 7 == 0),
                        temperature_req=temp_req,
                        is_liquid=is_liq or (i % 9 == 0),
                        is_crush_sensitive=is_crush or (i % 6 == 0),
                        is_active=True
                    )
                    session.add(product)
                    session.commit()
                    session.refresh(product)
                    products.append(product)
                else:
                    products.append(p_existing)
        else:
            products = session.query(Product).all()
        print(f"[OK] Total Catalog Products: {len(products)}")

        # 8. Seed Orders & Packing Verifications (1,000 Orders)
        print("Seeding Orders and Packing Verifications (1,000 Orders)...")
        existing_orders_count = session.query(Order).count()
        if existing_orders_count < 1000:
            to_create = 1000 - existing_orders_count
            start_date = datetime.now(timezone.utc) - timedelta(days=30)

            for i in range(to_create):
                idx = existing_orders_count + i + 1
                order_num = f"ORD-2026-{idx:05d}"
                store = random.choice(stores)
                op_user = random.choice(operators)
                created_dt = start_date + timedelta(minutes=i * 40)

                # Decide packaging scenario
                scenario = i % 10 # 0, 1, 2 failure edge cases; 3..9 pass/warning

                order = Order(
                    order_number=order_num,
                    store_id=store.id,
                    operator_id=op_user.id,
                    status="CREATED",
                    verification_status="UNVERIFIED",
                    created_at=created_dt,
                    updated_at=created_dt
                )
                session.add(order)
                session.flush()

                # Add 2-4 items to order
                order_items_list = []
                num_items = random.randint(2, 4)
                sample_products = random.sample(products, num_items)

                if scenario == 1:
                    # Fragile failure scenario
                    sample_products[0] = next(p for p in products if p.is_fragile)
                elif scenario == 2:
                    # Frozen failure scenario
                    sample_products[0] = next(p for p in products if p.temperature_req in ["FROZEN", "COLD"])
                elif scenario == 3:
                    # Liquid + fragile failure scenario
                    sample_products[0] = next(p for p in products if p.is_liquid)
                    sample_products[1] = next(p for p in products if p.is_fragile)

                for p in sample_products:
                    item = OrderItem(
                        order_id=order.id,
                        product_id=p.id,
                        quantity=random.randint(1, 3),
                        item_attributes_snapshot=str({
                            "sku": p.sku,
                            "name": p.name,
                            "is_fragile": p.is_fragile,
                            "temperature_req": p.temperature_req,
                            "is_liquid": p.is_liquid,
                            "is_crush_sensitive": p.is_crush_sensitive
                        })
                    )
                    session.add(item)
                    order_items_list.append(item)

                session.commit()

                # Perform verification evaluation for ~80% of orders
                if i % 5 != 0:
                    selected_mats = []
                    if scenario == 1:
                        # Missing fragile protection
                        selected_mats = [m for m in materials if m.material_type in ["PAPER_BAG", "PLASTIC_BAG"]]
                    elif scenario == 2:
                        # Missing cold-chain
                        selected_mats = [m for m in materials if m.material_type == "CARTON"]
                    elif scenario == 3:
                        # Missing liquid/fragile separation
                        selected_mats = [m for m in materials if m.material_type == "PAPER_BAG"]
                    else:
                        # Good packaging
                        selected_mats = [
                            next(m for m in materials if m.material_type == "CARTON"),
                            next(m for m in materials if m.material_type in ["BUBBLE_WRAP", "ICE_PACK", "PROTECTIVE_SLEEVE"])
                        ]

                    if not selected_mats:
                        selected_mats = [materials[0]]

                    order_obj = session.query(Order).filter_by(id=order.id).first()
                    score, status_outcome, v_list, r_list = RuleEngine.evaluate_packing(
                        order=order_obj,
                        selected_materials=selected_mats,
                        has_valid_image=True
                    )

                    pv = PackingVerification(
                        order_id=order.id,
                        operator_id=op_user.id,
                        image_path=f"uploads/synthetic_packing_{i:04d}.jpg",
                        packing_score=score,
                        status=status_outcome,
                        violations_json=json.dumps([v.model_dump() for v in v_list]),
                        recommendations_json=json.dumps(r_list),
                        verified_at=created_dt + timedelta(minutes=15)
                    )
                    session.add(pv)
                    session.flush()

                    for v in v_list:
                        rv = RuleViolation(
                            verification_id=pv.id,
                            rule_code=v.rule_code,
                            rule_name=v.rule_name,
                            severity=v.severity,
                            description=v.description,
                            detected_value=v.detected_value,
                            expected_value=v.expected_value,
                            deduction=v.deduction,
                            created_at=created_dt + timedelta(minutes=15)
                        )
                        session.add(rv)

                    order.verification_status = status_outcome
                    order.packing_score = score
                    order.status = "VERIFIED"
                    session.commit()

        total_orders_final = session.query(Order).count()
        total_verifications_final = session.query(PackingVerification).count()
        print(f"[OK] Total Orders in Database: {total_orders_final}")
        print(f"[OK] Total Packing Verifications in Database: {total_verifications_final}")

        print("==================================================")
        print(" DEMO DATASET GENERATION COMPLETED SUCCESSFULLY")
        print("==================================================")

    except Exception as e:
        session.rollback()
        print(f"CRITICAL ERROR during synthetic dataset generation: {str(e)}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    seed_demo_dataset()
