with orders as (
    select 
        order_id,
        order_status
    
    from {{ref('fct_orders')}}
),

funnel as (
    select 'created' as stage, count(*) as total_orders
    from orders

    union all

    select 'approved', count(*)
    from orders
    where order_status in ('approved', 'processing', 'shipped', 'delivered')

    union all

    select 'shipped', count(*)
    from orders
    where order_status in ('shipped', 'delivered')

    union all

    select 'delivered', count(*)
    from orders
    where order_status = 'delivered'
),

drop_offs as (
    select
        order_status as stage,
        count(*) as total_orders
    from orders
    where order_status in ('canceled', 'unavailable')
    group by order_status
),

final as (
    select * from funnel

    union all

    select * from drop_offs
)

select 
    stage,
    total_orders,
    total_orders * 1.0 / max(case when stage = 'created' then total_orders end) over () as conversion_from_start,
    case
        when stage in ('canceled', 'unavailable') then 'drop_off'
        else 'progression'
    end as stage_type

from final