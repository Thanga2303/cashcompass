"""PayPal sandbox checkout (Orders v2): create an order, send the buyer to PayPal, capture, read back the result."""
import uuid

import requests

BASE = "https://api-m.sandbox.paypal.com"


class PayPalError(Exception):
    pass


def _check(r):
    if r.status_code >= 400:
        try:
            j = r.json()
            msg = j.get("error_description") or j.get("message") or j.get("name") or r.text
            names = [d.get("issue", "") for d in j.get("details", [])]
        except Exception:
            msg, names = r.text, []
        err = PayPalError(f"PayPal said: {msg} ({r.status_code})")
        err.issues = names
        raise err
    return r.json()


def _token(client_id, secret):
    r = requests.post(f"{BASE}/v1/oauth2/token", auth=(client_id, secret),
                      data={"grant_type": "client_credentials"}, headers={"Accept": "application/json"}, timeout=20)
    return _check(r)["access_token"]


def _headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def create_order(client_id, secret, usd, description, return_url, inr_rate):
    """Returns (order_id, url_to_send_the_buyer_to)."""
    body = {"intent": "CAPTURE",
            "purchase_units": [{"amount": {"currency_code": "USD", "value": f"{usd:.2f}"},
                                "description": description[:120], "custom_id": f"inr_rate={inr_rate}"}],
            "payment_source": {"paypal": {"experience_context": {
                "return_url": return_url, "cancel_url": return_url, "user_action": "PAY_NOW",
                "shipping_preference": "NO_SHIPPING", "brand_name": "CashCompass"}}}}
    h = _headers(_token(client_id, secret))
    h["PayPal-Request-Id"] = str(uuid.uuid4())
    data = _check(requests.post(f"{BASE}/v2/checkout/orders", json=body, headers=h, timeout=20))
    link = next((x["href"] for x in data.get("links", []) if x.get("rel") in ("payer-action", "approve")), None)
    if not link:
        raise PayPalError("PayPal did not return an approval link.")
    return data["id"], link


def get_order(client_id, secret, order_id):
    h = _headers(_token(client_id, secret))
    return _check(requests.get(f"{BASE}/v2/checkout/orders/{order_id}", headers=h, timeout=20))


def capture_order(client_id, secret, order_id):
    """Captures the approved order (safe to call again: an already-captured order is just read back)."""
    h = _headers(_token(client_id, secret))
    r = requests.post(f"{BASE}/v2/checkout/orders/{order_id}/capture", json={}, headers=h, timeout=20)
    try:
        _check(r)
    except PayPalError as e:
        if "ORDER_ALREADY_CAPTURED" not in getattr(e, "issues", []):
            raise
    return get_order(client_id, secret, order_id)


def summarize(order):
    pu = order["purchase_units"][0]
    cap = (pu.get("payments", {}).get("captures") or [{}])[0]
    amt = cap.get("amount") or pu["amount"]
    try:
        rate = float(str(pu.get("custom_id", "")).split("=")[1])
    except Exception:
        rate = 85.0
    return {"completed": order.get("status") == "COMPLETED", "usd": float(amt["value"]),
            "description": pu.get("description", "PayPal payment"), "rate": rate,
            "capture_id": cap.get("id", order.get("id", ""))}