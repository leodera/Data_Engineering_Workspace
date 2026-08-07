with avg_payment_fixture as (
    select AVG(payment_value) as overall_avg
    from olist_ecommerce.order_payments 
),
weighted_average as (
    select 
        3*overall_avg as tripled_avg
    from avg_payment_fixture 
)
select 
    p.payment_type,
    p.order_id,
    p.payment_value,
    wa.tripled_avg
from 
    olist_ecommerce.order_payments p 
cross join 
    weighted_average  as wa 
where 
    p.payment_value > wa.tripled_avg  
order 
    by p.payment_value desc 
limit 
    10;

