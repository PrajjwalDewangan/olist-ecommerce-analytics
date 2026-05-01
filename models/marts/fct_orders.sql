with orders as (
    select
        order_id,
        customer_id,
        order_status,
        approved_at,
        purchased_at,
        delivered_customer_at,
        total_items,
        total_product_value,
        total_freight_value,
        total_order_value
        
    from {{ref('int_orders_enriched')}}
),
payments as (
    select
        order_id,
        total_payment

    from {{ref('int_payments_agg')}}
)

select
    o.order_id,
    o.customer_id,
    o.order_status,
    o.approved_at,
    o.purchased_at,
    o.delivered_customer_at,
    
    case
        when o.delivered_customer_at is not null
        then  datediff(day, o.purchased_at, o.delivered_customer_at)
    end as delivery_time_days,
    
    datediff(day, o.purchased_at, o.approved_at) as approval_delay_days,

    o.total_items,
    o.total_product_value,
    o.total_freight_value,
    o.total_order_value,
    coalesce(p.total_payment, 0) as total_payment,
    o.total_order_value - coalesce(p.total_payment, 0) as payment_diff,
    case
        when abs(o.total_order_value - coalesce(p.total_payment, 0)) > 0.01 then 1
        else 0
    end as is_payment_mismatch

from orders o 
left join payments p
    on o.order_id = p.order_id