# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://www.hesatecnica.com.com/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@hesatecnica.com)
############################################################################
#    Coded by: german_442 email: (german.ponce@hesatecnica.com)
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 HESATEC (<http://www.hesatecnica.com>).
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
    "name" : "Agreements and Quotes for module Freight Management ",
    "version" : "1.0",
    "category" : "Vertical",
    'complexity': "normal",
    "author" : "HESATEC",
    "website": "http://www.hesatecnica.com",
    "depends" : ["tms"], #"jasper_reports", "hesatec_mx_accounting_reports_v7"],
    "description": "This module allows you to create and analyze travel quotes order to get to know if the trip is profitable and generating agreements based on Profit, special assistants to generate quite a journey with a single click! ....",
    "demo_xml" : [],
    "init_xml" : [],
    "update_xml" : [
                    'sale_view.xml',
                    'tms_quotation_view.xml',
                    'tms_agreement_view.xml',
                    #'agreement_sequence.xml',
                    'tms_waybill_view.xml',
                    #'tms_inherit_view.xml',
                    # 'crm_view.xml',
                    'res_partner_view.xml',
                    'product_view.xml',
                    ],
    "active": False,
    'application': True,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

