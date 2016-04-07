# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


{
    'name'          : 'Freight Management - Analysis',
    'version'       : '1.0',
    'category'      : 'Vertical',
    'complexity'    : "easy",
    'description'   : """TMS Analysis """,
    'author'        : 'HESATEC',
    'website'       : 'http://www.hesatecnica.com',
    'images' : [],
    'depends': ["tms"],
    'update_xml' : [
                'tms_waybill_analysis_view.xml',
                'tms_travel_analysis_view.xml',
                'tms_expense_analysis_view.xml',
                #'tms_report_fuel_voucher_view.xml',
                #'tms_report_performance_unit_view.xml',
                #'tms_report_performance_unit_fuel_route_view.xml',
                ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
