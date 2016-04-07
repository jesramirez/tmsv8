select  
	(control.id)             as id,                          
	(control.id)             as kiosk_id,

	(control.order_id)       as order_id,
	(control.name_order)     as order_name,
	
	(control.activity_id)    as activity_id,
	(control.name_activity)  as activity_name,
	
	(hr_employee_id)                                                                  as hr_employee_id,
	(select e.name_related from hr_employee as e where e.id = control.hr_employee_id) as hr_employee_name,

	(control.date_begin)     as date_begin,  
	(control.date_end)       as date_end,
	(control.hours_mechanic) as hours_work
	
from tms_activity_control_time as control, tms_maintenance_order as o
where control.state like 'end' and o.state like 'done' and o.id = control.order_id
order by control.id

select *
from tms_activity_control_time as control
where control.state like 'end'



select 
	pl.id                                                                       as id,
	pl.id                                                                       as product_line_id, 
	
	(select p.name_template from product_product as p where p.id=pl.product_id) as product_name,
	(select p.id from product_product as p where p.id=pl.product_id)            as product_id,
	
	pl.quantity                                                                 as quantity,
	pl.list_price                                                               as price,
	(pl.quantity*pl.list_price)                                                 as total_price,

	(select p.name_template  from product_product as p where p.id = activity.product_id) as activity_name,
	(activity.id                                                                       ) as activity_id,
	
	o.name                                                                               as order_name,
	o.id                                                                                 as order_id
	
from tms_product_line as pl, tms_maintenance_order_activity as activity, tms_maintenance_order as o
where pl.state like 'delivered' and pl.activity_id = activity.id and o.id = activity.maintenance_order_id    