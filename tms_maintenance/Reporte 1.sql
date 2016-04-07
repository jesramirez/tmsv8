select id as id, name as name, date as date,
       user_id as user_id,     (select u.login         from res_users     as u where u.id=o.user_id)   as user_name,
       unit_id as unit_id,     (select u.name          from fleet_vehicle as u where u.id=o.unit_id)   as unit_name,
       driver_id as driver_id, (select e.name_related  from hr_employee   as e where e.id=o.driver_id) as driver_name,
       date_start_real as date_start,
       date_end_real   as date_end,
       cost_service as manpower_cost,
       parts_cost   as material_cost
from tms_maintenance_order as o
where o.state like 'done'
order by o.id
