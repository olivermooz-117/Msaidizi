from backend.app.extensions import db
from backend.app.models import MockOrder, MockPayment, Handoff, Conversation
from backend.app.services.retrieval import search_knowledge


def get_order_status(business_id: str, order_no: str = None, phone: str = None) -> dict:
    q = MockOrder.query.filter_by(business_id=business_id)
    if order_no:
        order = q.filter_by(order_no=order_no.strip().upper()).first()
    elif phone:
        # normalize phone a bit
        phone = "".join(c for c in phone if c.isdigit())
        order = q.filter(MockOrder.phone.contains(phone[-9:])).order_by(MockOrder.last_update.desc()).first()
    else:
        return {"found": False, "error": "Provide order_no or phone"}

    if not order:
        return {"found": False}

    return {
        "found": True,
        "order_no": order.order_no,
        "status": order.status,
        "items": order.items,
        "amount": order.amount,
        "last_update": order.last_update.isoformat(),
        "phone": order.phone,
    }


def check_mpesa_payment(business_id: str, transaction_code: str) -> dict:
    code = transaction_code.strip().upper()
    payment = MockPayment.query.filter_by(
        business_id=business_id,
        mpesa_code=code,
    ).first()

    if not payment:
        return {"found": False, "mpesa_code": code}

    return {
        "found": True,
        "mpesa_code": payment.mpesa_code,
        "amount": payment.amount,
        "status": payment.status,
        "phone": payment.phone,
        "matched_order_no": payment.matched_order_no,
        "paid_at": payment.paid_at.isoformat(),
    }


def escalate_to_human(conversation_id: str, reason: str, summary: str) -> dict:
    conv = db.session.get(Conversation, conversation_id)
    if not conv:
        return {"error": "conversation not found"}

    if conv.handoff:
        return {"handoff_id": conv.handoff.id, "status": conv.handoff.status}

    handoff = Handoff(
        conversation_id=conversation_id,
        reason=reason[:255],
        summary=summary,
        status="pending",
    )
    conv.status = "escalated"
    db.session.add(handoff)
    db.session.commit()
    return {"handoff_id": handoff.id, "status": "pending"}


# Tool registry used by the agent
TOOL_DEFINITIONS = [
    {
        "name": "search_knowledge",
        "description": "Search the business knowledge base for product, price, delivery, hours or policy information. Always use this before answering factual questions.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_order_status",
        "description": "Look up an order by order number or customer phone number.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_no": {"type": "string"},
                "phone": {"type": "string"},
            },
        },
    },
    {
        "name": "check_mpesa_payment",
        "description": "Check whether an M-Pesa transaction code was received by the business.",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_code": {"type": "string", "description": "The M-Pesa code e.g. QKJ4X7R2M1"}
            },
            "required": ["transaction_code"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": "Hand the conversation to a human agent. Use for refunds, complaints, low confidence, or when the customer asks for a person.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "summary": {"type": "string"},
            },
            "required": ["reason", "summary"],
        },
    },
]


def run_tool(name: str, args: dict, business_id: str, conversation_id: str) -> dict:
    if name == "search_knowledge":
        return {"results": search_knowledge(business_id, args.get("query", ""))}
    if name == "get_order_status":
        return get_order_status(business_id, args.get("order_no"), args.get("phone"))
    if name == "check_mpesa_payment":
        return check_mpesa_payment(business_id, args.get("transaction_code", ""))
    if name == "escalate_to_human":
        return escalate_to_human(conversation_id, args.get("reason", "unknown"), args.get("summary", ""))
    return {"error": f"Unknown tool {name}"}
