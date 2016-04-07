# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp.osv import fields,osv
from openerp.tools import sql
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tms_analisys_03(osv.Model):
    _name = 'tms.analisys.03'
    _description = "Order Analisys Tms"
    _auto = False
    _description = 'Order Maintenace Analisys 3'

########################### Columnas : Atributos #######################################################################
    _columns = {
        'name'          : fields.many2one('tms.product.line','Product', readonly=True),
        'date'          : fields.datetime('Date', readonly=True),
        'year'          : fields.char('Year', size=4, readonly=True),
        'day'           : fields.char('Day', size=128, readonly=True),
        'month'         : fields.selection([('01',_('January')), ('02',_('February')), ('03',_('March')), ('04',_('April')),
                                        ('05',_('May')), ('06',_('June')), ('07',_('July')), ('08',_('August')), ('09',_('September')),
                                        ('10',_('October')), ('11',_('November')), ('12',_('December'))], 'Month',readonly=True),        

        'date_order'    : fields.datetime('Date Order', readonly=True),
        'order_id'      : fields.many2one('tms.maintenance.order','Order', readonly=True),
        'task_id'       : fields.many2one('tms.maintenance.order.activity','Task', readonly=True),
        'date_start'    : fields.datetime('Task Date Start', readonly=True),
        'product_id'    : fields.many2one('product.product','Spare Part', readonly=True),
        'product_category_id' : fields.many2one('product.category','Spare Part Category', readonly=True),

        'external_workshop': fields.boolean('External', readonly=True),
        
        
        'unit_id'       : fields.many2one('fleet.vehicle','Vehicle', readonly=True),
        'driver_id'     : fields.many2one('hr.employee','Driver', readonly=True),
        'supplier_id'   : fields.many2one('hr.employee','Supplier', readonly=True),
        'qty'           : fields.float('Qty', readonly=True),
        'product_uom'   : fields.many2one('product.uom','UoM', readonly=True),
        'list_price'    : fields.float('Std Price', readonly=True),
        'amount'        : fields.float('Amount', readonly=True),
    }
    
########################### Metodos ####################################################################################

    def init(self, cr):
        sql.drop_view_if_exists(cr,'tms_analisys_03')
        cr.execute("""
            create or replace view tms_analisys_03 as (

select sm.id, pl.id as name, sm.date, o.date as date_order, o.id as order_id, 
task.id as task_id, task.date_start,
sm.product_id, prod_tmpl.categ_id as product_category_id,
to_char(date_trunc('day',sm.date), 'YYYY') as year,
to_char(date_trunc('day',sm.date), 'MM') as month,
to_char(date_trunc('day',sm.date), 'DD') as day,
task.external_workshop, 
sm.unit_id, o.driver_id, task.supplier_id,
sm.product_qty qty,
sm.product_uom,
case when aml.debit > 0 then aml.debit / sm.product_qty else pl.list_price end as list_price,
case when aml.debit > 0 then aml.debit else pl.quantity * pl.list_price end as amount

from stock_move sm
	left join tms_product_line pl on pl.stock_move_id=sm.id and pl.state = 'delivered'
    left join account_move_line aml on aml.stock_move_id=sm.id and aml.state='valid' and aml.debit > 0
	left join account_move am on aml.move_id=am.id
		
	left join tms_maintenance_order_activity task on task.id=sm.activity_id --and task.state='done'
	left join tms_maintenance_order as o on o.id=sm.maintenance_order_id --and o.state='done'
	left join product_product prod on prod.id=sm.product_id
	left join product_template prod_tmpl on prod_tmpl.id=prod.product_tmpl_id

where sm.state='done' and sm.picking_id is not null
and sm.unit_id is not null --and sm.driver_id is not null
and (
	sm.location_dest_id in (select id from stock_location where usage in ('production', 'inventory'))
	or
	sm.location_id in (select id from stock_location where usage in ('production', 'inventory'))
	)
order by sm.date
);
        """)
        
        
"""
        
update tms_maintenance_order_activity a
set state=(
case when (select count(b.id) from tms_product_line b where a.id=b.activity_id and state='delivered') > 0 then 'done' else a.state end
);


update tms_product_line pl
set list_price=(
select sum(case when aml.debit > 0 then aml.debit else pl.quantity * pl.list_price end)
from stock_move sm 
	left join account_move am on sm.am_id=am.id
		left join account_move_line aml on am.id=aml.move_id and aml.state='valid' and aml.debit > 0
where sm.id=pl.stock_move_id and sm.state='done'
);


update tms_maintenance_order_activity a
set parts_cost=(
select sum(case when aml.debit > 0 then aml.debit else pl.quantity * pl.list_price end)
from tms_product_line pl 
	left join stock_move sm on sm.id=pl.stock_move_id and sm.state='done'
		left join account_move am on sm.am_id=am.id
			left join account_move_line aml on am.id=aml.move_id and aml.state='valid' and aml.debit > 0
where pl.activity_id=a.id)
where external_workshop = False;

update tms_maintenance_order_activity set cost_service=0 where external_workshop;

update tms_maintenance_order o
set 
spare_parts = (select sum(parts_cost) from tms_maintenance_order_activity a where a.maintenance_order_id = o.id and a.state<>'cancel'),
manpower = (select sum(cost_service) from tms_maintenance_order_activity a where a.maintenance_order_id = o.id and a.state<>'cancel' and not a.external_workshop),
spare_parts_external = (select sum(parts_cost_external) from tms_maintenance_order_activity a where a.maintenance_order_id = o.id and a.state<>'cancel'),
manpower_external = (select sum(cost_service_external) from tms_maintenance_order_activity a where a.maintenance_order_id = o.id and a.state<>'cancel' and a.external_workshop)
where o.state <> 'cancel';


"""
    
tms_analisys_03()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
