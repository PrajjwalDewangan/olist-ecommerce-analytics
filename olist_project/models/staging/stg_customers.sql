with src_customer as (
    select
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
    
    from {{source('olist_raw', 'RAW_CUSTOMERS')}}
)

select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix as zip_code,
    lower(trim(customer_city)) as customer_city,
    upper(trim(customer_state)) as customer_state

from src_customer