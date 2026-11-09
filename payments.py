"""Pay tab: UPI deep link / QR and Razorpay test-mode payment links."""
import streamlit as st


def _is_mobile():
    try:
        ua = st.context.headers.get("User-Agent", "")
    except Exception:
        return False
    return any(k in ua for k in ("Android", "iPhone", "iPad", "Mobile"))


def render(rzp_id="", rzp_secret=""):
    # ---------- Pay via UPI (GPay / PhonePe / Paytm) ----------
    from io import BytesIO
    from urllib.parse import quote

    st.divider()
    st.subheader("💸 Pay with UPI")
    st.caption("Opens GPay, PhonePe, Paytm or any UPI app installed on your phone.")

    upi_id = st.text_input("Receiver UPI ID", placeholder="name@okhdfcbank")
    payee = st.text_input("Receiver name")
    amount = st.number_input("Amount (₹)", min_value=1.0, step=10.0)
    note = st.text_input("Note", value="Paid via CashCompass")

    if upi_id and payee:
        link = (f"upi://pay?pa={quote(upi_id)}&pn={quote(payee)}"
                f"&am={amount:.2f}&cu=INR&tn={quote(note)}")
        if _is_mobile():
            st.markdown(f'<a class="paybtn" href="{link}">👉 Tap to pay ₹{amount:,.0f}</a>', unsafe_allow_html=True)
        else:
            st.info("UPI links only open on a phone. On this laptop, scan the QR code below with GPay, PhonePe "
                    "or Paytm, or use the Razorpay section further down to pay in the browser.")
        try:
            import qrcode
            buf = BytesIO()
            qrcode.make(link).save(buf)
            st.image(buf.getvalue(), caption="Scan with any UPI app", width=240)
        except ImportError:
            st.caption("Run `pip install qrcode[pil]` to also show a QR code.")
        st.caption("To pay from your phone instead, copy this UPI link and send it to yourself:")
        st.code(link, language=None)

    # ---------- Razorpay (test mode) ----------
    import os
    import requests

    st.divider()
    st.subheader("🧾 Pay with Razorpay (test mode)")
    st.caption("Creates a real Razorpay payment link. Use test keys, so no real money moves.")

    rz_amount = st.number_input("Amount (₹)", min_value=1.0, step=10.0, key="rz_amount")
    rz_desc = st.text_input("Description", value="CashCompass payment", key="rz_desc")

    if st.button("Create payment link"):
        if not (rzp_id and rzp_secret):
            st.warning("Add your Razorpay test keys in the sidebar first.")
        else:
            try:
                r = requests.post(
                    "https://api.razorpay.com/v1/payment_links",
                    auth=(rzp_id, rzp_secret),
                    json={"amount": int(rz_amount * 100), "currency": "INR",
                          "description": rz_desc},
                    timeout=15)
                data = r.json()
                if r.status_code == 200:
                    st.session_state.rzp_link = data
                else:
                    st.error(data.get("error", {}).get("description", "Razorpay error"))
            except Exception as e:
                st.error(f"Could not reach Razorpay: {e}")

    link_data = st.session_state.get("rzp_link")
    if link_data:
        st.success("Payment link created")
        st.markdown(f"[Open payment page]({link_data['short_url']})")
        if st.button("Check payment status"):
            s = requests.get(f"https://api.razorpay.com/v1/payment_links/{link_data['id']}",
                             auth=(rzp_id, rzp_secret), timeout=15).json()
            st.write("Status:", s.get("status", "unknown"))