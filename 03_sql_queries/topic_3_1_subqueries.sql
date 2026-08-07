select 
    p.order_id,
    p.payment_type,
    p.payment_value
from olist_ecommerce.order_payments p
where p.payment_value > 3*(select  AVG(p2.payment_value) from olist_ecommerce.order_payments p2)  
order by 
    p.payment_value desc 
limit 
    10;