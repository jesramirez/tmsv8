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
    "name": "TMS - Vehicle Insurance Policy Management",
    "version": "1.0",
    "author": "Argil Consulting",
    "category": "Addon",
    "description" : """
TMS - Vehicle Insurance Policy Management
=========================================

This module adds functionality to Manage Vehicle Insurance Policy expiration.
Also, adds an automated action where sends notification mail of Vehicle Insurance Policies to
expire in next [parameter] days, to [parameter] users.
    """,
    "website": "http://www.argil.mx/",
    "license": "AGPL-3",
    "depends": [
            "tms", 
            "report_webkit"
                ],
    "demo": [],
    "data": ["fleet_vehicle_view.xml", 
             "ir_config_parameter.xml",
             "fleet_vehicle_expired_insurance_report.xml"],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: