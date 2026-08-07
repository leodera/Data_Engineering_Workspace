SELECT 
    order_id,
    -- Pivot 1: Extract credit card payments into its own column
    SUM(CASE WHEN payment_type = 'credit_card' THEN payment_value ELSE 0 END) AS credit_card_val,
    -- Pivot 2: Extract voucher payments into its own column
    SUM(CASE WHEN payment_type = 'voucher' THEN payment_value ELSE 0 END) AS voucher_val
FROM olist_ecommerce.order_payments
GROUP BY order_id;


select 
    c.customer_state,
    sum(case when o.order_status = 'delivered' then 1 else 0 end) as delivered_orders, 
    sum(case when o.order_status = 'canceled' then 1 else 0 end) as canceled_orders, 
    sum(case when o.order_status = 'shipped' then 1 else 0 end) as shipped_orders
from 
    olist_ecommerce.orders o 
inner join 
    olist_ecommerce.customers c on o.customer_id = c.customer_id 
group by 
    c.customer_state 
having 
    sum(case when o.order_status = 'delivered' then 1 else 0 end) > 3000 
order by 
    delivered_orders;
    

select 
    c.customer_state,
    count(case when o.order_status = 'delivered' then 1 end) as delivered_orders, 
    count(case when o.order_status = 'canceled' then 1 end) as canceled_orders, 
    count(case when o.order_status = 'shipped' then 1 end) as shipped_orders
from 
    olist_ecommerce.orders o 
inner join 
    olist_ecommerce.customers c on o.customer_id = c.customer_id 
group by 
    c.customer_state 
having 
    count(case when o.order_status = 'delivered' then 1 end) > 3000 
order by 
    delivered_orders;
    
