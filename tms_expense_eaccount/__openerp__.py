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
    'name': 'TMS - Add support for Mexico e-Account',
    'version': '1.0',
    'category': 'Account',
    'description': """ 
TMS - Add support for Mexico e-Account
======================================

This module adds options to add XML Invoice file for Mexico's e-Account

""",
    'author': 'Argil Consulting',
    'depends': ['asti_eaccounting_mx_base_70'],
    'data': ['tms_expense_eaccount_view.xml',
            ],
    'website': 'http://www.argil.mx',
    #'installable': True,
    #'active': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
