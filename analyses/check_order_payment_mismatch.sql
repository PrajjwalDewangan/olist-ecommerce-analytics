select
    o.order_id,
    o.total_order_value,
    p.total_payment,
    o.total_order_value - coalesce(p.total_payment, 0) as diff
from {{ref('int_orders_enriched')}} o
left join {{ref('int_payments_agg')}} p
    on o.order_id = p.order_id
where o.order_status='delivered' and abs(o.total_order_value - coalesce(p.total_payment, 0)) > 0.01