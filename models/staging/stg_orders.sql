with src_orders as (
    select 
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date
        
    from {{ source('olist_raw', 'RAW_ORDERS')}}
)

select 
    order_id,
    customer_id,
    lower(trim(order_status)) as order_status,
    order_purchase_timestamp::timestamp as purchased_at,
    order_approved_at::timestamp as approved_at,
    order_delivered_carrier_date::timestamp as delivered_carrier_at,
    order_delivered_customer_date::timestamp as delivered_customer_at,
    order_estimated_delivery_date::date as estimated_delivery_date

from src_orders