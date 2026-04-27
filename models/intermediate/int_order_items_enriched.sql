with order_items as (
    select
        order_id,
        product_id,
        price,
        freight_value,

    from {{ref('stg_order_items')}}
),

products_enriched as (
    select
        product_id,
        product_category
    
    from {{ref('int_products_enriched')}}
)

select 
    oi.order_id,
    oi.product_id,
    oi.price,
    oi.freight_value,
    p.product_category

from order_items oi
left join products_enriched p
    on oi.product_id = p.product_id
