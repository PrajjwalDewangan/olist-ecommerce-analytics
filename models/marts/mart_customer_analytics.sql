with orders as (
    select 
        customer_id,
        order_id,
        total_items,
        total_product_value,
        total_order_value,
        is_payment_mismatch
    
    from {{ref('fct_orders')}}
    where order_status = 'delivered'
),

customers as (
    select 
        customer_id,
        customer_city,
        customer_state
    
    from {{ref('int_customers_enriched')}}
),

reviews as (
    select 
        order_id,
        score
    
    from {{ref('int_reviews_enriched')}}
)

select
    o.customer_id,
    c.customer_city,
    c.customer_state,
    
    count(distinct(o.order_id)) as total_orders,

    sum(o.total_order_value) as total_spends,
    avg(o.total_order_value) as avg_order_value,

    sum(o.is_payment_mismatch) as total_mismatched_orders,

    avg(r.score) as avg_review_score,

    case 
        when total_spends >= 10000 then 'high_value'
        when total_spends >= 5000 and total_spends < 10000 then 'mid_value'
        else 'low_value'
    end as customer_segment

from orders o
left join customers c
    on o.customer_id = c.customer_id
left join reviews r 
    on o.order_id = r.order_id

group by
    o.customer_id,
    c.customer_city,
    c.customer_state
