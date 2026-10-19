"""
Database Initialization & Scenario Seeding.
"""

from app.db.session import engine, SessionLocal, Base
from app.db.models import Scenario
from app.engine.scenarios_data import SCENARIOS


def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for scen_data in SCENARIOS:
            existing = db.query(Scenario).filter(Scenario.id == scen_data["id"]).first()
            if not existing:
                new_scen = Scenario(
                    id=scen_data["id"],
                    name=scen_data["name"],
                    category=scen_data["category"],
                    description=scen_data["description"],
                    severity_default=scen_data["severity_default"],
                    cwe_id=scen_data["cwe_id"],
                    owasp_category=scen_data["owasp_category"],
                    target_endpoint_vulnerable=scen_data["target_endpoint_vulnerable"],
                    target_endpoint_remediated=scen_data["target_endpoint_remediated"],
                    remediation_guidance=scen_data["remediation_guidance"],
                    steps_definition=scen_data["steps"]
                )
                db.add(new_scen)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized and scenarios seeded successfully.")
