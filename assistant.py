"""AI assistant: database-backed tools, Claude agent and the offline assistant."""
import json
from datetime import date

import pandas as pd

from fin_core import *  # noqa: F401,F403
from visuals import personality


# ---------------- Assistant: database-backed tools ----------------
TOOLS = [
    {"name": "query_transactions", "description": "Find transactions. Filters are optional. Returns count, total and rows.",
     "input_schema": {"type": "object", "properties": {
         "category": {"type": "string"}, "merchant": {"type": "string", "description": "text in the description"},
         "start": {"type": "string", "description": "YYYY-MM-DD"}, "end": {"type": "string", "description": "YYYY-MM-DD"},
         "min_amount": {"type": "number"}, "max_amount": {"type": "number"},
         "sort_by": {"type": "string", "enum": ["date", "amount"]}, "limit": {"type": "integer"}}}},
    {"name": "summarize", "description": "Total spend grouped by category, merchant, day, week or month.",
     "input_schema": {"type": "object", "properties": {
         "group_by": {"type": "string", "enum": ["category", "merchant", "day", "week", "month"]},
         "start": {"type": "string"}, "end": {"type": "string"}}, "required": ["group_by"]}},
    {"name": "compare_periods", "description": "Compare spending between two months (YYYY-MM), optionally for one category.",
     "input_schema": {"type": "object", "properties": {"period_a": {"type": "string"}, "period_b": {"type": "string"},
                                                       "category": {"type": "string"}}, "required": ["period_a", "period_b"]}},
    {"name": "financial_status", "description": "Budget, income, this month's spend, remaining budget and today's spend.",
     "input_schema": {"type": "object", "properties": {}}},
]


def run_tool(name, a, ctx):
    df = ctx["df"]
    if name == "query_transactions":
        d = df
        if a.get("category"):
            d = d[d["category"].str.lower() == a["category"].lower()]
        if a.get("merchant"):
            d = d[d["description"].str.lower().str.contains(a["merchant"].lower(), regex=False)]
        if a.get("start"):
            d = d[d["date"] >= pd.to_datetime(a["start"], errors="coerce")]
        if a.get("end"):
            d = d[d["date"] <= pd.to_datetime(a["end"], errors="coerce")]
        if a.get("min_amount") is not None:
            d = d[d["amount"] >= a["min_amount"]]
        if a.get("max_amount") is not None:
            d = d[d["amount"] <= a["max_amount"]]
        d = d.sort_values("amount" if a.get("sort_by") == "amount" else "date", ascending=False)
        rows = [{"date": f"{r.date:%Y-%m-%d}", "description": r.description, "category": r.category, "amount": float(r.amount)}
                for r in d.head(min(int(a.get("limit", 10)), 50)).itertuples()]
        return {"count": int(len(d)), "total": float(d["amount"].sum()), "transactions": rows}
    if name == "summarize":
        d = df
        if a.get("start"):
            d = d[d["date"] >= pd.to_datetime(a["start"], errors="coerce")]
        if a.get("end"):
            d = d[d["date"] <= pd.to_datetime(a["end"], errors="coerce")]
        key = {"category": d["category"], "merchant": d["description"],
               "day": d["date"].dt.strftime("%Y-%m-%d"), "week": d["date"].dt.to_period("W").astype(str),
               "month": d["date"].dt.to_period("M").astype(str)}[a.get("group_by", "category")]
        return {str(k): float(v) for k, v in d.groupby(key)["amount"].sum().sort_values(ascending=False).items()}
    if name == "compare_periods":
        out = {}
        for k in ("period_a", "period_b"):
            d = month_df(df, pd.Period(a[k], "M"))
            if a.get("category"):
                d = d[d["category"].str.lower() == a["category"].lower()]
            out[a[k]] = {"total": float(d["amount"].sum()), "count": int(len(d))}
        return out
    if name == "financial_status":
        p = ctx["period"]
        cur = month_df(df, p)
        today = pd.Timestamp(date.today())
        return {"period": str(p), "spent_this_period": float(cur["amount"].sum()),
                "budget": ctx["budget"] or "not set", "income": ctx["income"] or "not set",
                "remaining_budget": (ctx["budget"] - float(cur["amount"].sum())) if ctx["budget"] else "cannot calculate: no budget set",
                "spent_today": float(df[df["date"].dt.normalize() == today]["amount"].sum()),
                "transactions": int(len(cur))}
    return {"error": "unknown tool"}


def snapshot(ctx):
    df, p = ctx["df"], ctx["period"]
    cur = month_df(df, p)
    by = cur.groupby("category")["amount"].sum().sort_values(ascending=False)
    return (f"Today: {date.today():%Y-%m-%d}. Records span {df['date'].min():%Y-%m-%d} to {df['date'].max():%Y-%m-%d} ({len(df)} transactions).\n"
            f"Current period {p}: spent {inr(cur['amount'].sum())} in {len(cur)} transactions; previous month {inr(month_df(df, p - 1)['amount'].sum())}.\n"
            f"Categories this period: " + (", ".join(f"{k} {inr(v)}" for k, v in by.items()) or "none") + "\n"
            f"Monthly budget: {inr(ctx['budget']) if ctx['budget'] else 'NOT SET'}. Monthly income: {inr(ctx['income']) if ctx['income'] else 'NOT SET'}.")


SYSTEM = ("You are CashCompass, an AI financial assistant. Rules: "
          "1) Every figure must come from the tools or the snapshot below. Never invent transactions, income, budgets or numbers. "
          "2) For finance questions, call the tools to retrieve records and calculate before answering. "
          "3) If something cannot be calculated from the records (for example income or budget is NOT SET), say exactly what is missing and that it can be added in the sidebar. "
          "4) For advice, use the real category totals, give practical steps and a realistic target. "
          "5) Use the conversation for follow-up questions. "
          "6) For unrelated questions answer briefly and naturally without making up personal financial insights. "
          "7) Use ₹ and markdown, under 170 words. "
          "8) End with one line: 'Follow-ups: question one | question two | question three' (short questions).\n\nSNAPSHOT:\n")


def split_followups(text):
    if "Follow-ups:" in text:
        body, _, tail = text.rpartition("Follow-ups:")
        return body.strip(), [x.strip(" -•") for x in tail.split("|") if x.strip()][:3]
    return text.strip(), []


def ask_claude(question, ctx, key, history):
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    msgs = [{"role": r, "content": t} for r, t in history[-10:]] + [{"role": "user", "content": question}]
    while msgs[0]["role"] != "user":
        msgs.pop(0)
    system = SYSTEM + snapshot(ctx)
    for _ in range(6):
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=1000, tools=TOOLS, system=system, messages=msgs)
        if r.stop_reason != "tool_use":
            return split_followups("".join(b.text for b in r.content if b.type == "text"))
        msgs.append({"role": "assistant", "content": r.content})
        res = []
        for b in r.content:
            if b.type == "tool_use":
                try:
                    out = run_tool(b.name, b.input, ctx)
                except Exception as e:
                    out = {"error": str(e)}
                res.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(out)})
        msgs.append({"role": "user", "content": res})
    return "I couldn't finish that. Please try rephrasing.", []