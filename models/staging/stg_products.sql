with products_src as (
    select
        product_id,
        product_category_name,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm,
    
    from {{source('olist_raw', 'RAW_PRODUCTS')}}
)

select
    product_id,
    trim(lower(product_category_name)) as category_name,
    product_photos_qty::int as photo_qty,
    product_weight_g as product_weight,
    product_height_cm as product_height,
    product_width_cm as product_width

from products_src
