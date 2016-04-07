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

{
    "name": "TMS - Driver License Management",
    "version": "1.0",
    "author": "Argil Consulting",
    "category": "TMS",
    "description" : """
TMS - Driver License Management
===============================

This module adds functionality to Manage Driver license expiration and 
adds a constraint to avoid Dispatching Travels when Driver License is expired
or about to expire in next [parameter] days.
Also, adds an automated action where sends notification mail of licenses to
expire in next [parameter] days, to [parameter] users.
    """,
    "website": "http://www.argil.mx/",
    "license": "AGPL-3",
    "depends": [
            "tms", 
            "report_webkit"
                ],
    "demo": [],
    "data": ["hr_employee_view.xml", 
             "ir_config_parameter.xml",
             "hr_employee_expired_license_report.xml"],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: