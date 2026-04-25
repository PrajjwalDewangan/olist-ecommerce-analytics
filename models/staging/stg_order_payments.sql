with order_payments_src as (
    select
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value
    
    from {{source('olist_raw', 'RAW_ORDER_PAYMENTS')}}
)

select
    order_id,
    payment_sequential::int as payment_sequential,
    trim(lower(payment_type)) as type,
    payment_installments::int as installment,
    payment_value::float as value

from order_payments_src