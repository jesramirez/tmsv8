select 
	(select p.name_template  from product_product as p where p.id = activity.product_id) as activity_name,
	(activity.id                                                                       ) as activity_id,
	(activity.id                                                                       ) as id,
	
	activity.date_start_real                                                             as date_begin,
	activity.date_end_real                                                               as date_end,
	activity.hours_real                                                                  as hours,

	activity.cost_service                                                                as cost_manpower,
	activity.parts_cost                                                                  as cost_material,
	
	o.name                                                                               as order_name,
	o.id                                                                                 as order_id

                                                                  
from tms_maintenance_order_activity as activity, tms_maintenance_order as o
where activity.state like 'done' and activity.maintenance_order_id = o.id and o.state like 'done'
order by maintenance_order_id



select *                                                                      
from tms_maintenance_order_activity as activity
where activity.state like 'done'
order by maintenance_order_id

