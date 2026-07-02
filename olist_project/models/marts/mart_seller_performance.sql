with order_items as (
    select
        order_id,
        seller_id,
        price,
        freight_value

    from {{ref('int_order_items_enriched')}}
),

orders as (
    select 
        order_id,
    
    from {{ref('fct_orders')}}
    where order_status = 'delivered'
),

sellers as (
    select  
        seller_id,
        city,
        state
    
    from {{ref('int_sellers_enriched')}}
)

select  
    oi.seller_id,
    s.city,
    s.state,

    count(distinct oi.order_id) as total_orders,
    count(*) as total_items_sold,

    sum(oi.price) as seller_revenue,
    sum(oi.freight_value) as total_shipping_cost,
    sum(oi.price) + sum(oi.freight_value) as gross_order_value,

    avg(oi.price) as avg_item_price

from order_items oi
join orders o 
    on oi.order_id = o.order_id
left join sellers s
    on oi.seller_id = s.seller_id

group by
    oi.seller_id,
    s.city,
    s.state




