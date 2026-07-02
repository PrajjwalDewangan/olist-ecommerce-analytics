with sellers_src as (
    select 
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state
    
    from {{source('olist_raw', 'RAW_SELLERS')}}
)

select
    seller_id,
    seller_zip_code_prefix as zip_code,
    trim(lower(translate(seller_city, 'áàãâäéèêëíìîïóòõôöúùûüç', 'aaaaaeeeeiiiiooooouuuuc'))) as city,
    trim(upper(seller_state)) as state

from sellers_src