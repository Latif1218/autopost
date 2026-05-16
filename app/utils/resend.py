# app/utils/resend.py

import httpx
import logging
from ..config import RESEND_API_KEY, RESEND_AUDIENCE_ID

logger = logging.getLogger(__name__)

BASE_URL = "https://api.resend.com"
HEADERS = {
    "Authorization": f"Bearer {RESEND_API_KEY}",
    "Content-Type": "application/json",
}


async def add_to_ottomax_customers(
    email: str,
    full_name: str = "",
    plan: str = "essential"
) -> bool:
    try:
        full_name = full_name or ""
        name_parts = full_name.strip().split()

        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        async with httpx.AsyncClient(timeout=20) as client:

            # Step 1: Contact add/update to audience
            contact_response = await client.post(
                f"{BASE_URL}/audiences/{RESEND_AUDIENCE_ID}/contacts",
                headers=HEADERS,
                json={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "unsubscribed": False,
                    "data": {
                        "plan": plan,
                        "full_name": full_name
                    }
                }
            )

            if contact_response.status_code not in [200, 201]:
                logger.error(
                    f"Resend contact add failed: "
                    f"{contact_response.status_code} | {contact_response.text}"
                )
                return False

            logger.info(f"Resend contact added to audience: {email}")

            # Step 2: Send custom event to trigger automation
            event_response = await client.post(
                f"{BASE_URL}/events/send",
                headers=HEADERS,
                json={
                    "event": "Ottomax Customers",
                    "email": email,
                    "payload": {
                        "plan": plan,
                        "full_name": full_name,
                        "first_name": first_name,
                        "last_name": last_name
                    }
                }
            )

            if event_response.status_code in [200, 201, 202]:
                logger.info(f"Resend event triggered: {email} | Plan: {plan}")
                return True

            logger.error(
                f"Resend event trigger failed: "
                f"{event_response.status_code} | {event_response.text}"
            )
            return False

    except Exception as e:
        logger.error(f"add_to_ottomax_customers error: {e}")
        return False