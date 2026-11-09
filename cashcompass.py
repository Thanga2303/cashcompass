import json
from datetime import date
import pandas as pd
import streamlit as st

import streamlit.components.v1 as components

import theme

theme.apply()

# ---------- Categorizer ----------
CATEGORIES = {
    "Food": ["swiggy", "zomato", "cafe", "restaurant", "dominos", "mcdonald"],
    "Transport": ["uber", "ola", "rapido", "metro", "petrol", "irctc"],
    "Shopping": ["amazon", "flipkart", "myntra", "ajio"],
    "Bills": ["jio", "airtel", "electricity", "recharge", "wifi"],
    "Entertainment": ["netflix", "spotify", "bookmyshow", "hotstar"],
    "Education": ["udemy", "coursera", "book", "stationery"],
}


def categorize(desc):
    d = str(desc).lower()
    for cat in CATEGORIES:  # an explicit category name, like "Lunch (Food)", wins
        if cat.lower() in d:
            return cat
    for cat, words in CATEGORIES.items():
        if any(w in d for w in words):
            return cat
    return "Other"


SAMPLE = pd.DataFrame({
    "date": ["2026-11-01", "2026-11-01", "2026-11-02", "2026-11-03", "2026-11-04",
             "2026-11-05", "2026-11-05", "2026-11-06", "2026-11-07", "2026-11-07"],
    "description": ["Swiggy order", "Uber ride", "Amazon - headphones", "Jio recharge",
                    "Zomato order", "Netflix", "Coursera course", "Rapido", "Cafe Denim", "Stationery shop"],
    "amount": [320, 180, 1499, 299, 410, 199, 799, 90, 250, 120],
})

# ---------- Data ----------
with st.sidebar:
    st.header("Setup")
    file = st.file_uploader("Upload transactions CSV", type="csv",
                            help="Columns needed: date, description, amount")
    api_key = st.text_input("Anthropic API key (optional)", type="password",
                            help="Leave empty to use demo mode")

import os
import sqlite3
import requests


def secret(name):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, "")


SB_URL = str(secret("SUPABASE_URL")).rstrip("/")
SB_KEY = str(secret("SUPABASE_KEY"))
SB_HEAD = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json"}
USE_CLOUD = bool(SB_URL and SB_KEY)
DB = "cashcompass.db"


def local_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS tx (date TEXT, description TEXT, amount REAL, "
                "UNIQUE(date, description, amount))")
    return con


def save_tx(rows):
    if USE_CLOUD:  # permanent: Supabase
        r = requests.post(f"{SB_URL}/rest/v1/tx?on_conflict=date,description,amount",
                          headers={**SB_HEAD, "Prefer": "resolution=ignore-duplicates,return=minimal"},
                          json=rows, timeout=20)
        r.raise_for_status()
    else:  # this device only: SQLite
        con = local_db()
        con.executemany("INSERT OR IGNORE INTO tx VALUES (?,?,?)",
                        [(x["date"], x["description"], x["amount"]) for x in rows])
        con.commit()
        con.close()


def load_tx():
    if USE_CLOUD:
        r = requests.get(f"{SB_URL}/rest/v1/tx?select=date,description,amount",
                         headers=SB_HEAD, timeout=20)
        r.raise_for_status()
        return pd.DataFrame(r.json(), columns=["date", "description", "amount"])
    con = local_db()
    out = pd.read_sql("SELECT date, description, amount FROM tx", con)
    con.close()
    return out


st.sidebar.caption("☁️ Saved permanently (Supabase)" if USE_CLOUD
                   else "💾 Saved on this device only. Add Supabase keys to make it permanent.")

def clean_upload(f):
    raw = pd.read_csv(f)
    raw.columns = [c.strip().lower() for c in raw.columns]
    missing = {"date", "description", "amount"} - set(raw.columns)
    if missing:
        raise ValueError("CSV is missing column(s): " + ", ".join(sorted(missing)))
    out = raw[["date", "description", "amount"]].copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["amount"] = pd.to_numeric(out["amount"], errors="coerce")
    out["description"] = out["description"].astype(str).str.strip()
    bad = out.isna().any(axis=1) | (out["amount"] <= 0)
    out = out[~bad]
    if out.empty:
        raise ValueError("No valid rows found. Check the date and amount columns.")
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    return out, int(bad.sum())


if file:
    try:
        new, skipped = clean_upload(file)
        rows = [{"date": d, "description": ds, "amount": float(a)} for d, ds, a in new.values.tolist()]
        save_tx(rows)
        st.sidebar.success(f"Saved {len(rows)} transactions" + (f" ({skipped} invalid rows skipped)" if skipped else ""))
    except Exception as e:
        st.sidebar.error(f"Could not save: {e}")

try:
    df = load_tx()
except Exception as e:
    st.error(f"Could not load saved transactions: {e}")
    df = pd.DataFrame(columns=["date", "description", "amount"])
if df.empty:
    df = SAMPLE.copy()
    st.info("Showing sample data. Upload your CSV from the sidebar to save your own.")
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.strftime("%B %Y")
df["category"] = df["description"].apply(categorize)

# Month totals (from everything saved), then filter the rest of the page by month
monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum().sort_index()
choices = ["All time"] + [m.strftime("%B %Y") for m in monthly.index[::-1]]
picked = st.sidebar.selectbox("Month", choices)
df_all = df
if picked != "All time":
    df = df[df["month"] == picked]
cur = (pd.Period(pd.to_datetime(picked, format="%B %Y"), "M") if picked != "All time"
       else df_all["date"].dt.to_period("M").max())

SETTINGS = "settings.json"
try:
    with open(SETTINGS) as fh:
        cfg = json.load(fh)
except Exception:
    cfg = {}
budget = st.sidebar.number_input("Monthly budget (₹)", min_value=0.0, step=500.0, value=float(cfg.get("budget", 0)))
income = st.sidebar.number_input("Monthly income (₹)", min_value=0.0, step=500.0, value=float(cfg.get("income", 0)))
rzp_id = st.sidebar.text_input("Razorpay Key ID", value=os.getenv("RAZORPAY_KEY_ID", ""))
rzp_secret = st.sidebar.text_input("Razorpay Key Secret", type="password", value=os.getenv("RAZORPAY_KEY_SECRET", ""))
if (budget, income) != (cfg.get("budget", 0), cfg.get("income", 0)):
    try:
        with open(SETTINGS, "w") as fh:
            json.dump({"budget": budget, "income": income}, fh)
    except Exception:
        pass

# ---------- Dashboard + AI assistant ----------
import finance as fin

ctx = {"df": df_all, "period": cur, "budget": float(budget), "income": float(income)}
cur_total = float(fin.month_df(df_all, cur)["amount"].sum())

PAGES = [("dash", "📊 Dashboard"), ("add", "➕ Add Expense"), ("chat", "🤖 AI Chat"), ("pay", "💸 Pay")]
st.session_state.setdefault("page", "dash")


def go(p):
    st.session_state.page = p


with st.container(key="navbar"):
    for col, (pid, label) in zip(st.columns(4), PAGES):
        col.button(label, key=f"nav_{pid}", on_click=go, args=(pid,), use_container_width=True,
                   type="primary" if st.session_state.page == pid else "secondary")
page = st.session_state.page

if page == "dash":
    c1, c2, c3 = st.columns(3)
    c1.metric("Total spent", f"₹{df['amount'].sum():,.0f}")
    c2.metric("Transactions", len(df))
    c3.metric(f"{cur.strftime('%b %Y')} spend", fin.inr(cur_total))

    left, right = st.columns([1, 2])
    with left:
        st.markdown(fin.budget_ring_html(cur_total, float(budget)), unsafe_allow_html=True)
    with right:
        st.subheader("Insights")
        for tip in fin.insights(df_all, cur, float(budget), float(income)):
            st.markdown(f"<div class='glass tip'>💡 {tip}</div>", unsafe_allow_html=True)

    st.subheader("🌌 Money Universe")
    st.caption(f"{cur.strftime('%B %Y')}: planet size = amount spent. Hover a planet, click it for details.")
    components.html(fin.universe_html(df_all, cur), height=470)

    st.subheader("🔥 Spending heatmap")
    st.markdown(fin.heatmap_html(df_all, cur), unsafe_allow_html=True)
    st.subheader("🧬 Spending personality")
    st.markdown(fin.personality_html(df_all, cur), unsafe_allow_html=True)
    st.subheader("💧 Money flow")
    st.markdown(fin.flow_html(df_all, cur, float(income)), unsafe_allow_html=True)
    st.subheader("🕒 Financial timeline")
    st.markdown(fin.timeline_html(df_all, cur), unsafe_allow_html=True)

    st.subheader("📅 Month by month")
    st.caption("Each stack of coins is one month. Hover a tower, click it for details. The gold tower is the month in view.")
    components.html(fin.towers_html(df_all, cur), height=430)

if page == "add":
    st.subheader("➕ Add an expense")
    st.caption("Saved straight into CashCompass. You can still upload a CSV from the sidebar.")
    if st.session_state.get("flash"):
        st.success(st.session_state.pop("flash"))
    with st.form("add_expense", clear_on_submit=True):
        d_in = st.date_input("Date", value=date.today())
        desc_in = st.text_input("What was it for?", placeholder="Swiggy dinner, Uber, Amazon order...")
        amt_in = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
        pick = st.selectbox("Category", ["Auto-detect"] + list(CATEGORIES))
        go = st.form_submit_button("Save expense", use_container_width=True)
    st.caption("Two identical entries (same date, name and amount) are saved as one.")
    if go:
        desc_in = desc_in.strip()
        if not desc_in or amt_in <= 0:
            st.error("Enter what it was for and an amount above 0.")
        else:
            if pick != "Auto-detect" and pick.lower() not in desc_in.lower():
                desc_in = f"{desc_in} ({pick})"
            try:
                save_tx([{"date": d_in.strftime("%Y-%m-%d"), "description": desc_in, "amount": float(amt_in)}])
                st.session_state.flash = f"Saved ₹{amt_in:,.0f} for {desc_in} on {d_in:%d %b %Y} (category: {categorize(desc_in)})."
                st.rerun()
            except Exception as e:
                st.error(f"Could not save: {e}")

SUGGESTED = ["How can I save more money?", "Where did my money go?", "Am I overspending?",
             "Analyze my spending habits.", "Create a monthly budget.", "Find my unnecessary expenses."]


def ask(q):
    st.session_state.pending = q


def clear_chat():
    st.session_state.chat = []
    st.session_state.followups = []
    st.session_state.mem = {}


if page == "chat":
    st.subheader("Ask CashCompass")
    st.caption("Type any question about your transactions, budget or savings, or tap a suggestion.")
    if not api_key:
        st.info("Offline mode: I answer common money questions from your data. "
                "Add an Anthropic API key in the sidebar to ask anything.")
    for k, v in (("chat", []), ("followups", []), ("mem", {})):
        st.session_state.setdefault(k, v)

    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED):
        cols[i % 3].button(q, key=f"sg{i}", on_click=ask, args=(q,), use_container_width=True)
    qa1, qa2 = st.columns(2)
    qa1.button("📄 Financial summary", on_click=ask, args=("Give me a financial summary",), use_container_width=True)
    qa2.button("🧹 Clear chat", on_click=clear_chat, use_container_width=True)

    hist = st.container()
    chips = st.container()
    typed = st.chat_input("Ask anything about your money...")
    question = typed or st.session_state.pop("pending", None)
    if question:
        question = question.strip()[:500]
        st.session_state.chat.append(("user", question))
        with hist:
            with st.spinner("CashCompass is analysing your transactions…"):
                try:
                    if api_key:
                        answer, fu = fin.ask_claude(question, ctx, api_key, st.session_state.chat[:-1])
                    else:
                        answer, fu = fin.answer_demo(question, ctx, st.session_state.mem)
                except Exception as e:
                    answer, fu = fin.answer_demo(question, ctx, st.session_state.mem)
                    answer = f"⚠️ The AI service had a problem ({type(e).__name__}), so here is the offline answer:\n\n{answer}"
        st.session_state.chat.append(("assistant", answer))
        st.session_state.followups = fu
    with hist:
        for role, text in st.session_state.chat:
            st.chat_message(role).write(text)
    with chips:
        if st.session_state.followups:
            fcols = st.columns(len(st.session_state.followups))
            for i, q in enumerate(st.session_state.followups):
                fcols[i].button(q, key=f"fu{i}_{len(st.session_state.chat)}", on_click=ask, args=(q,), use_container_width=True)

if page == "pay":
    import payments

    payments.render(rzp_id, rzp_secret)