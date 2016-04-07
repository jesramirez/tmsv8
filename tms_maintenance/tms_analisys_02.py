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

class tms_analisys_02(osv.Model):
    _name = 'tms.analisys.02'
    _description = "MRO Tasks Analisys"
    _auto = False
    _description = 'Order Maintenace Analisys 2'

########################### Columnas : Atributos #######################################################################
    _columns = {
        
        'date_order'    : fields.datetime('Date Order', readonly=True),
        'order_id'      : fields.many2one('tms.maintenance.order','Order', readonly=True),
        'name'          : fields.many2one('tms.maintenance.order.activity','Task', readonly=True),
        'product_id'    : fields.many2one('product.product','Task', readonly=True),
        'product_category_id' : fields.many2one('product.category','Product Category', readonly=True),
        'date'          : fields.datetime('Date', readonly=True),
        'year'           : fields.char('Year', size=4, readonly=True),
        'day'            : fields.char('Day', size=128, readonly=True),
        'month'          : fields.selection([('01',_('January')), ('02',_('February')), ('03',_('March')), ('04',_('April')),
                                        ('05',_('May')), ('06',_('June')), ('07',_('July')), ('08',_('August')), ('09',_('September')),
                                        ('10',_('October')), ('11',_('November')), ('12',_('December'))], 'Month',readonly=True),        
        'duration'      : fields.float('Duration', readonly=True),
        'date_start'    : fields.datetime('Date Start', readonly=True),
        'date_end'      : fields.datetime('Date End', readonly=True),
        'external_workshop':   fields.boolean('External', readonly=True),
        'invoice_id'    : fields.many2one('account.invoice','Invoice Record', readonly=True),
        'supplier_invoice_number': fields.char('Invoice Number', readonly=True),
        'unit_id'       : fields.many2one('fleet.vehicle','Vehicle', readonly=True),
        'driver_id'     : fields.many2one('hr.employee','Driver', readonly=True),
        'supplier_id'   : fields.many2one('res.partner','Supplier', readonly=True, required=False),
        'spare_parts'   : fields.float('Spare Parts', readonly=True),
        'manpower'      : fields.float('Manpower', readonly=True),
        'spare_parts_external'   : fields.float('Spare Parts External', readonly=True),
        'manpower_external' : fields.float('Manpower External', readonly=True),
    }
    
########################### Metodos ####################################################################################

    def init(self, cr):
        sql.drop_view_if_exists(cr,'tms_analisys_02')
        cr.execute("""
            create or replace view tms_analisys_02 as (

select a.id, o.date as date_order, o.id as order_id, a.id as name, a.product_id, e.categ_id as product_category_id,
a.date_start as date,
to_char(date_trunc('day',a.date_start), 'YYYY') as year,
to_char(date_trunc('day',a.date_start), 'MM') as month,
to_char(date_trunc('day',a.date_start), 'YYYY-MM-DD') as day,
a.hours_real as duration, a.date_start_real as date_start, a.date_end_real as date_end, 
a.external_workshop, a.invoice_id, c.supplier_invoice_number,
o.unit_id, o.driver_id, a.supplier_id,
a.parts_cost as spare_parts,
a.cost_service as manpower,
a.parts_cost_external as spare_parts_external,
a.cost_service_external as manpower_external
from tms_maintenance_order_activity a
left join tms_maintenance_order as o on o.id=a.maintenance_order_id and o.state='done'
left join account_invoice as c on c.id=a.invoice_id and c.state <> 'cancel'
left join product_product d on d.id=a.product_id
left join product_template e on e.id=d.product_tmpl_id
where a.state = 'done'
order by o.date, a.date_start_real
                
            )
        """)
    
tms_analisys_02()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
