with products as (
    select
        product_id,
        category_name,
        photo_qty,
        product_weight,
        product_height,
        product_width

    from {{ref('stg_products')}}
),

translation as (
    select
        category_name,
        category_name_english

    from {{ref('stg_product_cate_translation')}}
)

select
    p.product_id,
    coalesce(t.category_name_english, p.category_name) as product_category,
    p.photo_qty,
    p.product_height,
    p.product_weight,
    p.product_width

from products p 
left join translation t
    on p.category_name = t.category_name