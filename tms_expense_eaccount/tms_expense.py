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

class tms_expense_line(osv.osv):
    _inherit = 'tms.expense.line'

    _columns = {
        'invoice_xml_file': fields.binary('Archivo XML', filters='*.xml', required=False, help='Aquí se debe subir el archivo XML de la Factura CFDI'),        
        'invoice_pdf_file': fields.binary('Archivo PDF', filters='*.pdf', required=False, help='Aquí se puede subir el archivo PDF de la Factura CFDI'),        
        
        }

    
class tms_expense_invoice(osv.osv_memory):
    _inherit = 'tms.expense.invoice'
    
    def create_supplier_invoice(self, cr, uid, line, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_tax_obj = self.pool.get('account.invoice.tax')
        expense_line_obj = self.pool.get('tms.expense.line')
        journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'purchase'),('tms_expense_suppliers_journal','=', 1)], context)
        if not journal_id:
            raise osv.except_osv('Error !',
                             _('You have not defined Travel Expense Supplier Journal...'))
        journal_id = journal_id and journal_id[0]

        if line.product_id:
            a = line.product_id.product_tmpl_id.property_account_expense.id
            if not a:
                a = line.product_id.categ_id.property_account_expense_categ.id
            if not a:
                raise osv.except_osv(_('Error !'),
                        _('There is no expense account defined ' \
                                'for this product: "%s" (id:%d)') % \
                                (line.product_id.name, line.product_id.id,))
        else:
            a = property_obj.get(cr, uid,
                    'property_account_expense_categ', 'product.category',
                    context=context).id
        account_fiscal_obj=self.pool.get('account.fiscal.position')
        a = account_fiscal_obj.map_account(cr, uid, False, a)
        inv_line = (0,0, {
            'name'                  : _('%s (TMS Expense Record %s)') % (line.product_id.name, line.expense_id.name),
            'origin'                : line.expense_id.name,
            'account_id'            : a,
            'quantity'              : line.product_uom_qty,
            'price_unit'            : line.price_unit,
            'invoice_line_tax_id'   : [(6, 0, [x.id for x in line.product_id.supplier_taxes_id])],
            'uos_id'                : line.product_uom.id,
            'product_id'            : line.product_id.id,
            'notes'                  : line.name,
            'account_analytic_id'   : False,
            'vehicle_id'            : line.expense_id.unit_id.id,
            'employee_id'           : line.expense_id.employee_id.id,
            'sale_shop_id'          : line.expense_id.shop_id.id,
            })
        
        #print "Subtotal Factura: ", round(line.price_subtotal / line.product_uom_qty, 4)

        notes = line.expense_id.name + ' - ' + line.product_id.name

        a = line.partner_id.property_account_payable.id

        inv = {
            'supplier_invoice_number' : line.invoice_number,
            'name'              : line.expense_id.name + ' - ' + line.invoice_number,
            'origin'            : line.expense_id.name,
            'type'              : 'in_invoice',
            'journal_id'        : journal_id,
            'reference'         : line.expense_id.name + ' - ' + line.invoice_number,
            'account_id'        : a,
            'partner_id'        : line.partner_id.id,
            'invoice_line'      : [inv_line],
            'currency_id'       : line.expense_id.currency_id.id,
            'comment'           : line.expense_id.name + ' - ' + line.invoice_number,
            'payment_term'      : line.partner_id.property_payment_term and line.partner_id.property_payment_term.id or False,
            'fiscal_position'   : line.partner_id.property_account_position.id or False,
            'comment'           : notes,
            }

        inv_id = invoice_obj.create(cr, uid, inv)
        if line.special_tax_amount:
            invoice_obj.button_reset_taxes(cr, uid, [inv_id])
            for tax_line in invoice_obj.browse(cr, uid, inv_id).tax_line:
                if tax_line.amount==0.0:
                    invoice_tax_obj.write(cr, uid, [tax_line.id], {'amount':line.special_tax_amount})
                    
        ###############################################
        if line.invoice_xml_file:
            fname_xml = line.invoice_number.replace(' ','') + '.xml'
            attach = self.pool.get('ir.attachment').create(cr, uid, {
                        'name': fname_xml,
                        'datas': line.invoice_xml_file,
                        'datas_fname': fname_xml,
                        'res_model': 'account.invoice',
                        'res_id': inv_id,
                    }, context=None)
        if line.invoice_pdf_file:
            fname_pdf = line.invoice_number.replace(' ','') + '.pdf'
            if line.invoice_pdf_file:
                attach = self.pool.get('ir.attachment').create(cr, uid, {
                        'name': fname_pdf,
                        'datas': line.invoice_pdf_file,
                        'datas_fname': fname_pdf,
                        'res_model': 'account.invoice',
                        'res_id': inv_id,
                        }, context=None)
        ###############################################
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
        res = expense_line_obj.write(cr, uid, [line.id], {'invoice_id':inv_id})
        return inv_id
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
