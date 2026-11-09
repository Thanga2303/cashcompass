"""Shared helpers for CashCompass."""
import html
import json
import math
from datetime import date

import pandas as pd

NEEDS = {"Bills", "Transport", "Education", "Food"}
COLORS = {"Shopping": "#F472B6", "Food": "#FBBF24", "Education": "#34D399", "Bills": "#60A5FA",
          "Transport": "#A78BFA", "Entertainment": "#F87171", "Other": "#94A3B8"}


def inr(v):
    return f"₹{v:,.0f}"


def month_df(df, period):
    return df[df["date"].dt.to_period("M") == period]


def spend(df, period=None, cat=None, merch=None, start=None, end=None):
    d = df
    if period is not None:
        d = month_df(d, period)
    if cat:
        d = d[d["category"] == cat]
    if merch:
        d = d[d["description"].str.lower().str.contains(merch, regex=False)]
    if start is not None:
        d = d[d["date"] >= start]
    if end is not None:
        d = d[d["date"] <= end]
    return d