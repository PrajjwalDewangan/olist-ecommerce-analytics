with payments_agg as (
    select 
        order_id,
        sum(value) as total_payment
    from {{ref('stg_order_payments')}}
    group by order_id
)

select
    order_id,
    total_payment
from payments_agg