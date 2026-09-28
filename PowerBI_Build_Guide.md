# Power BI Dashboard: Build Notes

Data source: `checkout_sessions.csv` (Get Data > Text/CSV).

## 1. Data preparation
- Set column types: `timestamp` as Date, all `*_inr` and `*_count` columns as Whole Number.
- Add a calculated column that flags "shipping shock" (a small cart that was charged a shipping fee):

```DAX
Shipping Shock =
IF('checkout_sessions'[shipping_cost_inr] > 0 && 'checkout_sessions'[cart_value_inr] < 800, 1, 0)
```

## 2. Measures
```DAX
Total Sessions = COUNTROWS('checkout_sessions')
Abandonment Rate = DIVIDE(CALCULATE([Total Sessions], 'checkout_sessions'[abandoned]=1), [Total Sessions])
Revenue Lost = CALCULATE(SUM('checkout_sessions'[cart_value_inr]), 'checkout_sessions'[abandoned]=1)
```

## 3. Dashboard layout
1. **Funnel visual**: stages on the axis, session counts as the value. Shows where sessions stop in checkout.
2. **Two KPI cards**: `Abandonment Rate` filtered to `Shipping Shock = 1` and to `Shipping Shock = 0` (87.5% vs 68.9%).
3. **Bar chart**: `Abandonment Rate` by `device`.
4. **Slicer** on `device` to filter every visual on the page.
5. **Text box** with the finding: small orders hit with a late shipping fee abandon at a much higher rate, so showing shipping cost earlier is a quick fix.
