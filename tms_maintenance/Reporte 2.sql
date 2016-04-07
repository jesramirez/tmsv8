select o.id as id, name as name, date as date,
       o.user_id as user_id,     (select u.login         from res_users     as u where u.id=o.user_id)   as user_name,
       o.unit_id as unit_id,     (select u.name          from fleet_vehicle as u where u.id=o.unit_id)   as unit_name,
       o.driver_id as driver_id, (select e.name_related  from hr_employee   as e where e.id=o.driver_id) as driver_name,
       o.date_start_real as date_start,
       o.date_end_real   as date_end,
       o.cost_service as manpower_cost,
       o.parts_cost   as material_cost,
       (select p.name_template from product_product as p where a.product_id = p.id) as activity_service_product_name,
       (select p.id from product_product as p where a.product_id = p.id)            as activity_service_product_id,
       a.id                                                                         as activity_id
from tms_maintenance_order as o, tms_maintenance_order_activity as a
where o.state like 'done' and o.id=a.maintenance_order_id
order by o.id


select * from tms_maintenance_order_activity

select * from tms_maintenance_order