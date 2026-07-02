with sellers as (
    select 
        seller_id,
        zip_code,
        city,
        state
    
    from {{ref('stg_sellers')}}
),

geo as (
    select 
        zip_code,
        latitude,
        longitude
    
    from {{ref('stg_geolocations')}}
)

select
    s.seller_id,
    s.city,
    s.state,
    s.zip_code,
    g.latitude,
    g.longitude

from sellers s
left join geo g
    on s.zip_code = g.zip_code