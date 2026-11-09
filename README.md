# CashCompass

An AI spending assistant. Ask where your money went in plain English, then pay with UPI or Razorpay.

## Files
- `cashcompass.py`: the Streamlit app (UI, saving, payments)
- `finance.py`: analytics, Money Universe, AI tools and the offline assistant (keep it next to `cashcompass.py`)

## Features
- Categorizes UPI and bank transactions from a CSV (date, description, amount)
- Chat with your spending, powered by Claude tool calling (demo mode works without an API key)
- Pay with a UPI link or QR code (GPay, PhonePe, Paytm)
- Razorpay test-mode payment links with status check

## Run it
```
pip install -r requirements.txt
streamlit run cashcompass.py
```

## Keys (optional)
Paste them in the sidebar, or set them in a `.env` file or your environment:
- Anthropic API key for the AI chat
- RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET (use test keys only)

Never commit your keys.

## Permanent storage (Supabase, free)
1. Create a project at supabase.com.
2. SQL Editor: run `supabase_setup.sql`.
3. Project Settings -> API: copy the Project URL and the `anon` key.
4. Add them locally in `.streamlit/secrets.toml`:
```
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "your-anon-key"
```
On Streamlit Community Cloud, paste the same two lines under App settings -> Secrets.
Without these, transactions are saved on the device only.

## Budget and income
Set your monthly budget and income in the sidebar. They are saved in `settings.json` on this device.
Budget health, money flow and savings answers need them; without them the app says what is missing.