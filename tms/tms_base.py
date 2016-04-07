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

# Agregamos manejar una secuencia por cada tienda para controlar viajes 
class tms_office(osv.osv):
    _name = "tms.office"

    
    _columns = {
            'code': fields.char('Code',size=12,required=True, select=1),
            'name': fields.char('Name',size=64,required=True, select=1),
            'active': fields.boolean('Active'),
            'notes': fields.text('Notes'),
            'partner_id':fields.many2one('res.partner', 'Address'),
            'tms_travel_seq': fields.many2one('ir.sequence', 'Travel Sequence'),
            'tms_advance_seq': fields.many2one('ir.sequence', 'Advance Sequence'),
            'tms_travel_expenses_seq': fields.many2one('ir.sequence', 'Travel Expenses Sequence'),
            'tms_loan_seq': fields.many2one('ir.sequence', 'Loan Sequence'),
            'tms_fuel_sequence_ids': fields.one2many('tms.office.fuel.supplier.seq', 'office_id', 'Fuel Sequence per Supplier'),
            'company_id': fields.many2one('res.company', 'Company', required=False),
        }
    
    _defaults = {'active':True}
    _order = 'name'




# Agregamos el detalle de las secuencias por proveedor de combustible por cada tienda. 
class tms_office_fuel_supplier_seq(osv.osv):
    _name = "tms.office.fuel.supplier.seq"
    _description = "TMS Office Sequences for Fuel Suppliers"
    
    _columns = {
            'office_id': fields.many2one('tms.office', 'Office', required=True),
            'partner_id': fields.many2one('res.partner', 'Fuel Supplier', required=True),
            'fuel_sequence': fields.many2one('ir.sequence', 'Fuel Sequence', required=True),
            }
    
    _sql_constraints = [
        ('tms_shop_fuel_supplier', 'unique(office_id, partner_id)', 'Partner must be unique !'),
        ]
    




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
