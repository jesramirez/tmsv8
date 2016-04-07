# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import amount_to_text_mx as  amount_to


# AMOUNT TO TEXT

class tms_advance(osv.osv):
    _name ='tms.advance'
    _inherit = 'tms.advance'

    def _amount_text(self, cr, uid, ids, field_name, args, context=None):
        if not context:
            context = {}
        res = {}
        amount_to_text = ''
        for record in self.browse(cr, uid, ids, context=context):
            if record.total > 0:
                amount_to_text = amount_to.get_amount_to_text(
                    self, record.total, 'es_cheque', record.currency_id.name
                    )
            res[record.id] = amount_to_text
        return res


    _columns = {        
        'amount_to_text': fields.function(_amount_text, method=True, string='Monto en Letra', type='char', size=256, store=True),


    }

tms_advance()
