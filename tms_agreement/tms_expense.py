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


class tms_indirect_expense(osv.osv):
    _name = 'tms.indirect.expense'
    _description = 'Indirect Expense for Agreement'
    _rec_name='product_id'

    _columns = {
        'product_id'        : fields.many2one('product.product', 'Product',domain=[('tms_category', '=','indirect_expense')] ),
        'agreement_id'		: fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
#        'period_day'        : fields.integer('Period Day', size=2, help="Defines the day to close the accounting period accounts for the indirect expenses this day must be between 1 and 15"),
        'description'       : fields.related('product_id', 'product_tmpl_id', 'description', type="text", string="Descripcion", readonly=True),
        'notes'             : fields.text('Notes'),
        'total_mount_indirect'		: fields.float('Total Mount', digits=(16, 2)),
        'automatic'         : fields.boolean('Automatic', help="If this field is enabled the amount of expenses will be calculated automatically"),
            }

    def get_current_instance(self, cr, uid, id):
        line = self.browse(cr,uid,id)
        obj = None
        for i in line:
            obj = i
        return obj


    _defaults = {
        'automatic': False,
     
    }
tms_indirect_expense()



class tms_direct_expense(osv.osv):
    _name = 'tms.direct.expense'
    _description = 'Directs expenses lines'

    def _amount_line(self, cr, uid, ids, field_name, args, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit
            taxes = tax_obj.compute_all(cr, uid, line.product_id.taxes_id, price, line.product_uom_qty, line.agreement_id.partner_invoice_id.id, line.product_id, line.agreement_id.partner_id)
            cur = line.agreement_id.currency_id

            amount_with_taxes = cur_obj.round(cr, uid, cur, taxes['total_included'])
            amount_tax = cur_obj.round(cr, uid, cur, taxes['total_included']) - cur_obj.round(cr, uid, cur, taxes['total'])
            
            price_subtotal = line.price_unit * line.product_uom_qty
            res[line.id] =  {   'price_total'   : amount_with_taxes,
                                'price_subtotal': price_subtotal,
                                'tax_amount'    : amount_tax,
                                }
        return res

    _columns = {
        'agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
        'automatic_advance': fields.boolean('Automatic Advance'),
        'travel_id'        : fields.many2one('tms.travel', 'Travel', required=False),
        'expense_id'        : fields.many2one('tms.expense', 'Expense', required=False, ondelete='cascade', select=True, readonly=True),
        'line_type'         : fields.selection([
                                          ('real_expense','Real Expense'),
                                          ('madeup_expense','Made-up Expense'),
                                          ('salary','Salary'),
                                          ('salary_retention','Salary Retention'),
                                          ('salary_discount','Salary Discount'),
                                          ('fuel','Fuel'),
                                          ('indirect','Indirect'),
                                    ], 'Line Type', require=True),

        'name'              : fields.char('Description', size=256, required=True),
        'sequence'          : fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'product_id'        : fields.many2one('product.product', 'Product', domain=[('tms_category', 'in', ('freight','move','highway_tolls','other','real_expense','madeup_expense','salary','fuel','indirect_expense'))]),
        'price_unit'        : fields.float('Price Unit', required=True, digits_compute= dp.get_precision('Sale Price')),

################# Pruebas de identificacion de errores Agreement #####################
        'price_subtotal'    : fields.function(_amount_line, method=True, string='SubTotal', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
        'price_total'       : fields.function(_amount_line, method=True, string='Total', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
        'tax_amount'        : fields.function(_amount_line, method=True, string='Tax Amount', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
#######################################################################################        
        'special_tax_amount': fields.float('Special Tax', required=False, digits_compute= dp.get_precision('Sale Price')),
        'tax_id'            : fields.many2many('account.tax', 'expense_tax', 'tms_expense_line_id', 'tax_id', 'Taxes'),
        'product_uom_qty'   : fields.float('Quantity (UoM)', digits=(16, 2)),
        'product_uom'       : fields.many2one('product.uom', 'Unit of Measure '),
        'notes'             : fields.text('Notes'),
        'expense_employee_id': fields.related('expense_id', 'employee_id', type='many2one', relation='res.partner', store=True, string='Driver'),
        'shop_id'           : fields.related('expense_id', 'shop_id', type='many2one', relation='sale.shop', string='Shop', store=True, readonly=True),
        'company_id'        : fields.related('expense_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'fuel_voucher'      : fields.boolean('Fuel Voucher'),

        'control'           : fields.boolean('Control'), # Useful to mark those lines that must not be taken for Expense Record (like Fuel from Fuel Voucher, Toll Stations payed without cash (credit card, voucher, etc)
        'automatic'         : fields.boolean('Automatic Advance', help="Check this if you want to create Advances for this line automatically"),
        'credit'            : fields.boolean('Automatic Fuel', help="Check this if you want to create Fuel Vouchers for this line"),
        'fuel_supplier_id'  : fields.many2one('res.partner', 'Fuel Supplier', domain=[('tms_category', '=', 'fuel')],  required=False),
        'on_change'         : fields.boolean('Creado desde el Onchange'),
    }
    _order = 'sequence'

    _defaults = {
        'line_type'         : 'real_expense',
        'product_uom_qty'   : 1,
        'sequence'          : 10,
        'price_unit'        : 0.0,
    }

    def on_change_product_id(self, cr, uid, ids, product_id):
        res = {}
        if not product_id:
            return {}
        prod_obj = self.pool.get('product.product')
        for product in prod_obj.browse(cr, uid, [product_id], context=None):
            res = {'value': {'product_uom' : product.uom_id.id,
                             'name': product.name,
                             'tax_id': [(6, 0, [x.id for x in product.supplier_taxes_id])],
                            }
                }
        return res

    def on_change_amount(self, cr, uid, ids, product_uom_qty, price_unit, product_id):
        res = {'value': {
                    'price_subtotal': 0.0, 
                    'price_total': 0.0,
                    'tax_amount': 0.0, 
                        }
                }
        if not (product_uom_qty and price_unit and product_id ):
            return res
        tax_factor = 0.00
        prod_obj = self.pool.get('product.product')
        for line in prod_obj.browse(cr, uid, [product_id], context=None)[0].supplier_taxes_id:
            tax_factor = (tax_factor + line.amount) if line.amount <> 0.0 else tax_factor
        price_subtotal = price_unit * product_uom_qty
        res = {'value': {
                    'price_subtotal': price_subtotal, 
                    'tax_amount': price_subtotal * tax_factor, 
                    'price_total': price_subtotal * (1.0 + tax_factor),
                        }
                }
        return res

# Wizard que permite validar la cancelacion de una Liquidacion
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: