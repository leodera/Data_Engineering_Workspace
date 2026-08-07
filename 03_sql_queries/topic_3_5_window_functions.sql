with rankedpayment as (
   select 
       order_id, 
       payment_type, 
       payment_value, 
       row_number() over(partition by payment_type order by payment_value desc) as row_num,
       rank() over (partition by payment_type order by payment_value desc ) as rk,
       dense_rank() over (partition by payment_type order by payment_value desc) as dense_rk 
   from 
       olist_ecommerce.order_payments
)
select 
    *
from 
    rankedpayment 
where payment_type = 'credit_card' and dense_rk <= 5; 
