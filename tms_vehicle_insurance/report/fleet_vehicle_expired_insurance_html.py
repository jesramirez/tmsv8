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
from openerp.report import report_sxw
from openerp.tools.translate import _
import time
#from report_webkit import report_helper
#from report_webkit import webkit_report



class fleet_vehicle_expired_insurance_report_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fleet_vehicle_expired_insurance_report_html, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.fleet.vehicle.expired_insurance.report.webkit','fleet.vehicle','addons/tms_vehicle_insurance/report/fleet_vehicle_expired_insurance_html.mako',parser=fleet_vehicle_expired_insurance_report_html)

#webkit_report.WebKitParser('report.account.move.report.webkit',
#                      'account.move',
#                      'addons/report_account_move/report/account_move_report_html.mako',
#                      parser=account_move_report_html)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
