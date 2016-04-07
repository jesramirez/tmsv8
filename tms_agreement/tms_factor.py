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


# Extra data fields for Waybills & Agreement
# Factors
class tms_factor(osv.osv):
    _name = "tms.factor"
    _inherit = "tms.factor"
    _columns = {        
        'agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade'),# select=True, readonly=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence calculation for these factors."),
        'notes': fields.text('Notes'),
        'control': fields.boolean('Control'),

    }

tms_factor()

#class tms_agreement(osv.osv):
#    _inherit = 'tms.agreement'

#    _columns = {

#        'agreement_customer_factor': fields.one2many('tms.factor', 'agreement_id', 'Agreement Customer Charge Factors', domain=[('category', '=', 'customer')], states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}), 
#        'agreement_supplier_factor': fields.one2many('tms.factor', 'agreement_id', 'Agreement Supplier Payment Factors', domain=[('category', '=', 'supplier')], states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
#        'agreement_driver_factor': fields.one2many('tms.factor', 'agreement_id', 'Agreement Driver Payment Factors', domain=[('category', '=', 'driver')], states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),

#    }

#tms_agreement()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
