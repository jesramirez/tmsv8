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
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


# Extra data fields for Waybills & Negotiations
class fleet_vehicle_category(osv.osv):
    _name = "tms.unit.category"
    _inherit = "tms.unit.category"
    _columns = {        
        'agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
#        'axis_number': fields.integer('Axis number maximum', required=True),

    }

fleet_vehicle_category()

# Definicion del Viaje de Ida
class tms_travel(osv.osv):
    _name = "tms.travel"
    _inherit = "tms.travel"
    _columns = {        
		'departure': fields.boolean('Departure'),
		'departure_2': fields.boolean('Departure'),
		'arrival': fields.boolean('Arrival'),
		'arrival_2': fields.boolean('Arrival'),
		}
tms_travel()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
