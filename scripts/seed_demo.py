"""
Seed a demo clothing shop with knowledge, orders and M-Pesa payments.
Run from project root after migrations:
    python -m scripts.seed_demo
"""
import sys
import os
import secrets
from datetime import datetime, timedelta

# Make sure backend is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from werkzeug.security import generate_password_hash
from backend.app import create_app, db
from backend.app.models import (
    Business,
    Document,
    Chunk,
    MockOrder,
    MockPayment,
)


def seed():
    app = create_app()
    with app.app_context():
        # Clean previous demo (optional – comment out if you want to keep data)
        print("Clearing previous demo data...")
        db.session.query(MockPayment).delete()
        db.session.query(MockOrder).delete()
        db.session.query(Chunk).delete()
        db.session.query(Document).delete()
        db.session.query(Business).delete()
        db.session.commit()

        # 1. Demo business
        widget_key = secrets.token_urlsafe(24)
        business = Business(
            name="Nairobi Threads",
            owner_email="owner@nairobitheads.co.ke",
            password_hash=generate_password_hash("demo1234"),
            widget_key=widget_key,
        )
        db.session.add(business)
        db.session.flush()
        print(f"Created business: {business.name} (widget_key={widget_key})")

        # 2. Knowledge base (FAQ + price list as pasted text)
        faq_text = """
Nairobi Threads – Frequently Asked Questions

Opening hours: We are open Monday to Saturday 9:00 AM – 7:00 PM. Closed on Sundays and public holidays.

Delivery: We deliver within Nairobi in 1–2 business days (KES 300). Upcountry deliveries take 3–5 business days (KES 500–800 depending on location). Free delivery on orders above KES 5,000 inside Nairobi.

Returns & Refunds: You can return unworn items within 7 days of delivery. Refunds are processed within 5 business days after we receive the item. We do not accept returns on sale items.

Payment methods: We accept M-Pesa (Paybill 522522, Account: your order number) and cash on delivery for Nairobi orders.

Size guide: Our sizes run true to size. If you are between sizes we recommend sizing up. Full size chart is available on each product page.

Contact: WhatsApp +254 712 345 678 or email hello@nairobitheads.co.ke
"""

        price_list = """
Nairobi Threads – Price List (KES)

Women's Collection
- Linen Midi Dress (White/Beige/Black): 3,200
- Oversized Cotton Shirt: 2,100
- High-waist Wide Leg Trousers: 2,800
- Knit Cardigan: 2,500
- Ankara Print Maxi Skirt: 2,400

Men's Collection
- Classic Oxford Shirt: 2,300
- Chino Trousers: 2,600
- Heavyweight Hoodie: 3,100
- Linen Shorts: 1,900

Accessories
- Leather Belt: 1,200
- Canvas Tote Bag: 1,500
- Beanie: 800
"""

        doc_faq = Document(
            business_id=business.id,
            title="FAQ",
            source_type="paste",
        )
        doc_prices = Document(
            business_id=business.id,
            title="Price List",
            source_type="paste",
        )
        db.session.add_all([doc_faq, doc_prices])
        db.session.flush()

        # Simple chunking (we'll improve later)
        def simple_chunks(text: str, doc_id: str, max_len: int = 400):
            paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
            chunks = []
            pos = 0
            for para in paragraphs:
                if len(para) <= max_len:
                    chunks.append(Chunk(document_id=doc_id, text=para, position=pos))
                    pos += 1
                else:
                    # Split long paragraphs
                    words = para.split()
                    current = []
                    for w in words:
                        current.append(w)
                        if len(" ".join(current)) > max_len:
                            chunks.append(Chunk(document_id=doc_id, text=" ".join(current[:-1]), position=pos))
                            pos += 1
                            current = [w]
                    if current:
                        chunks.append(Chunk(document_id=doc_id, text=" ".join(current), position=pos))
                        pos += 1
            return chunks

        chunks = simple_chunks(faq_text, doc_faq.id) + simple_chunks(price_list, doc_prices.id)
        db.session.add_all(chunks)
        print(f"Created {len(chunks)} knowledge chunks (embeddings will be added later)")

        # 3. Mock orders
        orders_data = [
            {
                "order_no": "NT-1001",
                "phone": "254712345678",
                "status": "shipped",
                "items": [{"name": "Linen Midi Dress (White)", "qty": 1, "price": 3200}],
                "amount": 3500,
                "days_ago": 1,
            },
            {
                "order_no": "NT-1002",
                "phone": "254722334455",
                "status": "processing",
                "items": [
                    {"name": "Oversized Cotton Shirt", "qty": 2, "price": 2100},
                    {"name": "Canvas Tote Bag", "qty": 1, "price": 1500},
                ],
                "amount": 5700,
                "days_ago": 0,
            },
            {
                "order_no": "NT-1003",
                "phone": "254733221100",
                "status": "delivered",
                "items": [{"name": "Classic Oxford Shirt", "qty": 1, "price": 2300}],
                "amount": 2600,
                "days_ago": 4,
            },
            {
                "order_no": "NT-1004",
                "phone": "254711998877",
                "status": "pending",
                "items": [{"name": "Ankara Print Maxi Skirt", "qty": 1, "price": 2400}],
                "amount": 2700,
                "days_ago": 0,
            },
        ]

        for o in orders_data:
            order = MockOrder(
                business_id=business.id,
                order_no=o["order_no"],
                phone=o["phone"],
                status=o["status"],
                items=o["items"],
                amount=o["amount"],
                last_update=datetime.utcnow() - timedelta(days=o["days_ago"]),
            )
            db.session.add(order)

        # 4. Mock M-Pesa payments
        payments_data = [
            {"mpesa_code": "QKJ4X7R2M1", "phone": "254712345678", "amount": 3500, "matched_order_no": "NT-1001", "hours_ago": 30},
            {"mpesa_code": "SLM9P3K8N2", "phone": "254722334455", "amount": 5700, "matched_order_no": "NT-1002", "hours_ago": 5},
            {"mpesa_code": "TGH2W5Y9Q4", "phone": "254733221100", "amount": 2600, "matched_order_no": "NT-1003", "hours_ago": 96},
            {"mpesa_code": "ABC1D2E3F4", "phone": "254700112233", "amount": 1500, "matched_order_no": None, "hours_ago": 2},  # unmatched
        ]

        for p in payments_data:
            payment = MockPayment(
                business_id=business.id,
                mpesa_code=p["mpesa_code"],
                phone=p["phone"],
                amount=p["amount"],
                status="completed",
                matched_order_no=p["matched_order_no"],
                paid_at=datetime.utcnow() - timedelta(hours=p["hours_ago"]),
            )
            db.session.add(payment)

        db.session.commit()
        print("\n✅ Demo data seeded successfully!")
        print(f"   Login: owner@nairobitheads.co.ke / demo1234")
        print(f"   Widget key: {widget_key}")
        print(f"   Sample M-Pesa codes: QKJ4X7R2M1, SLM9P3K8N2, TGH2W5Y9Q4")
        print(f"   Sample order numbers: NT-1001, NT-1002, NT-1003")


if __name__ == "__main__":
    seed()
