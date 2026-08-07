-- Stacking two distinct customer segments vertically
SELECT order_id, 'High Value' AS segment
FROM olist_ecommerce.order_payments
WHERE payment_value > 1000

UNION ALL

SELECT order_id, 'Frequent Buyer' AS segment
FROM olist_ecommerce.order_payments
WHERE payment_value BETWEEN 100 AND 500;



with setoperations as (
    select 
        order_id, 
        payment_value, 
        payment_type
    from 
        olist_ecommerce.order_payments 
    where 
        payment_type = 'voucher'
        
    union all 
    
    select 
        order_id, 
        payment_value, 
        payment_type 
    from 
        olist_ecommerce.order_payments 
    where 
        payment_type = 'debit_card' 
)
select 
    * 
from 
    setoperations 
order by 
    payment_value desc
limit 
    10;