with order_items as (
    select
        order_id,
        price,
        freight_value,
        product_category
    
    from {{ref('int_order_items_enriched')}}
),

orders as (
    select
        order_id,
        order_status
    
    from {{ref('fct_orders')}}
),

reviews as (
    select *
    from {{ref('int_reviews_enriched')}}

),

joined as (
    select
        oi.product_category,
        oi.order_id,
        oi.price,
        oi.freight_value,
        r.score,

    from order_items oi
    left join orders o
        on oi.order_id = o.order_id
    left join reviews r
        on oi.order_id = r.order_id
    where o.order_status = 'delivered'
)

select
    product_category,
    sum(price) as total_product_revenue,
    sum(freight_value) as total_freight_value,
    sum(price) + sum(freight_value) as total_revenue,
    count(distinct(order_id)) as total_orders,
    count(*) as total_items,
    avg(price) as avg_item_price,
    avg(score) as avg_review_score,
    rank() over (
        order by total_revenue desc
    ) as revenue_rank

from joined
group by product_category