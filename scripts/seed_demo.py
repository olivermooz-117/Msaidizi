import sys, os, secrets
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from werkzeug.security import generate_password_hash
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Business, MockOrder, MockPayment
from backend.app.services.ingest import ingest_text

def utcnow():
    return datetime.now(timezone.utc)

def seed():
    app = create_app()
    with app.app_context():
        print("Seeding demo business...")
        # Clear previous
        for model in [MockPayment, MockOrder]:
            db.session.query(model).delete()
        # Keep documents if you want; for clean slate uncomment below
        # from backend.app.models import Chunk, Document
        # db.session.query(Chunk).delete()
        # db.session.query(Document).delete()
        # db.session.query(Business).delete()

        existing = Business.query.filter_by(owner_email="owner@nairobitheads.co.ke").first()
        if existing:
            business = existing
            print(f"Using existing business {business.name}")
        else:
            business = Business(
                name="Nairobi Threads",
                owner_email="owner@nairobitheads.co.ke",
                password_hash=generate_password_hash("demo1234"),
                widget_key=secrets.token_urlsafe(24),
            )
            db.session.add(business)
            db.session.commit()

        # Knowledge
        faq = """
Nairobi Threads – FAQ
Opening hours: Monday to Saturday 9:00 AM – 7:00 PM. Closed Sundays and public holidays.
Delivery: Nairobi 1–2 days (KES 300). Upcountry 3–5 days (KES 500–800). Free delivery above KES 5,000 inside Nairobi.
Returns: Unworn items within 7 days. Refunds in 5 business days. No returns on sale items.
Payment: M-Pesa Paybill 522522, Account = order number. Cash on delivery in Nairobi.
Contact: WhatsApp +254 712 345 678 or hello@nairobitheads.co.ke
"""
        prices = """
Price List (KES)
Women: Linen Midi Dress 3200, Oversized Cotton Shirt 2100, Wide Leg Trousers 2800, Knit Cardigan 2500, Ankara Maxi Skirt 2400
Men: Oxford Shirt 2300, Chino Trousers 2600, Heavyweight Hoodie 3100, Linen Shorts 1900
Accessories: Leather Belt 1200, Canvas Tote 1500, Beanie 800
"""
        ingest_text(business.id, "FAQ", faq)
        ingest_text(business.id, "Price List", prices)

        # Orders & payments
        orders = [
            ("NT-1001", "254712345678", "shipped", [{"name": "Linen Midi Dress (White)", "qty": 1, "price": 3200}], 3500, 1),
            ("NT-1002", "254722334455", "processing", [{"name": "Oversized Cotton Shirt", "qty": 2, "price": 2100}], 5700, 0),
            ("NT-1003", "254733221100", "delivered", [{"name": "Classic Oxford Shirt", "qty": 1, "price": 2300}], 2600, 4),
        ]
        for ono, phone, status, items, amount, days in orders:
            if not MockOrder.query.filter_by(business_id=business.id, order_no=ono).first():
                db.session.add(MockOrder(
                    business_id=business.id, order_no=ono, phone=phone, status=status,
                    items=items, amount=amount,
                    last_update=utcnow() - timedelta(days=days),
                ))

        payments = [
            ("QKJ4X7R2M1", "254712345678", 3500, "NT-1001", 30),
            ("SLM9P3K8N2", "254722334455", 5700, "NT-1002", 5),
            ("TGH2W5Y9Q4", "254733221100", 2600, "NT-1003", 96),
        ]
        for code, phone, amount, ono, hours in payments:
            if not MockPayment.query.filter_by(business_id=business.id, mpesa_code=code).first():
                db.session.add(MockPayment(
                    business_id=business.id, mpesa_code=code, phone=phone,
                    amount=amount, matched_order_no=ono,
                    paid_at=utcnow() - timedelta(hours=hours),
                ))

        db.session.commit()
        print("✅ Seeded")
        print(f"   Login: owner@nairobitheads.co.ke / demo1234")
        print(f"   Widget key: {business.widget_key}")
        print(f"   Try M-Pesa: QKJ4X7R2M1   Order: NT-1001")

if __name__ == "__main__":
    seed()
