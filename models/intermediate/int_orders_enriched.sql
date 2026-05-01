with orders as (
    select
        order_id,
        customer_id,
        approved_at,
        purchased_at,
        delivered_customer_at,
        order_status

    from {{ref('stg_orders')}}
),

order_items as (
    select
        order_id,
        price,
        freight_value

    from {{ref('stg_order_items')}}
),

order_items_agg as (
    select 
        order_id,
        count(*) as total_items,
        sum(price) as total_product_value,
        sum(freight_value) as total_freight_value,
        sum(price) + sum(freight_value) as total_order_value
    from order_items
    group by order_id
)

select 
    o.order_id, 
    o.customer_id, 
    o.approved_at,
    o.purchased_at,
    o.delivered_customer_at, 
    o.order_status,
    coalesce(oi.total_items, 0) as total_items, 
    coalesce(oi.total_product_value, 0) as total_product_value,
    coalesce(oi.total_freight_value, 0) as total_freight_value,
    coalesce(oi.total_order_value, 0) as total_order_value
    
from orders o 
left join order_items_agg oi 
    on o.order_id = oi.order_id
