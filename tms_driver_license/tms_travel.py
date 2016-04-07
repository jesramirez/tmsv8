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
from datetime import date, datetime, time, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tms_travel(osv.osv):
    _inherit='tms.travel'
    
    def action_dispatch(self, cr, uid, ids, context=None):
        val = self.pool.get('ir.config_parameter').get_param(cr, uid, 'tms_driver_license_security_days', context=context)
        xdays = int(val) or 0
        date = datetime.now()  + timedelta(days=xdays)
        #return date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        for travel in self.browse(cr, uid, ids, context=context):
            if travel.employee_id.tms_driver_license_expiration and travel.employee_id.tms_driver_license_expiration <= date.strftime(DEFAULT_SERVER_DATE_FORMAT):
                raise osv.except_osv(_('Warning!'), _("You can not Dispatch this Travel because (%s) %s Driver's License Validity (%s) is expired or about to expire in next %s day(s)") % (travel.employee_id.id, travel.employee_id.name, travel.employee_id.tms_driver_license_expiration, val))
            if travel.employee2_id and travel.employee2_id.tms_driver_license_expiration and travel.employee2_id.tms_driver_license_expiration <= date.strftime(DEFAULT_SERVER_DATE_FORMAT):
                raise osv.except_osv(_('Warning!'), _("You can not Dispatch this Travel because (%s) %s Driver's License Validity (%s)is expired or about to expire in next %s day(s)") % (travel.employee2_id.id, travel.employee2_id.name, travel.employee2_id.tms_driver_license_expiration, val)) 
        return super(tms_travel, self).action_dispatch(cr, uid, ids, context=context)
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
