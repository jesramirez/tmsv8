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

class tms_travel_analysis(osv.osv):
    _name = "tms.travel.analysis"
    _description = "Travel Analisys"
    _auto = False
    #_rec_name = 'name'
    _columns = {
        'office_id'   : fields.many2one('tms.office', 'Office', readonly=True),
        'name'      : fields.char('Name', size=64, readonly=True),
        'date'      : fields.date('Date', readonly=True),
        'year'      : fields.char('Year', size=4, readonly=True),
        'day'       : fields.char('Day', size=128, readonly=True),
        'month'     : fields.selection([('01',_('January')), ('02',_('February')), ('03',_('March')), ('04',_('April')),
                                        ('05',_('May')), ('06',_('June')), ('07',_('July')), ('08',_('August')), ('09',_('September')),
                                        ('10',_('October')), ('11',_('November')), ('12',_('December'))], 'Month',readonly=True),

        'state'     : fields.selection([
                                    ('draft', 'Pending'),
                                    ('progress', 'Progress'),
                                    ('done', 'Done'),
                                    ('closed', 'Closed'),
                                    ('cancel', 'Cancelled')
                                    ], 'State',readonly=True),
        'employee_id'           : fields.many2one('hr.employee', 'Driver', readonly=True),
        'framework'             : fields.char('Framework', size=64, readonly=True),
        'unit_type_id'          : fields.many2one('tms.unit.category', 'Unit Type', readonly=True),
        'unit_id'               : fields.many2one('fleet.vehicle', 'Unit', readonly=True),
        'unit_char'             : fields.char('Unidad', size=64, readonly=True),
        'trailer1_id'           : fields.many2one('fleet.vehicle', 'Trailer 1', readonly=True),
        'dolly_id'              : fields.many2one('fleet.vehicle', 'Dolly', readonly=True),
        'trailer2_id'           : fields.many2one('fleet.vehicle', 'Trailer 2', readonly=True),
        'route_id'              : fields.many2one('tms.route', 'Route', readonly=True),
        'departure'             : fields.many2one('tms.place', 'Departure', readonly=True),
        'arrival'               : fields.many2one('tms.place', 'Arrival', readonly=True),
        'waybill_id'            : fields.many2one('tms.waybill', 'Waybill', readonly=True),
        'waybill_date'          : fields.date('Date', readonly=True),
        'partner_id'            : fields.many2one('res.partner', 'Customer', readonly=True),
        'waybill_state'         : fields.selection([
                                    ('draft', 'Pending'),
                                    ('approved', 'Approved'),
                                    ('confirmed', 'Confirmed'),
                                    ('cancel', 'Cancelled')
                                    ], 'Waybill State',readonly=True),

        'waybill_sequence'      : fields.many2one('ir.sequence', 'Waybill Sequence', readonly=True),
        'currency_id'           : fields.many2one('res.currency', 'Currency', readonly=True),
        'waybill_type'          : fields.selection([
                                    ('self', 'Self'),
                                    ('outsourced', 'Outsourced'),
                                    ], 'Waybill Type', readonly=True),
        'invoice_id'            : fields.many2one('account.invoice', 'Invoice', readonly=True),
        'invoice_name'          : fields.char('Invoice Name',   size=64, readonly=True),
        'user_id'               : fields.many2one('res.users', 'Salesman', readonly=True),
        'product_id'            : fields.many2one('product.product', 'Line', readonly=True),
        'amount'                : fields.float('Amount', digits_compute= dp.get_precision('Sale Price'), readonly=True),        
        'tms_category'          : fields.selection([
                                          ('freight','Freight'), 
                                          ('move','Move'), 
                                          ('insurance','Insurance'), 
                                          ('highway_tolls','Highway Tolls'), 
                                          ('other','Other'),
                                            ], "Income Category", readonly=True),

        'shipped_product_id'    : fields.many2one('product.product', 'Shipped Product', readonly=True),
        'qty'                   : fields.float('Product Qty', digits=(18,6), readonly=True),
        'operation_id'          : fields.many2one('tms.operation', 'Operation', readonly=True),


    }

#    _order = "office_id, date_order, name"

    def init(self, cr):
        sql.drop_view_if_exists(cr, 'tms_travel_analysis')
        cr.execute ("""
CREATE OR REPLACE VIEW tms_travel_analysis as
select row_number() over() as id,
a.office_id, a.name, 

a.date,
to_char(date_trunc('day',a.date), 'YYYY') as year,
to_char(date_trunc('day',a.date), 'MM') as month,
to_char(date_trunc('day',a.date), 'YYYY-MM-DD') as day,

a.state, a.employee_id, a.framework, f.unit_type_id, 
a.unit_id, f.name as unit_char, a.trailer1_id, a.dolly_id, a.trailer2_id, a.route_id, a.departure_id departure, a.arrival_id arrival,
b.id as waybill_id, b.date_order as waybill_date, 
case 
when b.partner_id is null then 1
else b.partner_id
end partner_id, 
b.state as waybill_state, b.sequence_id as waybill_sequence, b.currency_id, b.waybill_type, b.invoice_id, b.invoice_name, b.user_id,
c.product_id, 
c.price_subtotal / 
(case (select count(id) from tms_waybill_shipped_product where waybill_id=b.id)::FLOAT
when 0.0 then 1.0 
else (select count(id) from tms_waybill_shipped_product where waybill_id=b.id)::FLOAT
end) as amount,
d.tms_category, e.product_id as shipped_product_id, 
e.product_uom_qty / 
(case (select count(id) from tms_waybill_line where waybill_id=b.id)::FLOAT
when 0.0 then 1
else (select count(id) from tms_waybill_line where waybill_id=b.id)::FLOAT
end) as qty,
a.operation_id
from tms_travel a
	left join tms_waybill b on (a.id = b.travel_id and b.state in ('approved', 'confirmed'))	
	left join tms_waybill_line c on (c.waybill_id = b.id and c.line_type = 'product')
	left join product_product d on (c.product_id = d.id)
	left join tms_waybill_shipped_product e on (e.waybill_id = b.id)
	left join fleet_vehicle f on (a.unit_id = f.id)
order by a.office_id, a.name, a.date;
        """)



## Vista para ver la disponibilidad de unidades
class tms_travel_availability(osv.osv):
    _name = "tms.travel.availability"
    _description = "Unit availability for Travel"
    _auto = False
    _rec_name = 'name'
    _columns = {
        'name'                  : fields.many2one('fleet.vehicle', 'Unit', readonly=True),
        'supplier_unit'         : fields.boolean('Supplier Unit', readonly=True),
        'fleet_type'            : fields.selection([('tractor','Motorized Unit'), ('trailer','Trailer'), ('dolly','Dolly'), ('other','Other')], 'Unit Fleet Type', readonly=True),
        'office_id'               : fields.many2one('tms.office', 'Office', readonly=True),
        'travel_id'             : fields.many2one('tms.travel', 'Travel', readonly=True),
        'trailer1_id'           : fields.many2one('fleet.vehicle', 'Trailer 1', readonly=True),
        'dolly_id'              : fields.many2one('fleet.vehicle', 'Dolly', readonly=True),
        'trailer2_id'           : fields.many2one('fleet.vehicle', 'Trailer 2', readonly=True),
        'employee_id'           : fields.many2one('hr.employee', 'Driver', readonly=True),

        'date'                  : fields.date('Travel Date', readonly=True),
        'date_start'            : fields.date('Date Start', readonly=True),
        'date_end'              : fields.date('Date End', readonly=True),

        'state'                 : fields.selection([                                   
                                    ('draft', 'Pending'),
                                    ('progress', 'Progress'),
                                    ('free', 'Free'),
                                    ], 'State',readonly=True),


        'framework'             : fields.char('Framework', size=64, readonly=True),
        'unit_type_id'          : fields.many2one('tms.unit.category', 'Unit Type', readonly=True),
        'route_id'              : fields.many2one('tms.route', 'Route', readonly=True),
        'departure'             : fields.many2one('tms.place', 'Departure', readonly=True),
        'arrival'               : fields.many2one('tms.place', 'Arrival', readonly=True),
        'waybill_id'            : fields.many2one('tms.waybill', 'Waybill', readonly=True),
        'waybill_date'          : fields.date('Waybill Date', readonly=True),
        'partner_id'            : fields.many2one('res.partner', 'Customer', readonly=True),
        'user_id'               : fields.many2one('res.users', 'Salesman', readonly=True),

    }

    _order = "name, date, office_id"

    def init(self, cr):
        sql.drop_view_if_exists(cr, 'tms_travel_availability')
        cr.execute ("""
CREATE OR REPLACE VIEW tms_travel_availability as
select row_number() over() as id,
a.id as name, a.supplier_unit, a.fleet_type,
b.office_id, b.id travel_id, b.trailer1_id, b.dolly_id, b.trailer2_id, b.employee_id,
case when b.date is null then current_date else b.date end date, b.date_start, b.date_end, 
case  when b.state is null then 'free' else b.state end state,
b.framework,
a.unit_type_id, b.route_id, b.departure_id departure, b.arrival_id arrival,
c.id waybill_id,
c.date_order waybill_date,
c.partner_id,
b.user_id
from fleet_vehicle a
	left join tms_travel b on a.id = b.unit_id and b.state in ('draft','progress')
	left join tms_waybill c on c.travel_id = b.id and c.state <> 'cancelled'

order by  a.name, b.date, a.office_id
;
        """)

tms_travel_availability()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
