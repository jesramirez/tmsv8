# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Argil Consulting - http://www.argil.mx
############################################################################
#    Coded by: Israel Cruz Argil (israel.cruz@argil.mx)
############################################################################
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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, date, timedelta

class fleet_vehicle(osv.osv):
    _inherit='fleet.vehicle'
    
    def _get_days_to_expire(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        days=0.0
        for rec in self.browse(cr, uid, ids, context=context):
            a = datetime.strptime(rec.insurance_policy_expiration, '%Y-%m-%d') if rec.insurance_policy_expiration else datetime.now()
            b = datetime.now()
            delta = a - b
            res[rec.id] = delta.days if delta.days > 0 else 0
        return res

    
    _columns = {
        'insurance_policy'              : fields.char('Insurance Policy', size=64),
        'insurance_policy_data'         : fields.char('Insurance Policy Data', size=64),
        'insurance_policy_expiration'   : fields.date('Insurance Policy Expiration'),
        'insurance_supplier_id'         : fields.many2one('res.partner', 'Insurance Supplier', required=False, readonly=False, 
                                            domain="[('tms_category','=','none'),('is_company', '=', True)]"),
        'insurance_policy_days_to_expire' : fields.function(_get_days_to_expire, method=True, string='Days to expire', type='integer', store=False, multi=False),
        }
    
    
    def send_mail_vehicle_insurance_report(self, cr, uid, ids, context=None):
        email_template_obj = self.pool.get('email.template')
        template_ids = email_template_obj.search(cr, uid, [('model_id.model', '=','fleet.vehicle')], context=context) 
        if not template_ids:
            return True #raise osv.except_osv(_('Warning!'), _('There are no Template configured for sending mail'))
        values = email_template_obj.generate_email(cr, uid, template_ids[0], ids, context=context)
        values['res_id'] = False
        mail_mail_obj = self.pool.get('mail.mail')
        msg_id = mail_mail_obj.create(cr, uid, values, context=context)

        attachment_obj = self.pool.get('ir.attachment')
        ir_actions_report = self.pool.get('ir.actions.report.xml')

        matching_reports = ir_actions_report.search(cr, uid, [('report_name','=','fleet.vehicle.expired_insurance.report.webkit')])
        if not matching_reports:
            return True #raise osv.except_osv(_('Warning!'), _('There is no Report to send')) 

        report = ir_actions_report.browse(cr, uid, matching_reports[0])
        report_service = 'report.' + report.report_name
        service = netsvc.LocalService(report_service)
        date = self.pool.get('fleet.vehicle.expired_insurance')._get_date(cr, uid, ids)
        vehicle_ids = self.search(cr, uid, [('insurance_policy_expiration',"<=", date)], order='insurance_policy_expiration desc')
        if not vehicle_ids:
            return True #raise osv.except_osv(_('Warning!'), _('There are no records to print'))

        (result, format) = service.create(cr, uid, vehicle_ids, 
                                          {'model': 'fleet.vehicle', 'count': len(vehicle_ids),'date': date}, context=context)

        result = base64.b64encode(result)
        file_name = _('Expire_or_to_expire_Vehicle_Insurance_Policies')
        file_name += ".pdf"
        attachment_id = attachment_obj.create(cr, uid,
            {
                'name': file_name,
                'datas': result,
                'datas_fname': file_name,
                'res_model': self._name,
                'res_id': msg_id,
                'type': 'binary'
            }, context=context)
                

        if msg_id and attachment_id:
            mail_mail_obj.write(cr, uid, msg_id, {'attachment_ids': [(6, 0, [attachment_id])]}, context=context)
            mail_mail_obj.send(cr, uid, [msg_id], context=context)
        return True


class fleet_vehicle_expired_insurance(osv.osv_memory):
    _name = 'fleet.vehicle.expired_insurance'
    _description = "Wizard to get Vehicle Insurance Policies to expire"

    
    def _get_date(self, cr, uid, ids, context=None):
        val = self.pool.get('ir.config_parameter').get_param(cr, uid, 'tms_vehicle_insurance_notification_x_days', context=context)
        xdays = int(val) or 0
        date = datetime.now()  + timedelta(days=xdays)
        return date.strftime(DEFAULT_SERVER_DATE_FORMAT)
    
    _columns = {
            'date'    : fields.date('Date', required=True),
            'include' : fields.selection([
                                ('all', 'All Vehicles (Own & Suppliers)'),
                                ('int', 'Own Vehicles'),
                                ('ext', 'Supplier Vehicles'),
                                ], 'Include', required=True),
            }

    _defaults = {
        'date'   : _get_date,
        'include' : 'all',
            }
    
    def button_get_vehicle_insurance_policies_to_expire(self, cr, uid, ids, to_attach=False, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}

        
        date = self.browse(cr, uid, ids)[0].date
        include = self.browse(cr, uid, ids)[0].include
        vehicle_obj = self.pool.get('fleet.vehicle')
        condition = [('insurance_policy_expiration',"<=", date)]#, ('tms_category','=','driver')]
        if include=='int':
            condition.append(('supplier_unit','=',False))
        elif include=='ext':
            condition.append(('supplier_unit','=',True))
        vehicle_ids = vehicle_obj.search(cr, uid, condition, order='insurance_policy_expiration desc')
        
        if vehicle_ids:
            datas = {   'ids': vehicle_ids, 
                        'count': len(vehicle_ids),
                        'date': date}
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'fleet.vehicle.expired_insurance.report.webkit',
                'datas': datas,
                }
        else:
            raise osv.except_osv(_('Warning!'), _('There are no Fleet Vehicle Insurance Policies expired or to expire on this date'))

        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
