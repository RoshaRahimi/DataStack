SELECT
    *,
    dateDiff(minute, creation_date, wait_to_payment_date) from_creation_to_wait_to_payment,
    dateDiff(minute, wait_to_payment_date, paied_date) from_wait_to_payment_to_paid,
    dateDiff(minute, wait_to_payment_date, payment_cancelled_date) from_wait_to_paymment_to_payment_cancelled,
    dateDiff(minute, paied_date, wait_to_approve_date) from_paied_to_wait_to_approve,
    dateDiff(minute, wait_to_approve_date, rejected_date) from_wait_to_approve_ro_reject,
    dateDiff(minute, wait_to_approve_date, approved_date) from_wait_to_approve_to_approved,
    dateDiff(minute, approved_date, finalized_date) from_approved_to_finalized,
    dateDiff(minute, approved_date, cancelled_date) from_approved_to_cancelled
FROM
(select
    order_id,
    customer_id,
    toDateTime(max(if(status_id=1, orders.created_at, NULL))) as creation_date,
    toDateTime(max(if(status_id=2, orders.updated_at, NULL))) as wait_to_payment_date,
    toDateTime(max(if(status_id=3, orders.updated_at, NULL))) as paied_date,
    toDateTime(max(if(status_id=4, orders.updated_at, NULL))) as payment_cancelled_date,
    toDateTime(max(if(status_id=5, orders.updated_at, NULL))) as wait_to_approve_date,
    toDateTime(max(if(status_id=6, orders.updated_at, NULL))) as rejected_date,
    toDateTime(max(if(status_id=7, orders.updated_at, NULL))) as approved_date,
    toDateTime(max(if(status_id=8, orders.updated_at, NULL))) as cancelled_date,
    toDateTime(max(if(status_id=9, orders.updated_at, NULL))) as finalized_date
from orders
group by
    order_id, customer_id)
