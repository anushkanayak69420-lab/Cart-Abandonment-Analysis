"""
Synthetic e-commerce checkout funnel dataset generator.
Simulates session-level behavior through a 6-stage funnel with realistic,
correlated drop-off drivers (not random noise) so the downstream analysis
and model have real signal to find.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(42)
N = 18000

STAGES = ["product_view", "add_to_cart", "cart_view", "checkout_start", "shipping_info", "payment_info", "order_confirmed"]

devices = rng.choice(["Mobile", "Desktop", "Tablet"], size=N, p=[0.58, 0.34, 0.08])
traffic = rng.choice(["Paid Social", "Organic Search", "Email", "Direct", "Paid Search", "Affiliate"],
                     size=N, p=[0.27, 0.22, 0.13, 0.16, 0.14, 0.08])
new_customer = rng.choice([1, 0], size=N, p=[0.64, 0.36])  # 1 = new/guest, 0 = returning/logged-in
day_of_week = rng.choice(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], size=N,
                          p=[0.13,0.13,0.14,0.14,0.15,0.16,0.15])
hour = rng.integers(0, 24, size=N)

# cart value — pick from common order sizes, weighted so smaller carts are more common
cart_value = rng.choice([300, 600, 900, 1500, 2500, 4000, 6000], size=N,
                        p=[0.22, 0.22, 0.18, 0.15, 0.12, 0.07, 0.04])
cart_value = cart_value + rng.integers(-100, 100, size=N)  # small random jitter so values aren't all identical
cart_value = np.clip(cart_value, 200, 15000)

# shipping cost shown at checkout — a KEY hidden driver of abandonment
# free shipping threshold at 2000
shipping_cost = np.where(cart_value >= 2000, 0, rng.choice([0, 99, 149, 199], size=N, p=[0.25,0.35,0.25,0.15]))
shipping_shock = (shipping_cost > 0) & (cart_value < 800)  # small cart, gets hit with shipping fee

coupon_field_opened = rng.choice([1, 0], size=N, p=[0.34, 0.66])
coupon_applied_success = np.where(coupon_field_opened == 1, rng.choice([1, 0], size=N, p=[0.42, 0.58]), 0)
# failed coupon search -> leaves to hunt for a code elsewhere = classic abandonment driver
coupon_failed = (coupon_field_opened == 1) & (coupon_applied_success == 0)

# friction signals — most sessions have 0, a few have 1, very few have 2 or more
payment_retry = rng.choice([0, 1, 2, 3], size=N, p=[0.72, 0.19, 0.06, 0.03])
rage_click = rng.choice([0, 1, 2, 3], size=N, p=[0.78, 0.15, 0.05, 0.02])
form_field_errors = rng.choice([0, 1, 2, 3], size=N, p=[0.62, 0.24, 0.10, 0.04])

session_seconds_precheckout = rng.integers(20, 300, size=N)  # session length: 20 seconds to 5 minutes

# ---- Build stage-by-stage survival probabilities (this is where the story lives) ----
# Everyone starts at product_view -> add_to_cart (baseline)
p_view_to_cart = 0.62 + 0.05*(devices=="Desktop") - 0.03*(devices=="Mobile")
p_cart_to_cartview = 0.88

# checkout_start depends on new vs returning + device
p_cartview_to_checkout = 0.70 + 0.10*(new_customer==0) - 0.06*(devices=="Mobile")

# shipping_info step: hurt by mobile form friction + form errors expectation
p_checkout_to_shipping = 0.82 - 0.04*(devices=="Mobile")

# payment_info step: THIS is where shipping shock and coupon failure bite hardest
p_shipping_to_payment = (0.85
                          - 0.45*shipping_shock
                          - 0.30*coupon_failed
                          - 0.08*(devices=="Mobile")
                          - 0.10*(form_field_errors>=2))
p_shipping_to_payment = np.clip(p_shipping_to_payment, 0.08, 0.97)

# order_confirmed: hurt by payment retries and rage clicks (trust/technical friction)
p_payment_to_confirmed = (0.90
                           - 0.30*(payment_retry>=2)
                           - 0.20*(rage_click>=2)
                           - 0.05*(devices=="Mobile"))
p_payment_to_confirmed = np.clip(p_payment_to_confirmed, 0.10, 0.98)

def roll(p):
    return rng.random(N) < p

reach_cart          = roll(p_view_to_cart)
reach_cartview      = reach_cart & roll(p_cart_to_cartview)
reach_checkout      = reach_cartview & roll(p_cartview_to_checkout)
reach_shipping      = reach_checkout & roll(p_checkout_to_shipping)
reach_payment       = reach_shipping & roll(p_shipping_to_payment)
reach_confirmed     = reach_payment & roll(p_payment_to_confirmed)

def final_stage(i):
    if reach_confirmed[i]: return "order_confirmed"
    if reach_payment[i]: return "payment_info"
    if reach_shipping[i]: return "shipping_info"
    if reach_checkout[i]: return "checkout_start"
    if reach_cartview[i]: return "cart_view"
    if reach_cart[i]: return "add_to_cart"
    return "product_view"

last_stage = np.array([final_stage(i) for i in range(N)])
abandoned = last_stage != "order_confirmed"

# session timestamp over last 90 days
start = datetime(2026, 6, 30)
session_ts = [start + timedelta(days=int(rng.integers(0, 90)), hours=int(hour[i]), minutes=int(rng.integers(0,60))) for i in range(N)]

df = pd.DataFrame({
    "session_id": [f"S{100000+i}" for i in range(N)],
    "timestamp": session_ts,
    "day_of_week": day_of_week,
    "hour": hour,
    "device": devices,
    "traffic_source": traffic,
    "customer_type": np.where(new_customer==1, "New/Guest", "Returning/Logged-in"),
    "cart_value_inr": cart_value.astype(int),
    "shipping_cost_inr": shipping_cost.astype(int),
    "coupon_field_opened": coupon_field_opened,
    "coupon_applied_success": coupon_applied_success,
    "payment_retry_count": payment_retry,
    "rage_click_count": rage_click,
    "form_field_errors": form_field_errors,
    "session_seconds_before_checkout": session_seconds_precheckout,
    "last_stage_reached": last_stage,
    "abandoned": abandoned.astype(int),
})

df.to_csv("checkout_sessions.csv", index=False)
print(df.shape)
print(df["last_stage_reached"].value_counts())
print("Overall abandonment rate:", round(df["abandoned"].mean()*100,1), "%")
