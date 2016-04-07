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
from openerp.tools.translate import _
from openerp.tools import sql
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tms_analisys_01(osv.osv):
    _name = 'tms.analisys.01'
    _description = "Order Analisys Tms"
    _auto = False
    _description = 'Order Maintenace Analisys 1, Order'

########################### Columnas : Atributos #######################################################################
    _columns = {
        'name'           : fields.many2one('tms.maintenance.order','Service Order'),
        'date'           : fields.date('Date', readonly=True),
        'year'           : fields.char('Year', size=4, readonly=True),
        'day'            : fields.char('Day', size=128, readonly=True),
        'month'          : fields.selection([('01',_('January')), ('02',_('February')), ('03',_('March')), ('04',_('April')),
                                        ('05',_('May')), ('06',_('June')), ('07',_('July')), ('08',_('August')), ('09',_('September')),
                                        ('10',_('October')), ('11',_('November')), ('12',_('December'))], 'Month',readonly=True),
        'date_start_real': fields.datetime('Date Start'),
        'date_end_real'  : fields.datetime('Date End'),
        'duration_real'  : fields.float('Duration', digits_compute=dp.get_precision('Account')),
        'product_id'     : fields.many2one('product.product','Service'),
        'supervisor_id'  : fields.many2one('hr.employee','Supervisor'),
        'unit_id'        : fields.many2one('fleet.vehicle','Vehicle'),
        'driver_id'      : fields.many2one('hr.employee','Driver'),
        'maint_cycle_id' : fields.many2one('product.product','Maint. Cycle'),
        'user_id'        : fields.many2one('res.users','User'),
        'notes'          : fields.text('Notes'),

        'parts_cost'     : fields.float('Spare Parts', digits_compute=dp.get_precision('Account')),
        'cost_service'   : fields.float('Manpower Cost', digits_compute=dp.get_precision('Account')),
        'parts_cost_external': fields.float('External Spare Parts', digits_compute=dp.get_precision('Account')),
        'cost_service_external': fields.float('External Manpower Cost', digits_compute=dp.get_precision('Account')),
        
        
    }
    
########################### Metodos ####################################################################################

    def init(self, cr):
        sql.drop_view_if_exists(cr,'tms_analisys_01')
        cr.execute("""

create or replace view tms_analisys_01 as (

select 
o.id, o.id as name, o.product_id, o.supervisor_id, o.maint_cycle_id, o.driver_id,
o.user_id, o.unit_id, o.date,
to_char(date_trunc('day',o.date), 'YYYY') as year,
to_char(date_trunc('day',o.date), 'MM') as month,
to_char(date_trunc('day',o.date), 'YYYY-MM-DD') as day,
o.date_start_real, o.date_end_real,
o.duration_real, o.notes,
sum(a.parts_cost) as parts_cost,
sum(a.cost_service) as cost_service,
sum(a.parts_cost_external) as parts_cost_external,
sum(a.cost_service_external) as cost_service_external
from tms_maintenance_order as o
left join tms_maintenance_order_activity a on o.id=a.maintenance_order_id and a.state='done'
where o.state = 'done'
group by o.id, o.product_id, o.supervisor_id, o.maint_cycle_id, o.driver_id,
o.user_id, o.unit_id, o.name, o.date, o.date_start_real, o.date_end_real,
o.duration_real, o.notes
order by o.date
);
  
        """)
    
tms_analisys_01()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
