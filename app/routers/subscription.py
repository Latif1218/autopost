# app/routers/subscription.py

import stripe
import logging
from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..models.users_models import User, UserPlan
from ..models.subscription_model import Subscription, PlanType, SubscriptionStatus
from ..schemas.subscription_schema import (
    CreateCheckoutRequest,
    CheckoutResponse,
    SubscriptionStatusResponse,
)
from ..database import get_db
from ..authentication.users_oauth import get_current_user
from ..supabase_client import supabase_admin
from ..utils.mailerlite import add_to_ottomax_customers
from ..config import (
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    STRIPE_SUCCESS_URL,
    STRIPE_CANCEL_URL,
    PRICE_IDS,
)
import httpx


logger = logging.getLogger(__name__)
stripe.api_key = STRIPE_SECRET_KEY


router = APIRouter(
    prefix="/subscription",
    tags=["Subscription"]
)


# ──────────────────────────────────────────────
# Helper — n8n trigger (non-critical)
# ──────────────────────────────────────────────
async def trigger_n8n_welcome(
    email: str,
    plan: str,
    full_name: str = ""
) -> None:
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:5678/webhook/welcome",
                json={
                    "email": email,
                    "plan": plan,
                    "full_name": full_name
                },
                timeout=5.0
            )
        logger.info(f"n8n welcome triggered: {email}")
    except Exception as e:
        logger.warning(f"n8n trigger failed (non-critical): {e}")


# ──────────────────────────────────────────────
# GET /subscription/config
# ──────────────────────────────────────────────
@router.get("/config")
async def get_payment_config():
    return {
        "plans": {
            "essential": {
                "price": 0.00,
                "currency": "USD",
                "note": "Free plan",
                "interval": None
            },
            "starter": {
                "price": 14.99,
                "currency": "USD",
                "price_id": PRICE_IDS.get("starter"),
                "interval": "monthly"
            },
            "pro": {
                "price": 29.99,
                "currency": "USD",
                "price_id": PRICE_IDS.get("pro"),
                "interval": "monthly"
            },
            "premium": {
                "price": 49.99,
                "currency": "USD",
                "price_id": PRICE_IDS.get("premium"),
                "interval": "one_time"
            }
        }
    }


# ──────────────────────────────────────────────
# GET /subscription/status
# ──────────────────────────────────────────────
@router.get("/status", response_model=SubscriptionStatusResponse)
def get_subscription_status(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()

    if not sub:
        return SubscriptionStatusResponse(
            plan="essential",
            status="inactive",
            current_period_end=None,
            cancel_at_period_end=False,
            message="You are on the free plan."
        )

    return SubscriptionStatusResponse(
        plan=sub.plan_type,
        status=sub.status,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=sub.cancel_at_period_end,
        message="Active subscription."
    )


# ──────────────────────────────────────────────
# POST /subscription/checkout
# ──────────────────────────────────────────────
@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    req: CreateCheckoutRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    plan = req.plan.lower()

    price_id = PRICE_IDS.get(plan)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Price ID not configured for plan: {plan}"
        )

    if plan == "premium" and not req.is_one_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Premium plan is one-time payment only"
        )

    mode = "payment" if plan == "premium" else "subscription"

    try:
        session = stripe.checkout.Session.create(
            mode=mode,
            payment_method_types=["card"],
            customer_email=current_user.email,
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={
                "user_id": str(current_user.id),
                "email": current_user.email,
                "plan": plan,
                "is_one_time": str(req.is_one_time),
                "full_name": current_user.full_name or ""
            },
            success_url=STRIPE_SUCCESS_URL,
            cancel_url=STRIPE_CANCEL_URL,
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment setup failed: {str(e)}"
        )

    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()

    if not sub:
        sub = Subscription(
            user_id=current_user.id,
            plan_type=PlanType(plan),
            price_id=price_id,
            status=SubscriptionStatus.INCOMPLETE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(sub)
    else:
        sub.plan_type = PlanType(plan)
        sub.price_id = price_id
        sub.status = SubscriptionStatus.INCOMPLETE
        sub.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(sub)

    logger.info(f"Checkout created | User: {current_user.id} | Plan: {plan} | Mode: {mode}")

    return CheckoutResponse(
        session_id=session.id,
        url=session.url,
        plan=plan,
        is_one_time=req.is_one_time
    )


# ──────────────────────────────────────────────
# POST /subscription/webhook
# ──────────────────────────────────────────────
@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Annotated[Session, Depends(get_db)]
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured"
        )

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid Stripe signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")

    event_type = event["type"]
    logger.info(f"Stripe event: {event_type}")

    # ── checkout.session.completed ──
    if event_type == "checkout.session.completed":
        session_data = event["data"]["object"]

        user_id = session_data["metadata"].get("user_id")
        plan = session_data["metadata"].get("plan")
        full_name = session_data["metadata"].get("full_name", "")
        customer_id = session_data.get("customer")
        subscription_id = session_data.get("subscription")
        user_email = session_data.get("customer_email")

        if not user_id or not plan:
            logger.warning("Webhook missing metadata")
            return {"status": "ignored"}

        # ✅ Bug fix: UUID type cast করো
        from uuid import UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            logger.error(f"Invalid user_id format: {user_id}")
            return {"status": "invalid user_id"}

        local_user = db.query(User).filter(
            User.id == user_uuid
        ).first()

        if not local_user:
            logger.error(f"User not found: {user_id}")
            return {"status": "user not found"}

        # 1. User plan update
        local_user.plan = UserPlan(plan)
        local_user.updated_at = datetime.utcnow()

        # 2. Subscription update
        sub = db.query(Subscription).filter(
            Subscription.user_id == local_user.id
        ).first()

        if not sub:
            sub = Subscription(
                user_id=local_user.id,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
                plan_type=PlanType(plan),
                status=SubscriptionStatus.ACTIVE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(sub)
        else:
            sub.stripe_customer_id = customer_id
            sub.stripe_subscription_id = subscription_id
            sub.plan_type = PlanType(plan)
            sub.status = SubscriptionStatus.ACTIVE
            sub.updated_at = datetime.utcnow()

        # 3. Supabase metadata update
        # ✅ supabase_admin সরাসরি use করছি — client already initialized
        if local_user.supabase_uid:
            try:
                supabase_admin.auth.admin.update_user_by_id(
                    local_user.supabase_uid,
                    {"user_metadata": {"plan": plan}}
                )
                logger.info(f"Supabase metadata updated: {local_user.email}")
            except Exception as e:
                logger.warning(f"Supabase metadata update failed (non-critical): {e}")

        db.commit()
        db.refresh(sub)

        final_email = user_email or local_user.email
        final_name = full_name or local_user.full_name or ""

        # 4. MailerLite — group এ add করো
        mailerlite_ok = await add_to_ottomax_customers(
            email=final_email,
            full_name=final_name,
            plan=plan
        )
        if not mailerlite_ok:
            logger.warning(f"MailerLite add failed: {final_email}")

        # 5. n8n trigger
        await trigger_n8n_welcome(
            email=final_email,
            plan=plan,
            full_name=final_name
        )

        logger.info(f"✅ Payment complete | {final_email} | Plan: {plan}")

    # ── customer.subscription.deleted ──
    elif event_type == "customer.subscription.deleted":
        sub_id = event["data"]["object"]["id"]

        sub = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == sub_id
        ).first()

        if sub:
            sub.status = SubscriptionStatus.CANCELED
            sub.updated_at = datetime.utcnow()

            user = db.query(User).filter(User.id == sub.user_id).first()
            if user:
                user.plan = UserPlan.ESSENTIAL
                user.updated_at = datetime.utcnow()

                if user.supabase_uid:
                    try:
                        supabase_admin.auth.admin.update_user_by_id(
                            user.supabase_uid,
                            {"user_metadata": {"plan": "essential"}}
                        )
                    except Exception as e:
                        logger.warning(f"Supabase downgrade failed: {e}")

            db.commit()
            logger.info(f"Subscription canceled: {sub_id}")

    # ── invoice.payment_failed ──
    elif event_type == "invoice.payment_failed":
        sub_id = event["data"]["object"].get("subscription")

        sub = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == sub_id
        ).first()

        if sub:
            sub.status = SubscriptionStatus.PAST_DUE
            sub.updated_at = datetime.utcnow()
            db.commit()
            logger.warning(f"Payment failed — past_due: {sub_id}")

    # ── invoice.payment_succeeded ──
    elif event_type == "invoice.payment_succeeded":
        sub_id = event["data"]["object"].get("subscription")

        sub = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == sub_id
        ).first()

        if sub:
            sub.status = SubscriptionStatus.ACTIVE
            sub.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Subscription renewed: {sub_id}")

    return {"status": "success"}

