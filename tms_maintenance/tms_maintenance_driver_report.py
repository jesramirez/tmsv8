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




# Travel - Money advance payments for Travel expenses

class tms_maintenance_driver_report(osv.osv):
    _name ='tms.maintenance.driver_report'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Driver Report of Vehicle Failure'

    def _solved(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = True if record.maintenance_order_id.id else False
        return res


    def _get_changes_from_tms_maintenance_order(self, cr, uid, ids, context=None):
        report_ids = {}
        for rec in self.pool.get('tms.maintenance.order').browse(cr, uid, ids, context=context):
            for r in rec.tms_maintenance_driver_report_ids:
                report_ids[r.id] = True

        res = []
        if report_ids:
            res = self.pool.get('tms.maintenance.driver_report').search(cr, uid, [('id','in',report_ids.keys())], context=context)
        return res
    

    
    _columns = {


        'name'          : fields.char('Report', size=64, required=False),
        'state'         : fields.selection([('draft','Draft'), ('confirmed','Confirmed'), ('closed','Closed'), ('cancel','Cancelled')], 'State', readonly=True),
        'date'          : fields.date('Date', states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)],'closed':[('readonly',True)]}, required=True),
        'office_id'       : fields.many2one('tms.office', 'Workshop', states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)],'closed':[('readonly',True)]}, required=True),
        'vehicle_id'    : fields.many2one('fleet.vehicle', 'Vehicle', states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)],'closed':[('readonly',True)]}, required=True),
        'employee_id'   : fields.many2one('hr.employee', 'Driver', states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)],'closed':[('readonly',True)]}, required=True),
        'notes'         : fields.text('Notes', states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)],'closed':[('readonly',True)]}, required=True),
        #'maintenance_order_ids': fields.many2many('tms.travel', 'tms_expense_travel_rel', 'expense_id', 'travel_id', 'Travels', readonly=False, states={'confirmed': [('readonly', True)],'closed':[('readonly',True)]}),
        'maintenance_order_id'  : fields.many2one('tms.maintenance.order', 'Service Order', ondelete='restrict', required=False, readonly=True, states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)], 'closed':[('readonly',True)]}),
        'date_end_real'       : fields.related('maintenance_order_id', 'date_end_real', type='datetime', string='Date Solved', readonly=True),                

        'create_uid'    : fields.many2one('res.users', 'Created by', readonly=True),
        'create_date'   : fields.datetime('Creation Date', readonly=True, select=True),
        'cancelled_by'  : fields.many2one('res.users', 'Cancelled by', readonly=True),
        'date_cancelled': fields.datetime('Date Cancelled', readonly=True),
        'confirmed_by'  : fields.many2one('res.users', 'Confirmed by', readonly=True),
        'date_confirmed': fields.datetime('Date Confirmed', readonly=True),
        'closed_by'     : fields.many2one('res.users', 'Closed by', readonly=True),
        'date_closed'   : fields.datetime('Date Closed', readonly=True),
        'drafted_by'    : fields.many2one('res.users', 'Drafted by', readonly=True),
        'date_drafted'  : fields.datetime('Date Drafted', readonly=True),
        'solved'        : fields.function(_solved, method=True, string='Solved', type='boolean', multi=False,
                                          store = {'tms.maintenance.order': (_get_changes_from_tms_maintenance_order, None, 50)}),        
        }
    
    _defaults = {
        'date'              : lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        'state'             : lambda *a: 'draft',
        }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Driver Report number must be unique !'),
        ]
    _order = "name desc, date desc"


    def create(self, cr, uid, vals, context=None):        
        office_id = vals['office_id']
        shop = self.pool.get('tms.office').browse(cr, uid, [office_id])[0]
        if shop.tms_maintenance_order_driver_report_seq:
            seq_id = shop.tms_maintenance_order_driver_report_seq.id
            seq_number = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
            vals['name'] = seq_number
        else:
            raise osv.except_osv(_('Driver Failure Report Error !'), _('You have not defined Driver Failure Report Sequence for shop ' + shop.name))
        return super(tms_maintenance_driver_report, self).create(cr, uid, vals, context=context)


    def action_cancel_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        for record in self.browse(cr, uid, ids):
            self.write(cr, uid, ids, {'state':'draft','drafted_by':uid,'date_drafted':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.state not in ('closed') and record.maintenance_order_id.id:
                raise osv.except_osv( _('Could not cancel Report !'),
                                      _('This Driver Report of Failure is already linked to Service Order'))
            else:
                self.write(cr, uid, ids, {'state':'cancel', 'cancelled_by':uid,'date_cancelled':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'confirmed', 'confirmed_by':uid,'date_confirmed':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'cancelled_by' : False,
            'date_cancelled': False,
            'confirmed_by' : False,
            'date_confirmed': False,
            'closed_by' : False,
            'date_closed': False,
            'drafted_by' : False,
            'date_drafted': False,
            'maintenance_order_id': False,
            'notes': False,
        })
        return super(tms_maintenance_driver_report, self).copy(cr, uid, id, default, context)


# Adding relation between Expense Records and Travels
class tms_maintenance_order(osv.osv):
    _inherit="tms.maintenance.order"

    _columns = {
        'tms_maintenance_driver_report_ids'   : fields.many2many('tms.maintenance.driver_report', 'tms_driver_report_maint_order_rel', 'order_id', 'report_id', 'Driver Report of Failures',
                                                                 readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(tms_maintenance_order, self).write(cr, uid, ids, vals, context=context)
        if 'tms_maintenance_driver_report_ids' in vals or ('state' in vals and vals['state']=='done'):
            report_obj = self.pool.get('tms.maintenance.driver_report')
            report_ids = report_obj.search(cr, uid, [('maintenance_order_id','=',ids[0])])
            if report_ids:
                report_obj.write(cr, uid, report_ids, {'maintenance_order_id':False, 'state': 'confirmed', 'closed_by' : False, 'date_closed': False})
            report_ids = []
            order = self.browse(cr, uid, ids)[0]
            for report in order.tms_maintenance_driver_report_ids:
                    report_ids.append(report.id)
            if report_ids:
                report_obj.write(cr, uid, report_ids, {'maintenance_order_id':ids[0],'state': 'closed', 'closed_by' : uid, 'date_closed': order.date_end_real})
        return res                

    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

