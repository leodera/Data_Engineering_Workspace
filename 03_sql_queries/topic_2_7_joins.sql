SELECT 
    c.customer_state,
    COUNT(o.order_id) AS total_orders
FROM olist_ecommerce.orders AS o
INNER JOIN olist_ecommerce.customers AS c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_state
HAVING COUNT(o.order_id) > 3000
ORDER BY total_orders DESC;


select 
    o.order_id,
    coalesce(p.payment_type, 'Not Specified') as clean_payment_type,
    p.payment_value,
    case 
    	when p.payment_value > 500 then 'High Value'
    	when p.payment_value >= 100 then 'Medium Value'
    	else 'Low value'
    end as payment_category 
from 
    olist_ecommerce.orders as o 
inner join 
    olist_ecommerce.order_payments as p on o.order_id = p.order_id 
where 
    o.order_status = 'delivered' 
limit 
    10;
    