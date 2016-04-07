# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

#
# Please note that these reports are not multi-currency !!!
#

from openerp.osv import fields,osv
from openerp.tools import sql
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tms_expense_analysis(osv.osv):
    _name = "tms.expense.analysis"
    _description = "Travel Expenses Analisys"
    _auto = False
    _rec_name = 'name'
    _columns = {
        'driver_helper'         : fields.boolean('Driver Helper'),
        'office_id'               : fields.many2one('tms.office', 'Office', readonly=True),
        'name'                  : fields.char('Name', size=64, readonly=True),
        'date'                  : fields.date('Date', readonly=True),
        'year'                  : fields.char('Year', size=4, readonly=True),
        'day'                   : fields.char('Day', size=128, readonly=True),
        'month'                 : fields.selection([('01',_('January')), ('02',_('February')), ('03',_('March')), ('04',_('April')),
                                        ('05',_('May')), ('06',_('June')), ('07',_('July')), ('08',_('August')), ('09',_('September')),
                                        ('10',_('October')), ('11',_('November')), ('12',_('December'))], 'Month',readonly=True),
        'state'                 : fields.selection([
                ('draft', 'Draft'),
                ('approved', 'Approved'),
                ('confirmed', 'Confirmed'),
                ('cancel', 'Cancelled')
                ], 'State',readonly=True),
        'employee_id'           : fields.many2one('hr.employee', 'Driver', readonly=True),
        'unit_id'               : fields.many2one('fleet.vehicle', 'Unit', readonly=True),
        'unit_char'             : fields.char('Unidad', size=64, readonly=True),
        'currency_id'           : fields.many2one('res.currency', 'Currency', readonly=True),
        'product_id'            : fields.many2one('product.product', 'Line', readonly=True),
        'expense_line_description' : fields.char('Description',   size=256, readonly=True),

#        'travel_id'             : fields.many2one('tms.travel', 'Travel', readonly=True),
#        'route_id'              : fields.many2one('tms.route', 'Route', readonly=True),
#        'waybill_income'        : fields.float('Waybill Amount', digits=(18,2), readonly=True),        

#        'travels'               : fields.integer('Travels', readonly=True),        
        'qty'                   : fields.float('Qty', digits=(18,2), readonly=True),        
        'price_unit'            : fields.float('Price Unit', digits=(18,4), readonly=True),        
        'subtotal'              : fields.float('SubTotal', digits=(18,2), readonly=True),        
        'operation_id'          : fields.many2one('tms.operation', 'Operation', readonly=True),
    }

#    _order = "office_id, date_order, name"

    def init(self, cr):
        sql.drop_view_if_exists(cr, 'tms_expense_analysis')
        cr.execute ("""

CREATE OR REPLACE VIEW tms_expense_analysis as
select b.id as id,
a.driver_helper,
a.office_id, a.name, 
a.date,
to_char(date_trunc('day',a.date), 'YYYY') as year,
to_char(date_trunc('day',a.date), 'MM') as month,
to_char(date_trunc('day',a.date), 'YYYY-MM-DD') as day,
a.state, a.employee_id, a.unit_id, fv.name as unit_char, a.currency_id, 
b.product_id, b.name expense_line_description,
b.product_uom_qty qty,
b.price_unit,
b.price_subtotal subtotal,
b.operation_id
from tms_expense a
	inner join tms_expense_line b on a.id = b.expense_id 
    left join fleet_vehicle fv on fv.id=a.unit_id
	--inner join tms_travel c on a.id = c.expense_id
	where a.state <> 'cancel'

union

select b.id as id,
a.driver_helper,
a.office_id, a.name, 
a.date,
to_char(date_trunc('day',a.date), 'YYYY') as year,
to_char(date_trunc('day',a.date), 'MM') as month,
to_char(date_trunc('day',a.date), 'YYYY-MM-DD') as day,
a.state, a.employee_id, a.unit_id, fv.name as unit_char, a.currency_id, 
b.product_id, b.name expense_line_description,
b.product_uom_qty qty,
b.price_unit,
b.price_subtotal subtotal,
b.operation_id
from tms_expense a
	inner join tms_expense_line b on a.id = b.expense_id 
    left join fleet_vehicle fv on fv.id=a.unit_id
	--inner join tms_travel c on a.id = c.expense2_id
	where a.state <> 'cancel'

order by office_id, name, date
;
        """)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
