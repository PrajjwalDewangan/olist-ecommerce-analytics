with reviews_src as (
    select 
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date,
        review_answer_timestamp
    
    from {{source('olist_raw', 'RAW_ORDER_REVIEWS')}}

),

deduplicated_reviews as (
    select *,
        row_number() over (
            partition by review_id
            order by review_creation_date desc
        ) as rn

    from reviews_src
)
select
    review_id,
    order_id,
    review_score::int as score,
    review_comment_title as review_title,
    review_comment_message as review_message,
    review_creation_date::date as created_date,
    review_answer_timestamp::timestamp as answered_at

from deduplicated_reviews
where rn = 1