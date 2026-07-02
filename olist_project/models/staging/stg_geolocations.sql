with geolocation_src as (
    select
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state

    from {{source('olist_raw', 'RAW_GEOLOCATIONS')}}       
),

deduplicated as (
    select
        geolocation_zip_code_prefix as zip_code,
        geolocation_lat as latitude,
        geolocation_lng as longitude,
        trim(lower(translate(geolocation_city, 'áàãâäéèêëíìîïóòõôöúùûüç', 'aaaaaeeeeiiiiooooouuuuc'))) as city,
        trim(upper(geolocation_state)) as state,
        row_number() over (
            partition by geolocation_zip_code_prefix
            order by geolocation_lat
        ) as rn

    from geolocation_src
)

select 
    zip_code,
    latitude,
    longitude,
    city,
    state

from deduplicated
where rn = 1