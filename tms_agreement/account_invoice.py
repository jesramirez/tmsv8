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

import dateutil
import dateutil.parser
from dateutil.relativedelta import relativedelta
from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {        
        'entry_invoice': fields.selection([('Ingreso','Ingreso'),('Egreso','Egreso')],'Ingreso o Egreso', required=False),
    }


    def invoice_validate(self, cr, uid, ids, context=None):
        result =  super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        for rec in self.browse(cr, uid, ids, context=context):
            tipoComprobante = ""
            if rec.type == 'out_invoice':
                tipoComprobante = 'Ingreso'
            elif rec.type == 'out_refund':
                tipoComprobante = 'Egreso'
            rec.write({'entry_invoice': tipoComprobante})

        return result

account_invoice()