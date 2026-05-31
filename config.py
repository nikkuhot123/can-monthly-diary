import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import ClassVar

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./audit_diary.db"
    UPLOAD_DIR: str = "uploads"
    APP_NAME: str = "Audit Diary System"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 9931
    OCR_TESSERACT_CMD: str = ""

    CANARA_BANK_GSTIN: ClassVar[dict] = {
        "Jammu & Kashmir":           "01AAACC6106G1ZF",
        "Himachal Pradesh":          "02AAACC6106G2ZC",
        "Punjab":                    "03AAACC6106G1DK",
        "Chandigarh":                "04AAACC6106G2Z8",
        "Uttarakhand":               "05AAACC6106G3Z5",
        "Haryana":                   "06AAACC6106G2Z4",
        "Delhi":                     "07AAACC6106G4Z0",
        "Rajasthan":                 "08AAACC6106G2Z0",
        "Uttar Pradesh":             "09AAACC6106G3ZX",
        "Bihar":                     "10AAACC6106G2ZF",
        "Sikkim":                    "11AAACC6106G1DN",
        "Arunachal Pradesh":         "12AAACC6106G2ZB",
        "Nagaland":                  "13AAACC6106G2Z9",
        "Manipur":                   "14AAACC6106G2Z7",
        "Mizoram":                   "15AAACC6106G2Z5",
        "Tripura":                   "16AAACC6106G1DD",
        "Meghalaya":                 "17AAACC6106G2Z1",
        "Assam":                     "18AAACC6106G2ZZ",
        "West Bengal":               "19AAACC6106G3ZW",
        "Jharkhand":                 "20AAACC6106G2ZE",
        "Odisha":                    "21AAACC6106G3ZB",
        "Chhattisgarh":              "22AAACC6106G3Z9",
        "Madhya Pradesh":            "23AAACC6106G2Z8",
        "Gujarat":                   "24AAACC6106G2Z6",
        "Daman & Diu":               "25AAACC6106G2Z4",
        "Dadra & Nagar Haveli":      "26AAACC6106G2Z2",
        "Maharashtra":               "27AAACC6106G4ZY",
        "Karnataka":                 "29AAACC6106G1ZX",
        "Goa":                       "30AAACC6106G2ZD",
        "Lakshadweep":               "31AAACC6106G2ZB",
        "Kerala":                    "32AAACC6106G3Z8",
        "Tamil Nadu":                "33AAACC6106G5Z4",
        "Puducherry":                "34AAACC6106G2Z5",
        "Andaman & Nicobar Islands": "35AAACC6106G1Z4",
        "Telangana":                 "36AAACC6106G3Z0",
        "Andhra Pradesh":            "37AAACC6106G2ZZ",
    }

    GST_RATES: ClassVar[dict] = {
        "Airlines": 5, "Train": 0, "Bus": 0,
        "Taxi": 5, "Auto": 0, "Own Vehicle": 0, "Other": 0,
    }

    HOTEL_GST_RATES: ClassVar[dict] = {
        "Budget": 0, "ThreeStar": 12, "FiveStar": 18,
    }

    HA_FULL_DAY: ClassVar[dict] = {
        "A1": 1500, "A": 1350, "B1": 1200,
        "B": 1050, "C": 900, "OTHER": 750,
    }

    HA_CITY_OVERRIDE: ClassVar[dict] = {
        "NASHIK": 1800,
    }

    CITY_CATEGORY: ClassVar[dict] = {
        "MUMBAI": "A1", "DELHI": "A1", "CHENNAI": "A1",
        "KOLKATA": "A1", "BANGALORE": "A1", "BENGALURU": "A1",
        "HYDERABAD": "A1", "PUNE": "A", "AHMEDABAD": "A",
        "NAGPUR": "B1", "NASHIK": "B1", "AURANGABAD": "B1",
        "BHOPAL": "B1", "INDORE": "B1", "PATNA": "B1",
        "AHMADNAGAR": "B", "AHMEDNAGAR": "B", "BHUSAWAL": "C", "JALGAON": "C",
    }

    STATE_CODES: ClassVar[dict] = {
        "01": "Jammu & Kashmir", "02": "Himachal Pradesh",
        "03": "Punjab", "04": "Chandigarh", "05": "Uttarakhand",
        "06": "Haryana", "07": "Delhi", "08": "Rajasthan",
        "09": "Uttar Pradesh", "10": "Bihar", "11": "Sikkim",
        "12": "Arunachal Pradesh", "13": "Nagaland", "14": "Manipur",
        "15": "Mizoram", "16": "Tripura", "17": "Meghalaya",
        "18": "Assam", "19": "West Bengal", "20": "Jharkhand",
        "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh",
        "24": "Gujarat", "25": "Daman & Diu", "26": "Dadra & Nagar Haveli",
        "27": "Maharashtra", "29": "Karnataka", "30": "Goa",
        "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu",
        "34": "Puducherry", "35": "Andaman & Nicobar Islands",
        "36": "Telangana", "37": "Andhra Pradesh",
    }

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()


def get_bank_gstin(state: str) -> str:
    return settings.CANARA_BANK_GSTIN.get(state, "")


def get_state_from_gstin(gstin: str) -> str:
    if gstin and len(gstin) >= 2:
        return settings.STATE_CODES.get(gstin[:2], "Unknown")
    return "Unknown"


def get_ha_rate(city: str) -> float:
    city_key = city.upper().strip()
    if city_key in settings.HA_CITY_OVERRIDE:
        return settings.HA_CITY_OVERRIDE[city_key]
    cat = settings.CITY_CATEGORY.get(city_key, "OTHER")
    return settings.HA_FULL_DAY.get(cat, 750)


FIREBASE = {
    "api_key": os.getenv("FIREBASE_API_KEY", ""),
    "auth_domain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
    "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
    "storage_bucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
    "messaging_sender_id": os.getenv("FIREBASE_MSG_SENDER_ID", ""),
    "app_id": os.getenv("FIREBASE_APP_ID", ""),
    "service_account_path": "firebase-service-account.json",
}
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "admin@gmail.com").split(",")
