select
    order_id,
    score

from {{ref('stg_order_reviews')}}