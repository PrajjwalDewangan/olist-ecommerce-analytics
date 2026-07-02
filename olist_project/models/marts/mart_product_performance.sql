with order_items as (
    select
        order_id,
        product_id,
        product_category,
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

reviews as (
    select
        order_id,
        score

    from {{ref('int_reviews_enriched')}}
)

select 
    oi.product_id,
    oi.product_category,

    sum(oi.price) as total_product_revenue,
    sum(oi.freight_value) as total_freight_value,
    sum(oi.price) + sum(oi.freight_value) as total_revenue,

    count(*) as total_products_sold,
    count(distinct(oi.order_id)) as total_orders,

    avg(oi.price) as avg_price,

    avg(r.score) as avg_review_score

from order_items oi
left join orders o
    on oi.order_id = o.order_id
left join reviews r
    on oi.order_id = r.order_id
where o.order_id is not null

group by 
    oi.product_id,
    oi.product_category
