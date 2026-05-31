import sys, os, bcrypt
sys.path.insert(0, os.path.dirname(__file__))
from database.db import SessionLocal, engine
from database import models

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

existing = db.query(models.User).filter(models.User.staff_no == "861198").first()
if existing:
    print(f"User already exists: {existing.name}")
else:
    user = models.User(
        staff_no="861198",
        name="NIKHILESH KUMAR",
        mobile="9199199936",
        designation="Senior Manager",
        designation_code="1301",
        dp_code="55265",
        section="ZI MUMBAI UNIT NASHIK",
        zone="ZI MUMBAI",
        basic_pay=105280.0,
        home_state="Maharashtra",
        city_category="B1",
        email="nikhilkumarnikhilesh@gmail.com",
        hashed_password=bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()
    print(f"Created: {user.name}")

db.close()
