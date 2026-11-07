"""
Create a demo Nairobi Threads business and sample data.

Run from the repository root:
    python -m scripts.seed_demo

This script is intentionally non-destructive. If the demo business
already exists, it exits without deleting or replacing existing data.
"""

import os
import secrets
import sys
from datetime import datetime, timedelta

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

from werkzeug.security import generate_password_hash

from backend.app import create_app, db
from backend.app.models import (
    Business,
    Chunk,
    Document,
    MockOrder,
    MockPayment,
)
from backend.app.api.knowledge import split_text_into_chunks


def seed():
    app = create_app()

    with app.app_context():
        email = "owner@nairobitheads.co.ke"

        existing = db.session.query(Business).filter_by(
            owner_email=email
        ).first()

        if existing:
            print("Demo business already exists. Nothing was deleted.")
            print(f"Business: {existing.name}")
            print(f"Email: {existing.owner_email}")
            return

        business = Business(
            name="Nairobi Threads",
            owner_email=email,
            password_hash=generate_password_hash("demo1234"),
            widget_key=secrets.token_urlsafe(32),
        )

        db.session.add(business)
        db.session.flush()

        faq_text = """
Nairobi Threads - Frequently Asked Questions

Opening hours: Monday to Saturday, 9:00 AM to 7:00 PM.
Closed on Sundays and public holidays.

Delivery: Nairobi deliveries take 1-2 business days and cost KES 300.
Upcountry deliveries take 3-5 business days and cost KES 500-800.
Free delivery applies to Nairobi orders above KES 5,000.

Returns: Unworn items can be returned within 7 days of delivery.
Refunds are processed within 5 business days after receiving the item.
Sale items cannot be returned.

Payments: We accept M-Pesa Paybill 522522.
Use your order number as the account reference.
Cash on delivery is available for Nairobi orders.

Contact: WhatsApp +254 712 345 678.
Email: hello@nairobitheads.co.ke.
"""

        price_text = """
Nairobi Threads Price List - KES

Women's Collection:
Linen Midi Dress: 3200
Oversized Cotton Shirt: 2100
High-waist Wide Leg Trousers: 2800
Knit Cardigan: 2500
Ankara Print Maxi Skirt: 2400

Men's Collection:
Classic Oxford Shirt: 2300
Chino Trousers: 2600
Heavyweight Hoodie: 3100
Linen Shorts: 1900

Accessories:
Leather Belt: 1200
Canvas Tote Bag: 1500
Beanie: 800
"""

        documents = [
            Document(
                business_id=business.id,
                title="Frequently Asked Questions",
                source_type="paste",
            ),
            Document(
                business_id=business.id,
                title="Price List",
                source_type="paste",
            ),
        ]

        db.session.add_all(documents)
        db.session.flush()

        all_chunks = []

        for document, content in zip(
            documents,
            [faq_text, price_text],
        ):
            for position, chunk_text in split_text_into_chunks(content):
                all_chunks.append(
                    Chunk(
                        document_id=document.id,
                        text=chunk_text,
                        position=position,
                    )
                )

        db.session.add_all(all_chunks)

        orders = [
            MockOrder(
                business_id=business.id,
                order_no="NT-1001",
                phone="254712345678",
                status="shipped",
                items=[
                    {
                        "name": "Linen Midi Dress (White)",
                        "qty": 1,
                        "price": 3200,
                    }
                ],
                amount=3500,
                last_update=datetime.utcnow() - timedelta(days=1),
            ),
            MockOrder(
                business_id=business.id,
                order_no="NT-1002",
                phone="254722334455",
                status="processing",
                items=[
                    {
                        "name": "Oversized Cotton Shirt",
                        "qty": 2,
                        "price": 2100,
                    },
                    {
                        "name": "Canvas Tote Bag",
                        "qty": 1,
                        "price": 1500,
                    },
                ],
                amount=5700,
                last_update=datetime.utcnow(),
            ),
            MockOrder(
                business_id=business.id,
                order_no="NT-1003",
                phone="254733221100",
                status="delivered",
                items=[
                    {
                        "name": "Classic Oxford Shirt",
                        "qty": 1,
                        "price": 2300,
                    }
                ],
                amount=2600,
                last_update=datetime.utcnow() - timedelta(days=4),
            ),
        ]

        payments = [
            MockPayment(
                business_id=business.id,
                mpesa_code="QKJ4X7R2M1",
                phone="254712345678",
                amount=3500,
                status="completed",
                matched_order_no="NT-1001",
                paid_at=datetime.utcnow() - timedelta(hours=30),
            ),
            MockPayment(
                business_id=business.id,
                mpesa_code="SLM9P3K8N2",
                phone="254722334455",
                amount=5700,
                status="completed",
                matched_order_no="NT-1002",
                paid_at=datetime.utcnow() - timedelta(hours=5),
            ),
            MockPayment(
                business_id=business.id,
                mpesa_code="TGH2W5Y9Q4",
                phone="254733221100",
                amount=2600,
                status="completed",
                matched_order_no="NT-1003",
                paid_at=datetime.utcnow() - timedelta(hours=96),
            ),
        ]

        db.session.add_all(orders + payments)
        db.session.commit()

        print("Demo data created successfully.")
        print(f"Business: {business.name}")
        print(f"Login email: {email}")
        print("Demo password: demo1234")
        print("Change the demo password before any public deployment.")
        print(f"Widget key: {business.widget_key}")
        print("Sample order: NT-1001")
        print("Sample M-Pesa code: QKJ4X7R2M1")


if __name__ == "__main__":
    seed()
