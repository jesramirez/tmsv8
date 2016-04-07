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

class tms_maintenance_order(osv.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'tms.maintenance.order'
    _description = 'Order Maintenace'

########################### Columnas : Atributos #######################################################################
    _columns = {
        'name': fields.char('Order Maintenance'),
        'description': fields.char('Description'),
        'notes': fields.text('Notes'),
        'state': fields.selection([('draft','Draft'), ('confirmed','Confirmed'), ('done','Done'), ('cancel','Cancelled')],'Estados'),

        'cheduled_start': fields.datetime('Cheduled Start'),
        'cheduled_end': fields.datetime('Cheduled End'),
        'cheduled_start_real': fields.datetime('Cheduled Start Real'),
        'cheduled_end_real': fields.datetime('Cheduled End Real'),

        ########Many2One###########
        'unit_id': fields.many2one('tms.unit','Unit'),
        'concept_id': fields.many2one('product.product','Concept Maintenance'),
        'supervisor_id': fields.many2one('hr.employee','Supervisor'),
        'driver_report_id': fields.many2one('hr.employee','Driver Report'),
        'user_register_order_id': fields.many2one('hr.employee','User Register Report'),
        
        ########One2Many###########
        'activities_ids': fields.one2many('tms.maintenance.order.activity','maintenance_order_id','Activities'),
    }
    
########################### Metodos ####################################################################################

    ########## Metodos para el 'state' ##########
    def action_draft(self,cr,uid,ids,context={}):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def action_confirmed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{'state':'confirmed'}) 
        return True

    def action_done(self,cr,uid,ids,context={}): 
        self.write(cr, uid, ids, {'state':'done'})
        return True    


    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

########################### Valores por Defecto ########################################################################
    _defaults = {
        'state'                 : lambda *a: 'draft',
    }

########################### Criterio de ordenamiento ###################################################################
    _order = 'name'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
