"""Offline assistant (no API key): intent rules over the same data."""
import pandas as pd
from datetime import date

from fin_core import *  # noqa: F401,F403
from visuals import personality


# ---------------- Offline assistant (no API key): intent rules over the same data ----------------
SYN = {"food": ["food", "eat", "restaurant", "meal"], "shopping": ["shopping", "shop", "purchase"],
       "transport": ["transport", "travel", "ride", "commute"], "bills": ["bill", "recharge"],
       "entertainment": ["entertainment", "movie", "subscription"], "education": ["education", "study", "course"]}
NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _resolve(ql, df):
    cats = {c.lower(): c for c in df["category"].unique()}
    cat = next((cats[c] for c in cats if c in ql), None)
    if not cat:
        for k, words in SYN.items():
            if k in cats and any(w in ql for w in words):
                cat = cats[k]
                break
    firsts = {str(d).lower().split()[0] for d in df["description"] if len(str(d).split()[0]) >= 4}
    merch = next((m for m in firsts if m in ql), None)
    return cat, merch


def _tx_lines(d, n=5):
    return "\n".join(f"- {r.date:%d %b}: {r.description} ({r.category}), {inr(r.amount)}" for r in d.head(n).itertuples())


def financial_summary(ctx):
    df, p, b, inc = ctx["df"], ctx["period"], ctx["budget"], ctx["income"]
    cur = month_df(df, p)
    if cur.empty:
        return f"No transactions are recorded for {p.strftime('%B %Y')}.", ["Show my latest transactions"]
    total = float(cur["amount"].sum())
    by = cur.groupby("category")["amount"].sum().sort_values(ascending=False)
    lines = [f"**{p.strftime('%B %Y')}:** you spent {inr(total)} across {len(cur)} transactions.",
             f"Your highest category is **{by.index[0]}** ({inr(by.iloc[0])}, {by.iloc[0] / total:.0%})."]
    pt = float(month_df(df, p - 1)["amount"].sum())
    if pt > 0:
        ch = (total - pt) / pt * 100
        lines.append(f"That is {abs(ch):.0f}% {'more' if ch >= 0 else 'less'} than {(p - 1).strftime('%B')} ({inr(pt)}).")
    if b > 0:
        lines.append(f"Budget {inr(b)}: {inr(b - total)} left." if total <= b else f"You are {inr(total - b)} over your {inr(b)} budget.")
    else:
        lines.append("No monthly budget is set, so the remaining budget cannot be calculated. Add it in the sidebar.")
    if inc > 0:
        lines.append(f"Against your income of {inr(inc)}, you are {inr(abs(inc - total))} {'under' if inc >= total else 'over'}.")
    return "\n\n".join(lines), ["How can I save more money?", "Which expenses can I reduce?", "Create a monthly budget"]


def advice(ctx):
    df, p, b, inc = ctx["df"], ctx["period"], ctx["budget"], ctx["income"]
    cur = month_df(df, p)
    if cur.empty:
        return "There are no transactions this month to analyse yet.", []
    total = float(cur["amount"].sum())
    by = cur.groupby("category")["amount"].sum().sort_values(ascending=False)
    wants = cur[~cur["category"].isin(NEEDS)]
    wby = wants.groupby("category")["amount"].sum().sort_values(ascending=False)
    tc = wby.index[0] if len(wby) else by.index[0]
    tv = float(wby.iloc[0] if len(wby) else by.iloc[0])
    days = max((cur["date"].max() - cur["date"].min()).days + 1, 1)
    weekly = tv / days * 7
    big = ", ".join(f"{r.description} ({inr(r.amount)})" for r in (wants if len(wants) else cur).nlargest(2, "amount").itertuples())
    cut = tv * 0.15
    lines = [f"You have spent {inr(total)} this month across {len(cur)} transactions.",
             f"Your highest spending category is **{by.index[0]}** ({inr(by.iloc[0])}).",
             "Here are three ways to improve:",
             f"1. Set a weekly **{tc}** limit of about {inr(weekly * 0.85)} (you are on pace for {inr(weekly)}).",
             f"2. Pause impulse buys. Your biggest wants were {big}.",
             f"3. Pay yourself first: trimming {tc} by 15% frees about {inr(cut)}" + (f", taking your left-over to {inr(max(inc - total, 0) + cut)}." if inc > 0 else ". Add your income in the sidebar to see the effect on savings.")]
    if b > 0:
        lines.append(f"You have used {total / b:.0%} of your {inr(b)} budget.")
    lines.append(f"**Target:** cut {tc} spending by 15% next month, about {inr(cut)} less.")
    return "\n\n".join(lines), ["Which expenses can I reduce?", "Create a monthly budget", "Am I spending more than I earn?"]


def answer_demo(q, ctx, mem):
    df, p, b, inc = ctx["df"], ctx["period"], ctx["budget"], ctx["income"]
    ql = q.lower()
    if df.empty:
        return "There are no transactions yet. Upload a CSV from the sidebar first.", []
    cat, merch = _resolve(ql, df)
    if not cat and not merch and mem.get("cat") and any(w in ql for w in ["what about", "and last", "and this", "that", "same", "them"]):
        cat = mem["cat"]
    if cat:
        mem["cat"] = cat
    cur = month_df(df, p)
    total = float(cur["amount"].sum())
    fu_cat = [f"Show my {cat} transactions", f"Compare my {cat} this month and last month"] if cat else []

    if "today" in ql:
        d = df[df["date"].dt.normalize() == pd.Timestamp(date.today())]
        if cat:
            d = d[d["category"] == cat]
        return (f"You spent {inr(d['amount'].sum())} today ({date.today():%d %b}) across {len(d)} transactions." if len(d)
                else f"There are no transactions recorded for today ({date.today():%d %b})."), ["Give me a financial summary"]
    if "compare" in ql or ("last month" in ql and any(w in ql for w in ["this month", "than", "vs", "versus"])):
        a_, b_ = spend(df, p, cat), spend(df, p - 1, cat)
        what = cat or "spending"
        if month_df(df, p - 1).empty:
            return f"There are no records for {(p - 1).strftime('%B %Y')}, so the comparison cannot be calculated.", ["Give me a financial summary"]
        x, y = float(a_["amount"].sum()), float(b_["amount"].sum())
        diff = f"{abs(x - y) / y:.0%} {'more' if x >= y else 'less'}" if y else "n/a"
        return f"Your {what} in {p.strftime('%B')}: {inr(x)}. In {(p - 1).strftime('%B')}: {inr(y)}. That is {diff} this month.", ["How can I save more money?"]
    if any(w in ql for w in ["remaining", "left"]) and "budget" in ql:
        return ((f"Your monthly budget is {inr(b)}; you have spent {inr(total)}, so {inr(b - total)} remains." if total <= b
                 else f"You are {inr(total - b)} over your {inr(b)} budget.") if b > 0
                else "I can't calculate the remaining budget because no monthly budget is set. Add it in the sidebar."), ["Create a monthly budget"]
    if "save" in ql and any(w in ql for w in ["week", "weekly"]) and "much" in ql:
        if inc <= 0:
            return "I can't work out a weekly saving target because your monthly income isn't set. Add it in the sidebar.", []
        cap = max(inc - total, 0)
        return (f"A common goal is saving 20% of income: {inr(inc * 0.2 / 4.345)} a week. "
                f"Based on this month's spending, you currently have {inr(cap)} left, about {inr(cap / 4.345)} a week."), ["Which expenses can I reduce?"]
    if any(w in ql for w in ["earn", "income"]) and any(w in ql for w in ["more than", "spending", "overspend"]):
        if inc <= 0:
            return "I can't tell, because your monthly income isn't set. Add it in the sidebar and ask again.", []
        return (f"Yes. You spent {inr(total)} against an income of {inr(inc)}, {inr(total - inc)} more than you earn." if total > inc
                else f"No. You spent {inr(total)} against an income of {inr(inc)}, leaving {inr(inc - total)}."), ["How can I save more money?"]
    if any(w in ql for w in ["reduce", "unnecessary", "cut", "overspend", "control", "save more", "how can i save", "improve", "habit", "analy"]):
        if "analy" in ql or "habit" in ql:
            s, f = financial_summary(ctx)
            pr = personality(df, p)
            return (s + (f"\n\nSpending personality: **{pr['title']}**. {pr['why']}" if pr else "")), f
        return advice(ctx)
    if "budget" in ql and any(w in ql for w in ["create", "plan", "make", "set"]):
        base = inc if inc > 0 else total
        note = "your income" if inc > 0 else "your current spending (add income in the sidebar for a better plan)"
        return (f"A 50/30/20 plan based on {note} ({inr(base)}):\n\n- Needs (bills, transport, food, education): {inr(base * .5)}\n"
                f"- Wants (shopping, entertainment): {inr(base * .3)}\n- Savings: {inr(base * .2)}\n\n"
                f"This month you spent {inr(float(cur[cur['category'].isin(NEEDS)]['amount'].sum()))} on needs and "
                f"{inr(float(cur[~cur['category'].isin(NEEDS)]['amount'].sum()))} on wants."), ["Which expenses can I reduce?"]
    if any(w in ql for w in ["expensive", "biggest", "largest", "highest"]) and "categor" not in ql:
        r = df.nlargest(1, "amount").iloc[0]
        return f"Your most expensive transaction is {r['description']} ({r['category']}) for {inr(r['amount'])} on {r['date']:%d %b %Y}.", ["Show my top five expenses"]
    if "top" in ql:
        n = next((v for k, v in NUM.items() if k in ql), None) or next((int(t) for t in ql.split() if t.isdigit()), 5)
        return f"Your top {n} expenses:\n\n" + _tx_lines(df.nlargest(n, "amount"), n), ["What was my most expensive transaction?"] + fu_cat[:1]
    if any(w in ql for w in ["show", "list", "transactions", "latest", "recent"]):
        d = spend(df, None, cat, merch).sort_values("date", ascending=False)
        return (f"{len(d)} matching transactions, {inr(d['amount'].sum())} in total. Latest:\n\n" + _tx_lines(d, 8)) if len(d) else "No matching transactions found.", fu_cat
    if cat or merch:
        scope_p = p - 1 if "last month" in ql else p
        d = spend(df, scope_p, cat, merch)
        what = cat or merch
        return f"You spent {inr(d['amount'].sum())} on {what} in {scope_p.strftime('%B %Y')} ({len(d)} transaction{"" if len(d) == 1 else "s"}).", fu_cat
    if "week" in ql:
        end = pd.Timestamp(date.today())
        d = spend(df, start=end - pd.Timedelta(days=6), end=end + pd.Timedelta(days=1))
        return (f"In the last 7 days you spent {inr(d['amount'].sum())} across {len(d)} transactions." if len(d)
                else "There are no transactions in the last 7 days."), ["Give me a financial summary"]
    if any(w in ql for w in ["summary", "where did my money", "spend", "total", "how much"]):
        return financial_summary(ctx)
    return ("In offline mode I can answer questions about your totals, categories, merchants, budgets, savings and overspending. "
            "Add an Anthropic API key in the sidebar and I can answer open-ended questions too."), ["Give me a financial summary", "How can I save more money?"]