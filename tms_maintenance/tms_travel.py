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
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tms_travel(osv.osv):
    _inherit='tms.travel'
    
    def action_dispatch(self, cr, uid, ids, context=None):
        val = self.pool.get('ir.config_parameter').get_param(cr, uid, 'tms_restrict_travel_distpatch_if_vehicle_has_open_service_order', context=context)
        restrict = int(val) or 0
        if restrict:
            for travel in self.browse(cr, uid, ids, context=context):
                cr.execute("select id from tms_maintenance_order where unit_id=%s and state='open';" % (travel.unit_id.id))
                if filter(None, map(lambda x:x[0], cr.fetchall())):
                    raise osv.except_osv(_('Warning!'), _("You can not Dispatch this Travel because Vehicle %s has an Open Maintenance Service Order") % (travel.unit_id.name))
                if travel.trailer1_id:
                    cr.execute("select id from tms_maintenance_order where unit_id=%s and state='open';" % (travel.trailer1_id.id))
                    if filter(None, map(lambda x:x[0], cr.fetchall())):
                        raise osv.except_osv(_('Warning!'), _("You can not Dispatch this Travel because Vehicle %s has an Open Maintenance Service Order") % (travel.trailer1_id.name))
                if travel.dolly_id:
                    cr.execute("select id from tms_maintenance_order where unit_id=%s and state='open';" % (travel.dolly_id.id))
                    if filter(None, map(lambda x:x[0], cr.fetchall())):
                        raise osv.except_osv(_('Warning!'), _("You can not Dispatch this Travel because Vehicle %s has an Open Maintenance Service Order") % (travel.dolly_id.name))
                if travel.trailer2_id:
                    cr.execute("select id from tms_maintenance_order where unit_id=%s and state='open';" % (travel.trailer2_id.id))
                    if filter(None, map(lambda x:x[0], cr.fetchall())):
                        raise osv.except_osv(_('Warning!'), _("You can not Dispatch this Travel because Vehicle %s has an Open Maintenance Service Order") % (travel.trailer2_id.name))                       
        return super(tms_travel, self).action_dispatch(cr, uid, ids, context=context)
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
