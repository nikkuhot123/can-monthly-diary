"""Seed all RBI bank holidays for all 28 states + 8 UTs for 2025-2026"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from datetime import date
from database.db import SessionLocal, engine
from database import models

# RBI state/city -> our state name mapping
CITY_TO_STATE = {
    "Agartala":"Tripura","Ahmedabad":"Gujarat","Aizawl":"Mizoram",
    "Belapur":"Maharashtra","Bengaluru":"Karnataka","Bhopal":"Madhya Pradesh",
    "Bhubaneswar":"Odisha","Chandigarh":"Chandigarh","Chennai":"Tamil Nadu",
    "Dehradun":"Uttarakhand","Gangtok":"Sikkim","Guwahati":"Assam",
    "Hyderabad":"Telangana","Imphal":"Manipur","Itanagar":"Arunachal Pradesh",
    "Jaipur":"Rajasthan","Jammu":"Jammu and Kashmir","Kanpur":"Uttar Pradesh",
    "Kochi":"Kerala","Kohima":"Nagaland","Kolkata":"West Bengal",
    "Lucknow":"Uttar Pradesh","Mumbai":"Maharashtra","Nagpur":"Maharashtra",
    "New Delhi":"Delhi","Panaji":"Goa","Patna":"Bihar","Raipur":"Chhattisgarh",
    "Ranchi":"Jharkhand","Shillong":"Meghalaya","Shimla":"Himachal Pradesh",
    "Srinagar":"Jammu and Kashmir","Thiruvananthapuram":"Kerala",
    "Vijayawada":"Andhra Pradesh",
    "Across India":"ALL",
}

ALL_STATES = sorted(set(v for v in CITY_TO_STATE.values() if v != "ALL") | {
    "Delhi","Jammu and Kashmir","Ladakh","Puducherry",
    "Andaman and Nicobar","Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu","Lakshadweep"
})

def expand_states(cities_str: str) -> list[str]:
    if cities_str == "Across India":
        return ALL_STATES
    cities = [c.strip() for c in cities_str.replace("  "," ").split(",")]
    states = set()
    for c in cities:
        mapped = CITY_TO_STATE.get(c)
        if mapped:
            states.add(mapped)
        elif c:
            states.add(c)
    return sorted(states)

# Format: (year, month, day, occasion, cities_str)
HOLIDAY_DATA_2026 = [
    (2026,1,1,"New Year's Day","Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Rajasthan, Sikkim, Tamil Nadu, Telangana"),
    (2026,1,2,"New Year Holiday","Mizoram"),
    (2026,1,3,"Hazrat Ali Jayanti","Uttar Pradesh"),
    (2026,1,12,"Swami Vivekananda Jayanti","West Bengal"),
    (2026,1,14,"Makara Sankranti","Arunachal Pradesh, Gujarat, Karnataka, Odisha, Sikkim"),
    (2026,1,14,"Pongal","Andhra Pradesh, Tamil Nadu, Telangana"),
    (2026,1,15,"Thiruvalluvar Day","Tamil Nadu"),
    (2026,1,23,"Vasant Panchami","Haryana, Odisha, Punjab, Tripura, West Bengal"),
    (2026,1,26,"Republic Day","Across India"),
    (2026,2,1,"Guru Ravidas Jayanti","Chhattisgarh, Haryana, Himachal Pradesh, Madhya Pradesh, Punjab"),
    (2026,2,15,"Maha Shivaratri","Andhra Pradesh, Chhattisgarh, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Karnataka, Madhya Pradesh, Maharashtra, Odisha, Punjab, Rajasthan, Telangana, Tripura, Uttarakhand, Uttar Pradesh"),
    (2026,2,18,"Losar","Sikkim"),
    (2026,2,19,"Chhatrapati Shivaji Maharaj Jayanti","Maharashtra"),
    (2026,2,20,"State Day","Mizoram, Arunachal Pradesh"),
    (2026,3,3,"Holi","Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Madhya Pradesh, Maharashtra, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Telangana, Tripura, Uttarakhand, Uttar Pradesh"),
    (2026,3,20,"Ugadi","Andhra Pradesh, Goa, Gujarat, Karnataka, Rajasthan, Telangana"),
    (2026,3,21,"Idul Fitr","Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, Himachal Pradesh, Madhya Pradesh, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Tamil Nadu, Tripura, Uttarakhand, Uttar Pradesh, West Bengal"),
    (2026,3,21,"Sarhul","Jharkhand"),
    (2026,3,22,"Bihar Day","Bihar"),
    (2026,3,27,"Ram Navami","Andhra Pradesh, Bihar, Chhattisgarh, Gujarat, Haryana, Himachal Pradesh, Madhya Pradesh, Maharashtra, Odisha, Punjab, Rajasthan, Sikkim, Tripura, Telangana, Uttarakhand, Uttar Pradesh"),
    (2026,3,31,"Mahavir Jayanti","Chhattisgarh, Gujarat, Haryana, Jharkhand, Karnataka, Madhya Pradesh, Maharashtra, Mizoram, Punjab, Rajasthan, Tamil Nadu, Tripura, Uttar Pradesh"),
    (2026,4,3,"Good Friday","Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Jharkhand, Karnataka, Madhya Pradesh, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttarakhand, Uttar Pradesh, West Bengal"),
    (2026,4,14,"Dr Ambedkar Jayanti","Andhra Pradesh, Bihar, Chhattisgarh, Goa, Gujarat, Jharkhand, Maharashtra, Haryana, Himachal Pradesh, Karnataka, Madhya Pradesh, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Uttarakhand, Uttar Pradesh"),
    (2026,4,14,"Bohag Bihu","Assam, Arunachal Pradesh"),
    (2026,4,15,"Bengali New Year","West Bengal"),
    (2026,4,15,"Himachal Day","Himachal Pradesh"),
    (2026,4,19,"Maharshi Parasuram Jayanti","Chhattisgarh, Gujarat, Haryana, Himachal Pradesh, Madhya Pradesh, Rajasthan"),
    (2026,4,20,"Basava Jayanti","Karnataka"),
    (2026,5,1,"Buddha Purnima / Maharashtra Day","Arunachal Pradesh, Chhattisgarh, Himachal Pradesh, Jharkhand, Madhya Pradesh, Maharashtra, Mizoram, Uttarakhand, Uttar Pradesh, Assam, Bihar, Goa, Karnataka, Manipur, Tamil Nadu, Telangana, Tripura, West Bengal"),
    (2026,5,27,"Bakrid / Eid al Adha","Andhra Pradesh, Arunachal Pradesh, Bihar, Chhattisgarh, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Karnataka, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura"),
    (2026,6,17,"Maharana Pratap Jayanti","Haryana, Himachal Pradesh, Rajasthan"),
    (2026,6,26,"Muharram","Andhra Pradesh, Bihar, Chhattisgarh, Gujarat, Himachal Pradesh, Jharkhand, Karnataka, Madhya Pradesh, Maharashtra, Mizoram, Odisha, Rajasthan, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, Uttarakhand"),
    (2026,6,29,"Sant Guru Kabir Jayanti","Haryana, Himachal Pradesh, Punjab, Tripura"),
    (2026,7,16,"Ratha Yatra","Manipur, Odisha"),
    (2026,8,15,"Independence Day","Across India"),
    (2026,8,16,"Parsi New Year","Maharashtra"),
    (2026,8,25,"Eid e Milad","Andhra Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Karnataka, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Uttar Pradesh, Uttarakhand, West Bengal, Delhi, Kerala"),
    (2026,8,27,"Thiruvonam","Kerala"),
    (2026,8,28,"Raksha Bandhan","Uttarakhand, Uttar Pradesh, Rajasthan, Madhya Pradesh, Haryana"),
    (2026,9,4,"Janmashtami","Andhra Pradesh, Bihar, Chhattisgarh, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Madhya Pradesh, Manipur, Meghalaya, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttarakhand, Uttar Pradesh"),
    (2026,9,15,"Ganesh Chaturthi","Andhra Pradesh, Goa, Gujarat, Karnataka, Maharashtra, Odisha, Tamil Nadu, Telangana"),
    (2026,9,21,"Ramdev Jayanti","Rajasthan"),
    (2026,10,2,"Gandhi Jayanti","Across India"),
    (2026,10,11,"Maharaja Agrasen Jayanti","Haryana, Rajasthan"),
    (2026,10,18,"Maha Saptami","Assam, Odisha, Sikkim, West Bengal"),
    (2026,10,19,"Maha Ashtami","Andhra Pradesh, Assam, Jharkhand, Manipur, Odisha, Rajasthan, Sikkim, Telangana, West Bengal"),
    (2026,10,20,"Maha Navami","Arunachal Pradesh, Assam, Bihar, Jharkhand, Karnataka, Meghalaya, Nagaland, Odisha, Sikkim, Tamil Nadu, Tripura, Uttar Pradesh, West Bengal"),
    (2026,10,21,"Vijaya Dashami","Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Karnataka, Madhya Pradesh, Maharashtra, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttarakhand, Uttar Pradesh, West Bengal"),
    (2026,10,26,"Maharishi Valmiki Jayanti","Chhattisgarh, Haryana, Himachal Pradesh, Karnataka, Madhya Pradesh, Punjab, Tripura"),
    (2026,11,8,"Diwali","Across India"),
    (2026,11,9,"Deepavali Holiday","Haryana, Karnataka, Maharashtra, Rajasthan, Uttarakhand, Uttar Pradesh"),
    (2026,11,11,"Bhai Dooj","Gujarat, Rajasthan, Sikkim, Uttarakhand, Uttar Pradesh"),
    (2026,11,15,"Chhath Puja","Jharkhand, Bihar"),
    (2026,11,24,"Guru Nanak Jayanti","Arunachal Pradesh, Chhattisgarh, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Madhya Pradesh, Maharashtra, Mizoram, Nagaland, Punjab, Rajasthan, Telangana, Uttarakhand, Uttar Pradesh, West Bengal"),
    (2026,11,27,"Kanakadasa Jayanti","Karnataka"),
    (2026,12,25,"Christmas Day","Across India"),
    (2026,12,31,"New Year's Eve","Mizoram"),
]

HOLIDAY_DATA_2025 = [
    (2025,1,26,"Republic Day","Across India"),
    (2025,2,19,"Chhatrapati Shivaji Maharaj Jayanti","Maharashtra"),
    (2025,2,26,"Maha Shivaratri","Maharashtra"),
    (2025,3,14,"Holi","Across India"),
    (2025,3,31,"Idul Fitr","Across India"),
    (2025,4,10,"Mahavir Jayanti","Across India"),
    (2025,4,14,"Dr Ambedkar Jayanti","Across India"),
    (2025,4,18,"Good Friday","Across India"),
    (2025,5,1,"Maharashtra Day","Maharashtra"),
    (2025,6,7,"Idul Zuha (Bakrid)","Across India"),
    (2025,7,6,"Muharram","Across India"),
    (2025,8,15,"Independence Day","Across India"),
    (2025,8,16,"Parsi New Year","Maharashtra"),
    (2025,8,27,"Ganesh Chaturthi","Across India"),
    (2025,9,5,"Milad-un-Nabi","Across India"),
    (2025,10,1,"Gandhi Jayanti (observed)","Across India"),
    (2025,10,2,"Gandhi Jayanti","Across India"),
    (2025,10,7,"Dussehra","Across India"),
    (2025,10,20,"Diwali","Across India"),
    (2025,10,21,"Diwali (Balipratipada)","Across India"),
    (2025,11,5,"Guru Nanak Jayanti","Across India"),
    (2025,12,25,"Christmas","Across India"),
]

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()
count = 0

for year_data in [HOLIDAY_DATA_2025, HOLIDAY_DATA_2026]:
    for y,m,d,occasion,cities_str in year_data:
        hdate = date(y,m,d)
        states = expand_states(cities_str)
        for state in states:
            existing = db.query(models.Holiday).filter(
                models.Holiday.holiday_date == hdate,
                models.Holiday.state == state,
            ).first()
            if existing:
                continue
            htype = "public" if cities_str == "Across India" else "bank"
            db.add(models.Holiday(
                holiday_date=hdate, state=state,
                description=occasion, holiday_type=htype,
            ))
            count += 1
            if count % 50 == 0:
                db.flush()

db.commit()
db.close()
print(f"Seeded {count} new holidays across {len(HOLIDAY_DATA_2025) + len(HOLIDAY_DATA_2026)} entries")
