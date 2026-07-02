with order_item_src as (
    select 
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_date,
        price,
        freight_value
    
    from {{source('olist_raw', 'RAW_ORDER_ITEMS')}}

)

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date::timestamp as shipping_limit_at,
    price::float as price,
    freight_value::float as freight_value

from order_item_src


