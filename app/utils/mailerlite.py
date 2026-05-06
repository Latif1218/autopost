# app/utils/mailerlite.py

import httpx
import logging
from ..config import MAILERLITE_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://connect.mailerlite.com/api"
HEADERS = {
    "Authorization": f"Bearer {MAILERLITE_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}


async def get_group_id(group_name: str) -> str | None:
    """Fetch ID using Group name"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/groups",
                headers=HEADERS
            )
            if response.status_code != 200:
                logger.error(f"Groups fetch failed: {response.text}")
                return None

            for group in response.json().get("data", []):
                if group["name"] == group_name:
                    return group["id"]

        logger.warning(f"Group '{group_name}' not found")
        return None

    except Exception as e:
        logger.error(f"get_group_id error: {e}")
        return None


async def add_to_ottomax_customers(
    email: str,
    full_name: str = "",
    plan: str = "essential"
) -> bool:
    """
    Added group 'Ottomax Customers' with  addSubscriber endpoint.
    Now MailerLite automation is triggered —
    Day 0, Day 2, Day 7 emails send automatically ।
    """
    try:
        group_id = await get_group_id("Ottomax Customers")
        if not group_id:
            logger.error("'Ottomax Customers' group Not Found in MailerLite")
            return False

        payload = {
            "email": email,
            "fields": {
                "name": full_name,
                "plan": plan,
            },
            "groups": [group_id],
            "status": "active"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/subscribers",
                headers=HEADERS,
                json=payload
            )

            if response.status_code in [200, 201]:
                logger.info(f"✅ MailerLite: {email} added to Ottomax Customers | Plan: {plan}")
                return True
            else:
                logger.error(f"MailerLite subscriber add failed: {response.text}")
                return False

    except Exception as e:
        logger.error(f"add_to_ottomax_customers error: {e}")
        return False