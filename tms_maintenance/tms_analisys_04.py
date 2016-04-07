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

class tms_analisys_04(osv.Model):
    _name = 'tms.analisys.04'
    _description = "Order Analisys Tms"
    _rec_name='activity_name'
    _auto = False
    _description = 'Order Maintenace Analisys 4'

########################### Columnas : Atributos #######################################################################
    _columns = {
        ######## Integer ###########
        'id':                  fields.integer('Kiosk ID'),

        ######## Char ###########
        'order_name':          fields.char('Order Name'),
        'activity_name':       fields.char('Activity Name'),
        'hr_employee_name':    fields.char('Employee Name'),
        'unit_name':           fields.char('Unit Name'),

        ######## Float ###########
        'hours_work':          fields.float('Hours Work'),

        ######## Date ###########
        'date_begin':          fields.datetime('Date Begin'),
        'date_end':            fields.datetime('Date End'),

        ######## Many2One ###########
        'order_id':            fields.many2one('tms.maintenance.order','Order ID'),
        'activity_id':         fields.many2one('tms.maintenance.order.activity','Activity ID'),
        'hr_employee_id':      fields.many2one('hr.employee','Mechanic'),
        'unit_id':     fields.many2one('fleet.vehicle','Unit'),
        'driver_id':   fields.many2one('hr.employee','Driver'),
    }
    
########################### Metodos ####################################################################################

    def init(self, cr):
        sql.drop_view_if_exists(cr,'tms_analisys_04')
        cr.execute("""
            create or replace view tms_analisys_04 as (

select  
	(control.id)             as id,                          
	(control.id)             as kiosk_id,

	(control.order_id)       as order_id,
	(control.name_order)     as order_name,
	
	(control.activity_id)    as activity_id,
	(control.name_activity)  as activity_name,
	
	(hr_employee_id)                                                                  as hr_employee_id,
	(select e.name_related from hr_employee as e where e.id = control.hr_employee_id) as hr_employee_name,

    (select u.id            from fleet_vehicle as u where u.id=o.unit_id)                as unit_id,
    (select u.name          from fleet_vehicle as u where u.id=o.unit_id)                as unit_name,

    (select e.id            from hr_employee   as e where e.id=o.driver_id)              as driver_id,
    (select e.name_related  from hr_employee   as e where e.id=o.driver_id)              as driver_name,

	(control.date_begin)     as date_begin,  
	(control.date_end)       as date_end,
	(control.hours_mechanic) as hours_work
	
from tms_activity_control_time as control, tms_maintenance_order as o
where control.state like 'end' and o.state like 'done' and o.id = control.order_id
order by control.id  
                
            )
        """)
    
tms_analisys_04()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
