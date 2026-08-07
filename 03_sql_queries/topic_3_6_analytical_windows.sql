SELECT 
    payment_value,
    LAG(payment_value, 1) OVER (ORDER BY payment_value DESC) AS prev_payment,
    -- Calculate difference between current and previous payment
    payment_value - LAG(payment_value, 1) OVER (ORDER BY payment_value DESC) AS value_difference,
    AVG(payment_value) OVER (ORDER BY order_id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3_orders,
    SUM(payment_value) OVER (ORDER BY order_id) AS running_total_payments
FROM olist_ecommerce.order_payments;


