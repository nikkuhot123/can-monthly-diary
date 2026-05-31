import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from services.whatsapp_parser import parse_whatsapp_message

text = open("C:/Users/nikhi/Downloads/WhatsApp Chat with ZI Mumbai.txt", "r", encoding="utf-8", errors="ignore").read()
staff_no = "861198"
records = parse_whatsapp_message(text, staff_no)
print(f"Total records for {staff_no}: {len(records)}")
print()
for r in records:
    print(f"  Date: {r.get('duty_date')}, Leave: {r.get('is_leave')}, Branch: '{r.get('branch_name', '')[:30]}', Holiday: {r.get('is_holiday')}, Weekend: {r.get('is_weekend')}, Review: {r.get('needs_review')}, Note: {r.get('review_note', '')}")