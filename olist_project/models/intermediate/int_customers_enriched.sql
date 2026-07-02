with customers as (
    select 
        customer_id,
        customer_unique_id,
        zip_code,
        customer_city,
        customer_state
    
    from {{ref('stg_customers')}}
),

geo as (
    select 
        zip_code,
        latitude,
        longitude
    
    from {{ref('stg_geolocations')}}
)

select  
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    c.zip_code,
    g.latitude,
    g.longitude

from customers c
left join geo g
    on c.zip_code = g.zip_code