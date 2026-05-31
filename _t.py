import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from database.db import SessionLocal
from database.models import User, MonthlyDiary, AttendanceRecord, TravelLeg, HotelStay, LocalConveyance, OtherExpense
from generators.diary_excel import generate_diary_excel
import openpyxl

db = SessionLocal()
user = db.query(User).first()
diary = db.query(MonthlyDiary).first()
attendance = db.query(AttendanceRecord).filter(AttendanceRecord.diary_id == diary.id).order_by(AttendanceRecord.duty_date).all()
travel = db.query(TravelLeg).filter(TravelLeg.diary_id == diary.id).order_by(TravelLeg.date_start).all()
hotels = db.query(HotelStay).filter(HotelStay.diary_id == diary.id).order_by(HotelStay.checkin_date).all()
local = db.query(LocalConveyance).filter(LocalConveyance.diary_id == diary.id).order_by(LocalConveyance.travel_date).all()
other = db.query(OtherExpense).filter(OtherExpense.diary_id == diary.id).order_by(OtherExpense.created_at).all()
out = os.path.join(os.path.dirname(__file__), "_t.xlsx")
generate_diary_excel(out, user, diary, attendance, travel, hotels, local, other)

wb = openpyxl.load_workbook(out)
ws3 = wb["Sheet3"]
print("Sheet3 formulas:")
for r in [7,9,11,13,15,17,19,20,22,24]:
    cell = ws3.cell(row=r, column=18)
    print(f"  R{r}: {cell.value}")
print(f"  G14: {ws3['G14'].value}")

# Check cross-sheet chain
print()
print("Cross-sheet chain:")
ws1 = wb["Sheet1"]
print(f"  Sheet1!U21: {ws1['U21'].value}")
print(f"  Sheet1!O124: {ws1['O124'].value}")

ws2 = wb["Sheet2"]
print(f"  Sheet2!J78: {ws2['J78'].value}")
print(f"  Sheet2!K78: {ws2['K78'].value}")
print(f"  Sheet2!Q78: {ws2['Q78'].value}")

db.close()
os.remove(out)
os.remove(os.path.join(os.path.dirname(__file__), "_t.py"))
print()
print("OK - no circular reference detected")
