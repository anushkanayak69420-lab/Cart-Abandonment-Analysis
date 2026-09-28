-- Cart Abandonment Analysis: SQL queries
-- Table: checkout_sessions (one row per customer session)
-- Key columns: device, cart_value_inr, shipping_cost_inr, last_stage_reached, abandoned (1 = left, 0 = bought)


-- Query 1: Where do sessions stop in the checkout?
SELECT last_stage_reached,
       COUNT(*) AS sessions
FROM checkout_sessions
GROUP BY last_stage_reached
ORDER BY sessions DESC;


-- Query 2: Overall abandonment rate (only sessions that added something to the cart)
-- abandoned is 0 or 1, so the average of it IS the abandonment rate
SELECT COUNT(*) AS sessions,
       ROUND(AVG(abandoned) * 100, 1) AS abandonment_rate_pct
FROM checkout_sessions
WHERE last_stage_reached <> 'product_view';


-- Query 3: THE KEY INSIGHT. Do late shipping fees on small orders cause more abandonment?
-- "Shipping shock" = small cart (under Rs 800) that still got charged a shipping fee
SELECT CASE WHEN shipping_cost_inr > 0 AND cart_value_inr < 800
            THEN 'Shipping shock'
            ELSE 'No shock' END AS order_group,
       COUNT(*) AS sessions,
       ROUND(AVG(abandoned) * 100, 1) AS abandonment_rate_pct
FROM checkout_sessions
WHERE last_stage_reached <> 'product_view'
GROUP BY order_group;


-- Query 4: How much revenue is lost in each group?
SELECT CASE WHEN shipping_cost_inr > 0 AND cart_value_inr < 800
            THEN 'Shipping shock'
            ELSE 'No shock' END AS order_group,
       SUM(cart_value_inr) AS revenue_lost_inr
FROM checkout_sessions
WHERE last_stage_reached <> 'product_view'
  AND abandoned = 1
GROUP BY order_group;


-- Query 5: Does the pattern hold on every device?
SELECT device,
       CASE WHEN shipping_cost_inr > 0 AND cart_value_inr < 800
            THEN 'Shipping shock'
            ELSE 'No shock' END AS order_group,
       ROUND(AVG(abandoned) * 100, 1) AS abandonment_rate_pct
FROM checkout_sessions
WHERE last_stage_reached <> 'product_view'
GROUP BY device, order_group
ORDER BY device, order_group;
