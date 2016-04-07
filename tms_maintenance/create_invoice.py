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

class tms_maintenance_order_activity_invoice(osv.osv_memory):

    _name = 'tms.maintenance.order.activity.invoice'
    _description = 'Create Invoices from External Workshop Supplier'
###################################################################################################        

    ########## Metodos para crear la factura ##########
    def button_generate_invoices(self,cr,uid,ids,context=None):
        
        invoice_obj = self.pool.get('account.invoice')
        record_ids =  context.get('active_ids',[])
        invoices_to_create = {}
        
        journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'purchase')], context=None)
        journal_id = journal_id and journal_id[0] or False
        activity_obj = self.pool.get('tms.maintenance.order.activity')
        for activity in activity_obj.browse(cr, uid, record_ids):
            a = activity.maintenance_order_id.product_id.property_stock_production.valuation_out_account_id.id
            if not a:
                raise osv.except_osv(_('Error !'),
                        _('There is no expense account defined ' \
                          'for production location of product: "%s" (id:%d)') % \
                                (activity.maintenance_order_id.product_id.name, activity.maintenance_order_id.product_id.id,))
            a = self.pool.get('account.fiscal.position').map_account(cr, uid, False, a)
            
            if activity.supplier_id.id not in invoices_to_create and activity.state=='done' and (not activity.invoiced or activity.invoice_id.state=='cancel'):
                invoices_to_create.update(
                    {   
                        activity.supplier_id.id : 
                        { 
                            'header' : {
                                    'name'              : _('Invoice TMS Maintenance'),
                                    'origin'            : activity.maintenance_order_id.name,
                                    'type'              : 'in_invoice',
                                    'journal_id'        : journal_id,
                                    'reference'         : _('Maintenance Activities Invoice'),
                                    'account_id'        : activity.supplier_id.property_account_payable.id,
                                    'partner_id'        : activity.supplier_id.id,
                                    #'address_invoice_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                                    #'address_contact_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                                    'invoice_line'      : [],
                                    'currency_id'       : activity.supplier_id.property_product_pricelist_purchase.currency_id.id,                                     #res.currency
                                    'comment'           : _('No Comments'),
                                    #'payment_term'      : pay_term,                                    #account.payment.term
                                    'fiscal_position'   : activity.supplier_id.property_account_position.id,
                                    'date_invoice'      : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                    },
                            'activity_ids' : [],
                            }
                    }
                )
                
            if activity.state =='done' and (not activity.invoiced or activity.invoice_id.state=='cancel') :
                inv_line = (0,0,{
                        'name'      : activity.maintenance_order_id.name + ', ' + activity.product_id.name, 
                        'origin'    : activity.maintenance_order_id.product_id.name,
                        'account_id': a,
                        'price_unit': (activity.cost_service_external + activity.parts_cost_external),
                        'quantity'  : 1,
                        'uos_id'    : activity.product_id.uom_id.id,
                        'product_id': activity.product_id.id,
                        'invoice_line_tax_id': [(6, 0, [x.id for x in activity.product_id.supplier_taxes_id])],
                        'note'      : _('Invoice Created from Maintenance External Workshop Tasks'),
                        #'account_analytic_id': False,
                        'vehicle_id': activity.maintenance_order_id.unit_id.id,
                        'employee_id': activity.maintenance_order_id.driver_id.id,
                        'office_id': activity.maintenance_order_id.office_id.id,
                       })

                invoices_to_create[activity.supplier_id.id]['header']['invoice_line'].append(inv_line)
                invoices_to_create[activity.supplier_id.id]['activity_ids'].append(activity.id)
            
        if not invoices_to_create:
            raise osv.except_osv(_('Warning!'), _("Either all Tasks are already Invoiced or they were not done by an External Workshop (Supplier)"))
        for (key, invoice) in invoices_to_create.iteritems():
            invoice_id = invoice_obj.create(cr, uid, invoice['header'])
            activity_obj.write(cr, uid, invoice['activity_ids'], {'invoice_id':invoice_id, 'invoiced':True})            
        return True

 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
