with orders as (

    select
        order_id,
        purchased_at,
        delivery_time_days,
        total_payment

    from {{ ref('fct_orders') }}
    where order_status = 'delivered'

),

reviews as (

    select
        order_id,
        score as review_score

    from {{ ref('int_reviews_enriched') }}

)

select
    o.order_id,
    date_trunc('month', o.purchased_at) as order_month,
    o.delivery_time_days,
    o.total_payment,
    r.review_score

from orders o
left join reviews r
    on o.order_id = r.order_id
