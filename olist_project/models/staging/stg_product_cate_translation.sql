with cate_translation_src as (
    select
        product_category_name,
        product_category_name_english
    
    from {{source('olist_raw', 'RAW_PRODUCT_CATEGORY_TRANSLATION')}}
)

select
    lower(trim(product_category_name)) as category_name,
    lower(trim(product_category_name_english)) as category_name_english

from cate_translation_src