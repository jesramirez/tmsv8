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
from pytz import timezone

class tms_agreement(osv.Model):
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_name = 'tms.agreement'
	_description = 'Agreement'


	# def _amount_factor(self, cr, uid, ids, field_name, arg, context=None):
	# 	tax_obj = self.pool.get('account.tax')
	# 	cur_obj = self.pool.get('res.currency')
	# 	res = {}
	# 	amount_customer_factor = amount_supplier_factor = amount_driver_factor = amount_factors = 0.0
	# 	for agreement in self.browse(cr, uid, ids, context=context):
	# 		res[agreement.id] = {
	# 			'amount_customer_factor': 0.0,
	# 			'amount_customer': 0.0,
	# 			'amount_supplier_factor': 0.0,
	# 			'amount_driver_factor': 0.0,
	# 			'amount_factors': 0.0,
	# 		}
	# 		amount_customer_factor_1 = amount_supplier_factor_1 = amount_driver_factor_1 = amount_factors_1 = 0.0
	# 		for customer_factor in agreement.agreement_customer_factor :
	# 			amount_customer_factor_1 += customer_factor.total_amount + customer_factor.fixed_amount
	# 		res[agreement.id] ['amount_customer_factor'] = amount_customer_factor_1
	# 		res[agreement.id] ['amount_customer'] = amount_customer_factor_1
	# 		amount_customer_factor = amount_customer_factor_1
	# 		for supplier_factor in agreement.agreement_supplier_factor:
	# 			result = self.calculate(cr, uid, 'supplier', ids, 'client', False)
	# 			amount_supplier_factor_1 += result
	# 		res[agreement.id] ['amount_supplier_factor'] = amount_supplier_factor_1
	# 		amount_supplier_factor = amount_supplier_factor_1
	# 		for driver_factor in agreement.agreement_driver_factor:
	# 			amount_driver_factor_1 += driver_factor.total_amount + driver_factor.fixed_amount
	# 		res[agreement.id] ['amount_driver_factor'] = amount_driver_factor_1
	# 		amount_driver_factor = amount_driver_factor_1
	# 		amount_factors = amount_supplier_factor + amount_driver_factor
	# 		res[agreement.id] ['amount_factors'] = amount_factors
	# 	return res

	# def _amount_factor_route(self, cr, uid, ids, field_name, arg, context=None):
	# 	tax_obj = self.pool.get('account.tax')
	# 	cur_obj = self.pool.get('res.currency')
	# 	res = {}
	# 	amount_toll_station_route = amount_driver_route = amount_factors_route = 0.0
	# 	for agreement in self.browse(cr, uid, ids, context=context):
	# 		res[agreement.id] = {
	# 			'amount_toll_station_route': 0.0,
	# 			'amount_driver_route': 0.0,
	# 			'amount_factors_route': 0.0,
	# 		}
	# 		for toll in agreement.route_id.tms_route_tollstation_ids:
	# 			amount_axis = 0.0
	# 			for axis in toll.tms_route_tollstation_costperaxis_ids:
	# 				amount_axis += axis.cost_credit + axis.cost_cash
	# 			amount_toll_station_route += amount_axis
	# 		res[agreement.id] ['amount_toll_station_route'] = amount_toll_station_route

	# 		for route in agreement.route_id.expense_driver_factor:
	# 			amount_driver_route +=route.total_amount + route.fixed_amount
	# 		res[agreement.id] ['amount_driver_route'] = amount_driver_route
	# 		res[agreement.id] ['amount_factors_route'] = amount_driver_route + amount_toll_station_route
	# 	return res

	def _shipped_product(self, cr, uid, ids, field_name, args, context=None):
		res = {}
		context_wo_lang = context.copy()
		context_wo_lang.pop('lang', None)
		for agreement in self.browse(cr, uid, ids, context=context_wo_lang):
			volume = weight = qty = 0.0
			for record in agreement.agreement_shipped_product:
				qty += record.product_uom_qty
				
				volume += record.product_uom_qty 
				weight += record.product_uom_qty 
				res[agreement.id] =  {'product_qty': qty,
									'product_volume': volume,
									'product_weight': weight,
									'product_uom_type': (record.product_uom.category_id.name),
									}
		return res



	# def _amount_direct_line(self, cr, uid, ids, field_name, arg, context=None):
	# 	res = {}
	# 	for agreement in self.browse(cr, uid, ids, context=context):
	# 		res[agreement.id] = {
	# 			'direct_amount': 0.0,
	# 			'taxes_amount_direct': 0.0,
	# 		}
	# 		direct_amount_sum = taxes_amount_direct_sum = 0.0
	# 		for direct_line in agreement.agreement_direct_expense_line:
	# 			direct_amount_sum += direct_line.price_total
	# 			taxes_amount_direct_sum += direct_line.tax_amount
	# 		res[agreement.id] ['direct_amount'] = direct_amount_sum
	# 		res[agreement.id] ['taxes_amount_direct'] = taxes_amount_direct_sum
	# 	return res


	# def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
	# 	print "################################## EJECUTANDO AMOUNT ALLLLLLLLL FUNCION"
	# 	cur_obj = self.pool.get('res.currency')
	# 	res = {}
	# 	for agreement in self.browse(cr, uid, ids, context=context):
	# 		res[agreement.id] = {
	# 			'expenses_amount': 0.0,
	# 			'amount_untaxed': 0.0,
	# 			'amount_tax': 0.0,
	# 			'amount_tax_expenses': 0.0,
	# 			'amount_subtotal': 0.0,
	# 			'amount_total': 0.0,

	# 		}
	# 		val = val1 = 0.0
	# 		taxes_expenses = agreement.taxes_amount_direct
	# 		indirect_amount = agreement.indirect_amount
	# 		direct_amount = agreement.direct_amount
	# 		customer_factor= agreement.amount_customer_factor
	# 		cur = agreement.currency_id
	# 		indirect_amount = agreement.indirect_amount
	# 		for line in agreement.agreement_line:
	# 			print "################################## PRODUCTO", line.product_id.name
	# 			print "################################## TOTAL", line.price_subtotal
	# 			val1 += line.price_subtotal
	# 			val += line.tax_amount
	# 		print "########################### RESULTADO DE LAS LINEAS", val1

	# 		res[agreement.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
	# 		res[agreement.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
	# 		res[agreement.id]['amount_tax_expenses'] = taxes_expenses
	# 		res[agreement.id] ['expenses_amount'] = (indirect_amount + direct_amount) - taxes_expenses
	# 		res[agreement.id]['amount_subtotal'] = res[agreement.id]['amount_untaxed'] + res[agreement.id]['amount_tax'] 
	# 		res[agreement.id]['amount_total'] = res[agreement.id]['amount_subtotal'] - (indirect_amount + direct_amount) 

	# 	return res

	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('tms.agreement.line').browse(cr, uid, ids, context=context):
			result[line.order_id.id] = True
		return result.keys()

	def _get_route_distance(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		distance=0.0
		for agreement in self.browse(cr, uid, ids, context=context):
			distance = agreement.route_id.distance
			res[agreement.id] = distance
		return res

	def _get_route_hours(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		hours=0.0
		for agreement in self.browse(cr, uid, ids, context=context):
			hours = agreement.route_id.travel_time
			res[agreement.id] = hours
		return res

	def _get_date_start(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		date_start_sched= time.strftime( DEFAULT_SERVER_DATETIME_FORMAT)
		
		for agreement in self.browse(cr, uid, ids, context=context):
			date_start_sched = agreement.date_start
			res[agreement.id] = date_start_sched
		return res
		
	def _get_date_end(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		date_end_sched= time.strftime( DEFAULT_SERVER_DATETIME_FORMAT)
		
		for agreement in self.browse(cr, uid, ids, context=context):
			date_end_sched = agreement.date_end
			res[agreement.id] = date_end_sched
		return res


	def _get_hours_total(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		date_total_hours = 0.0
		for agreement in self.browse(cr, uid, ids, context=context):
			res[agreement.id] = {
				'date_total_hours': 0.0,
			}
			date_total_hours = agreement.hours_start_upload + agreement.hours_upload_end_upload + agreement.hours_end_upload_lib_docs + agreement.hours_lib_docs_prog_download + agreement.hours_prog_download_start_download + agreement.hours_start_download_end_download + agreement.hours_end_download_lib_docs_download + agreement.hours_lib_docs_download_end_travel
			res[agreement.id] = date_total_hours
		return res


	def _get_active(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		date_system = time.strftime( DEFAULT_SERVER_DATETIME_FORMAT)
		for agreement in self.browse(cr, uid, ids, context=context):
			date_end_c = agreement.date_end
			if date_system > date_end_c :
				res[agreement.id] = False
			else:
				res[agreement.id] = True
		return res

	def copy(self, cr, uid, id, default=None, context=None):
		if not default:
			default = {}
		default.update({
			'name': self.pool.get('ir.sequence').get(cr, uid, 'tms.agreement'),
		})
		return super(tms_agreement_agreement, self).copy(cr, uid, id, default, context=context)


	_columns = {
		'image': fields.related('partner_id', 'image', type="binary", string="Logo", readonly=True),
		'image_medium': fields.related('partner_id', 'image_medium', type="binary", string="Logo"),
		'image_small': fields.related('partner_id', 'image_small', type="binary", string="Logo"),
		'name': fields.char('Name', size=64, readonly=True, select=True),
		'version': fields.float('Version', digits=(16, 2), readonly=False, select=True),
		'description': fields.char('Name', size=64, readonly=True, select=True),        
		'date'    : fields.datetime('Date',required=True, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'route_id': fields.many2one('tms.route', 'Route',states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}, required=True),              
		'route_return_id': fields.many2one('tms.route', 'Uncharged Route',states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}, required=False),              
		'departure_id': fields.related('route_id', 'departure_id', type='many2one', relation='tms.place', string='Departure', store=True, readonly=True),                
		'arrival_id': fields.related('route_id', 'arrival_id', type='many2one', relation='tms.place', string='Arrival', store=True, readonly=True),                
		'unit_ids': fields.many2one('tms.unit.category', 'Unit Category',required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'units_a': fields.integer('Units Number',required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'account_periods_ids' : fields.many2many('account.period', 'tms_agreement_account_period_rel', 'agreement_id', 'period_id', 'Accounts for this product'),
		'active': fields.boolean('Active', required=False),
		'travel_wizard': fields.boolean('Travel Created by Wizard'),
		'currency_id': fields.many2one('res.currency','Currency',states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}, required=True),
		'final_cost': fields.float('Final Cost  $', readonly=True,digits=(64,2)), # Este campo va ser dado automaticamente mediante una funcion...
		'indirect_amount': fields.float('Indirect Amount Total  $', readonly=True,digits=(64,2)), # Este campo va ser dado automaticamente mediante una funcion...
		# 'direct_amount': fields.function(_amount_direct_line, method=True, digits_compute= dp.get_precision('Sale Price'),string='Direct Amount $', multi='amount', help="The indirect amount.", store=True),
		# 'taxes_amount_direct': fields.function(_amount_direct_line, method=True, digits_compute= dp.get_precision('Sale Price'),string='Taxes Direct Amount $', multi='amount', help="The indirect amount.", store=True),
		# 'amount_customer': fields.function(_amount_factor, method=True, digits_compute= dp.get_precision('Sale Price'),string='Customer $', multi='factor', help="Total amount for Customer Factor.", store=True),
		# 'amount_customer_factor': fields.function(_amount_factor, method=True, digits_compute= dp.get_precision('Sale Price'),string='Customer Fleet', multi='factor', help="Total amount for Customer Factor.", store=True),
		# 'amount_supplier_factor': fields.function(_amount_factor, method=True, digits_compute= dp.get_precision('Sale Price'),string='Supplier $', multi='factor', help="Total amount for Supplier Factor", store=True),
		# 'amount_driver_factor': fields.function(_amount_factor, method=True, digits_compute= dp.get_precision('Sale Price'),string='Driver $', multi='factor', help="Total amount for Driver Factor", store=True),
		# 'amount_factors': fields.function(_amount_factor, method=True, digits_compute= dp.get_precision('Sale Price'),string='Amount Factors $', multi='factor', help="Total amount for Factors", store=True),
		
		# 'expenses_amount': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'),string='Expenses', multi='sums', help="The Expenses Amount.", store=True),
		# 'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'),string='Lines Amount', multi='sums', help="The amount without tax.", store=True),
		# 'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Taxes', multi='sums', help="The tax amount.", store=True),
		# 'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Lines Taxes', multi='sums', help="The tax amount.", store=True),
		# 'amount_tax_expenses': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Expenses Taxes', multi='sums', help="The tax amount.", store=True),
		# 'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Total (Gain or Loss)', multi='sums', help="The total amount.", store=True),
		# 'amount_subtotal': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Subtotal', multi='sums', help="The subtotal amount.", store=True),

		# 'expenses_amount': fields.float('Expenses', digits=(12,2), help="The Expenses Amount.", store=True),
		# 'amount_untaxed': fields.float('Concepts', digits=(12,2), help="The amount without tax.", store=True),
		# 'amount_tax': fields.float('Taxes Concepts', digits=(12,2), help="The tax amount.", store=True),
		# 'amount_tax': fields.float('Taxes Concepts', digits=(12,2), help="The tax amount.", store=True),
		# 'amount_tax_expenses': fields.float('Expenses Taxes', digits=(12,2), help="The tax amount.", store=True),
		# 'amount_total': fields.float('Total (Gain or Loss)', digits=(12,2), help="The total amount.", store=True),
		# 'amount_subtotal': fields.float('Subtotal', digits=(12,2), help="The subtotal amount.", store=True),

		'product_qty':fields.function(_shipped_product, method=True, string='Sum Qty', type='float', digits=(20, 6),  store=True, multi='product_qty'),
		'product_volume':fields.function(_shipped_product, method=True, string='Sum Volume', type='float', digits=(20, 6),  store=True, multi='product_qty'),
		'product_weight':fields.function(_shipped_product, method=True, string='Sum Weight', type='float', digits=(20, 6),  store=True, multi='product_qty'),
		'product_uom_type':fields.function(_shipped_product, method=True, string='Product UoM Type', type='char', size=64, store=True, multi='product_qty'),
		'hours_start_upload': fields.float('Start to Upload', digits=(16, 2), required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'hours_upload_end_upload': fields.float('Start UpLd to End UpLd', digits=(16, 2), required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'hours_end_upload_lib_docs': fields.float('End UpLd to Lib. Docs. UpLd', digits=(16, 2), required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'hours_lib_docs_prog_download': fields.float('Lib. Docs. UpLd to Prog DwnLd', digits=(16, 2), required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'hours_prog_download_start_download': fields.float('Prog Download to Start DwnLd', digits=(16, 2), required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'hours_start_download_end_download': fields.float('Start Download to End DwnLd', digits=(16, 2), required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'hours_end_download_lib_docs_download': fields.float('End Download to Lib. Docs. DwnLd', digits=(16, 2), required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'hours_lib_docs_download_end_travel': fields.float('Lib. Docs. DwnLd to End Travel', digits=(16, 2), required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'hours_total_travel': fields.function(_get_hours_total, string='Total Time for Travel in Hrs.', method=True, type='float', store=True),
		'date_end_calc': fields.function(_get_date_end, string='Date End', method=True, type='datetime', store=True),
		'date_start_calc': fields.function(_get_date_start, string='Date Start', method=True, type='datetime', store=True),
		'date_start': fields.datetime('Date Star', required=False, select=True,readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'date_end': fields.datetime('Date End', required=False, select=True,readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'agreement_customer_factor': fields.one2many('factor.quotation', 'agreement_id', 'Agreement Customer Charge Factors', domain=[('category', '=', 'customer')], states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}), 
		'agreement_supplier_factor': fields.one2many('factor.quotation', 'agreement_id', 'Agreement Supplier Payment Factors', domain=[('category', '=', 'supplier')], states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'agreement_driver_factor': fields.one2many('factor.quotation', 'agreement_id', 'Agreement Driver Payment Factors', domain=[('category', '=', 'driver')], states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'others_charges_calculate': fields.float('Impuestos  $', states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]},digits=(64,2)),
		'total_calculate': fields.float('Total  $', readonly=True,digits=(64,2)),
		'final_price': fields.float('Final Price  $', digits=(64,2), states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'gain_calculate': fields.float('Gain  $', readonly=True,digits=(64,2)),
		'origin': fields.char('Source Document', size=64, help="Reference of the document that generated this agreement request.",readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'client_order_ref': fields.char('Customer Reference', size=64, readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'state': fields.selection([('draft','Draft'), ('confirmed','Confirmed'), ('done','Done'), ('cancel','Cancelled')], 'Agreement State', readonly=True, help="Gives the state of the agreement. \n -The exception state is automatically set when a cancel operation occurs in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception). \nThe 'Waiting Schedule' state is set when the invoice is confirmed but waiting for the scheduler to run on the date 'Ordered Date'.", select=True),
		'user_id': fields.many2one('res.users', 'Salesman', select=True, readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'partner_id': fields.many2one('res.partner', 'Customer', required=False, change_default=True, select=True, readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', required=True, help="Invoice address for current Agreement.", readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'partner_order_id': fields.many2one('res.partner', 'Ordering Contact', required=True,  help="The name and address of the contact who requested the order or quotation.", readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'departure_address_id': fields.many2one('res.partner', 'Departure Address', required=True, help="Departure address for current Agreement.", readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'arrival_address_id': fields.many2one('res.partner', 'Arrival Address', required=True, help="Arrival address for current Agreement.", readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'upload_point': fields.char('Upload Point', size=128, readonly=False, required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'download_point': fields.char('Download Point', size=128, required=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'agreement_line': fields.one2many('tms.agreement.line', 'agreement_id', 'Agreement Lines', states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'agreement_shipped_product': fields.one2many('tms.agreement.shipped_product', 'agreement_id', 'Shipped Products', states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'agreement_extradata': fields.one2many('tms.waybill.extradata', 'agreement_id', 'Extra Data Fields', states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'agreement_direct_expense_line': fields.one2many('tms.direct.expense', 'agreement_id', 'Expenses Direct', states={'confirmed': [('readonly', False)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'agreement_indirect_expense_line': fields.one2many('tms.indirect.expense', 'agreement_id', 'Expenses Indirect', states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'create_uid' : fields.many2one('res.users', 'Created by', readonly=True),
		'create_date': fields.datetime('Creation Date', readonly=True, select=True),
		'cancelled_by' : fields.many2one('res.users', 'Cancelled by', readonly=True),
		'date_cancelled': fields.datetime('Date Cancelled', readonly=True),
		'confirmed_by' : fields.many2one('res.users', 'Confirmed by', readonly=True),
		'date_confirmed': fields.datetime('Date Confirmed', readonly=True),
		'done_by' : fields.many2one('res.users', 'Done by', readonly=True),
		'date_done': fields.datetime('Date Done', readonly=True),
		'drafted_by' : fields.many2one('res.users', 'Drafted by', readonly=True),
		'date_drafted': fields.datetime('Date Drafted', readonly=True),
		'notes': fields.text('Notes', readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'payment_term': fields.many2one('account.payment.term', 'Payment Term', readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position', readonly=False, states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'company_id': fields.related('shop_id','company_id',type='many2one',relation='res.company',string='Company',store=True,readonly=True),
		'distance_route': fields.function(_get_route_distance, string='Distance (mi./kms)', method=True, type='float', digits=(18,4), help="Route Distance.", store=True),       
		'hours_route': fields.function(_get_route_hours, string='Travel Time (hrs)',method=True, type='float', digits=(18,4), help="Route Hours.", store=True),
		'amount_declared' : fields.float('Amount Declared', digits_compute= dp.get_precision('Sale Price'),states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}, help=" Load value amount declared for insurance purposes..."),
		# 'amount_toll_station_route': fields.function(_amount_factor_route, method=True, digits_compute= dp.get_precision('Sale Price'),string='Amount Toll Station from Route $', multi='route', store=True),
		# 'amount_driver_route': fields.function(_amount_factor_route, method=True, digits_compute= dp.get_precision('Sale Price'),string='Amount Payment Driver from Route $', multi='route', store=True),
		# 'amount_factors_route': fields.function(_amount_factor_route, method=True, digits_compute= dp.get_precision('Sale Price'),string='Amount Factors from Route $', multi='route', store=True),

		'quotation_id': fields.many2one('tms.quotation', ' Quotation', states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
		'waybill_ref_id': fields.many2one('tms.waybill', 'Waibill', readonly=True),

		'departure': fields.boolean('Departure'),
		'departure_2': fields.boolean('Departure'),
		'arrival': fields.boolean('Arrival'),
		'arrival_2': fields.boolean('Arrival'),

	}
	_defaults = {
        'active'                : lambda *a:True,
		'state'                 : lambda *a: 'draft',
		'user_id'               : lambda obj, cr, uid, context: uid,
		'currency_id'           : lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id,
		'partner_invoice_id'    : lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['invoice'])['invoice'],
		'partner_order_id'      : lambda self, cr, uid, context: context.get('partner_id', False) and  self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['contact'])['contact'],
		'departure_address_id'  : lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['delivery'])['delivery'],
		'arrival_address_id'    : lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['delivery'])['delivery'],
		'date'                  : lambda *a: time.strftime( DEFAULT_SERVER_DATETIME_FORMAT),
	}

	_order = "name,id desc"

	##########----------- FUNCIONES SUPER ----------- ##########

	def copy(self, cr, uid, id, default=None, context=None):
		waybill = self.browse(cr, uid, id, context=context)
		if not default:
			default = {}
		default.update({
						'name'          : False, 
						#'unit_ids'      : False, 
						'state'         : 'draft',
						'invoice_id'    : False, 
						'cancelled_by'  : False,
						'date_cancelled': False,
						'approved_by'   : False,
						'date_approved' : False,
						'confirmed_by'  : False,
						'date_confirmed': False,
						'done_by'  : False,
						'date_done': False,
						'drafted_by'    : False,
						'date_drafted'  : False,
						'unit_id'  : False,
						'quotation_id': False,
						'waybill_ref_id': False,
						})
		return super(tms_agreement, self).copy(cr, uid, id, default, context=context)
	########## SUPER A WRITE POR SI NECESITAMOS AGREGAR UN EXTRA AL ACTUALIZAR
	def write(self, cr, uid, ids, vals, context=None):
		s = super(tms_agreement, self).write(cr, uid, ids, vals, context=context)
		# if i <=0:
		# 	self.action_mount_write(cr, uid, ids, context=None)
		# 	i +=1
		return s
	########### SUPER A CREATE PARA OBTENER LA SECUENCIA CORRECTA EN BASE A LA TIENDA Y LA QUE SE TENGA DEFINIDA
	def create(self, cr, uid, vals, context=None):
		shop = self.pool.get('sale.shop').browse(cr, uid, vals['shop_id'])
		seq_id = shop.tms_agreement_seq.id
		if shop.tms_agreement_seq:
			seq_number = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
			vals['name'] = seq_number
		else:
			raise osv.except_osv(_('Travel Sequence Error !'), _('You have not defined Travel Sequence for shop ' + shop.name))
		return super(tms_agreement, self).create(cr, uid, vals, context=context)
		
	########## FUNCION PRINCIPAL LO QUE HACE ES EJECUTAR UNA SERIE DE FUNCIONES EN CADENA PARA OBTENER LOS CALCULOS CORRECTOS, CREACION DE LINEAS DEL ACUERDO, ACTUALIZACION DE LOS DATOS, ETC.
	def action_mount_write(self,cr,uid,ids,context={}):
		context = context or {}
		amount_total = 0.0
		#### INCIAMOS EL CALCULO TOTAL DEL AGREEMENT
		cur_obj = self.pool.get('res.currency')
		res = {}
		for agreement in self.browse(cr, uid, ids, context=context):
			####### CREAMOS UN BARRIDO MANUAL DE LAS LINEAS GASTOS ETC, QUE SON CREADOS MANUALMENTE PARA CALUCLARLOS NUEVAMENTE:

			for lines in agreement.agreement_line:
				if lines.control:
					lines.unlink()
			for expense in agreement.agreement_direct_expense_line:
				if expense.control:
					expense.unlink()
			# for route in agreement.agreement_driver_factor:
			# 	if route.control:
			# 		route.unlink()

			####### INICIAMOS EL CALCULO DE LAS LINEAS GASTOS ETC
			agreement.create_product_fleet_line()
			agreement.create_product_payment_toll_station_line()
			agreement.create_product_payment_driver_line()
			agreement.create_product_payment_supplier_line()

			# ####### ACTUALIZANDO LOS CAMPOS CALCULADOS #####
			# res[agreement.id] = {
			# 	'expenses_amount': 0.0,
			# 	'amount_untaxed': 0.0,
			# 	'amount_tax': 0.0,
			# 	'amount_tax_expenses': 0.0,
			# 	'amount_subtotal': 0.0,
			# 	'amount_total': 0.0,
			# 	'direct_amount': 0.0,
			# 	'taxes_amount_direct': 0.0,

			# }
			# val = val1 = 0.0

			# taxes_expenses = direct_amount = 0.0
			# for direct_line in agreement.agreement_direct_expense_line:
			# 	direct_amount += direct_line.price_total
			# 	taxes_expenses += direct_line.tax_amount
			# 	print "############################### PRODUCTO", direct_line.product_id.name
			# 	print "############################### TXES EXPENSES", taxes_expenses
			# 	print "############################### DIRECT AMOUNT", direct_amount
			# expenses_amount = direct_amount - taxes_expenses

			# #taxes_expenses = agreement.taxes_amount_direct
			# indirect_amount = agreement.indirect_amount
			# #direct_amount = agreement.direct_amount
			# customer_factor= agreement.amount_customer_factor
			# cur = agreement.currency_id
			# indirect_amount = agreement.indirect_amount
			# for line in agreement.agreement_line:
			# 	print "################################## PRODUCTO", line.product_id.name
			# 	print "################################## TOTAL", line.price_subtotal
			# 	val1 += line.price_subtotal
			# 	val += line.tax_amount
			# print "########################### RESULTADO DE LAS LINEAS", val1

			
			# res[agreement.id] ['direct_amount'] = direct_amount
			# res[agreement.id] ['taxes_amount_direct'] = taxes_expenses
			# res[agreement.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
			# res[agreement.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
			# res[agreement.id]['amount_tax_expenses'] = taxes_expenses
			# res[agreement.id] ['expenses_amount'] = expenses_amount
			# res[agreement.id]['amount_subtotal'] = res[agreement.id]['amount_untaxed'] + res[agreement.id]['amount_tax'] 
			# res[agreement.id]['amount_total'] = res[agreement.id]['amount_subtotal'] - direct_amount

			# print "################################# EL RESULTADOOOOOOOOOOOOOOOOOOOOOO SERIA", res
			# print "################################# EL RESULTADOOOOOOOOOOOOOOOOOOOOOO SERIA", res[agreement.id]

		#self.write(cr, uid, ids, res[agreement.id], context)
		# self.message_post(cr, uid, ids, body=_("Total Cost for Agreement = <b><em>%s</em></b>.") % (res[agreement.id]['amount_total']) ,context=context)
		# self.action_mount_refresh(cr, uid, ids, context)
		return True 
######################################### ------------------- #############################################
	# def action_mount_refresh(self,cr,uid,ids,context={}):
	# 	context = context or {}
	# 	amount_total = 0.0
	# 	#### INCIAMOS EL CALCULO TOTAL DEL AGREEMENT
	# 	cur_obj = self.pool.get('res.currency')
	# 	res = {}
	# 	for agreement in self.browse(cr, uid, ids, context=context):

	# 		####### ACTUALIZANDO LOS CAMPOS CALCULADOS #####
	# 		res[agreement.id] = {
	# 			'expenses_amount': 0.0,
	# 			'amount_untaxed': 0.0,
	# 			'amount_tax': 0.0,
	# 			'amount_tax_expenses': 0.0,
	# 			'amount_subtotal': 0.0,
	# 			'amount_total': 0.0,
	# 			'direct_amount': 0.0,
	# 			'taxes_amount_direct': 0.0,

	# 		}
	# 		val = val1 = 0.0

	# 		taxes_expenses = direct_amount = 0.0
	# 		for direct_line in agreement.agreement_direct_expense_line:
	# 			direct_amount += direct_line.price_total
	# 			taxes_expenses += direct_line.tax_amount
	# 		expenses_amount = direct_amount - taxes_expenses

	# 		#taxes_expenses = agreement.taxes_amount_direct
	# 		indirect_amount = agreement.indirect_amount
	# 		#direct_amount = agreement.direct_amount
	# 		customer_factor= agreement.amount_customer_factor
	# 		cur = agreement.currency_id
	# 		indirect_amount = agreement.indirect_amount
	# 		for line in agreement.agreement_line:
	# 			val1 += line.price_subtotal
	# 			val += line.tax_amount
			
	# 		res[agreement.id] ['direct_amount'] = direct_amount
	# 		res[agreement.id] ['taxes_amount_direct'] = taxes_expenses
	# 		res[agreement.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
	# 		res[agreement.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
	# 		res[agreement.id]['amount_tax_expenses'] = taxes_expenses
	# 		res[agreement.id] ['expenses_amount'] = expenses_amount
	# 		res[agreement.id]['amount_subtotal'] = res[agreement.id]['amount_untaxed'] + res[agreement.id]['amount_tax'] 
	# 		res[agreement.id]['amount_total'] = res[agreement.id]['amount_subtotal'] - direct_amount

	# 	self.write(cr, uid, ids, res[agreement.id], context)
	# 	self.message_post(cr, uid, ids, body=_("Total Cost for Agreement = <b><em>%s</em></b>.") % (res[agreement.id]['amount_total']) ,context=context)
	# 	return True 
##################################SUPLIER PAYMENT FACTOR###############################################################

	def create_product_payment_supplier_line (self, cr, uid, ids, context=None):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category', '=', 'freight'),('active','=', 1),('tms_default_supplier_freight','=',True)], limit=1)
		factor_obj = self.pool.get('tms.indirect.expense')
		supplier_list_factor = []
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for Driver Payment,  (tms_category,=,freight),(tms_default_supplier_freight,=,True) !!!'))
		product = prod_obj.browse(cr, uid, prod_id,	 context=None)
		factor = self.pool.get('tms.factor')
		fpos_obj = self.pool.get('account.fiscal.position')

		for agreement in self.browse(cr,uid,ids,context=context):
			for line in agreement.agreement_supplier_factor:
				if line.control:
					line_obj.unlink(cr, uid, [line.id])
			if agreement.agreement_supplier_factor:
				result = self.calculate(cr, uid, 'supplier', ids, 'client', False)
				fpos = agreement.partner_id.property_account_position.id or False
				fpos = fpos and fpos_obj.browse(cr, uid, fpos, context=context) or False
				this = self.get_current_instance(cr, uid, ids)
				vals = (0,0,{
						'agreement_id': this.id,
						'automatic_advance': False,
						'line_type': 'real_expense',
						'name': product[0].name,
						'product_id' : product[0].id,
						'product_uom': product[0].uom_id.id,
						'sequence': False,
						'price_unit': result,
						'product_uom_qty': 1,
						'discount': 0.00,
						'notes': 'Supplier Payment',
						'control': True,
						#'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)])],
						})
				
				supplier_list_factor.append(vals)
				agreement.write({'agreement_direct_expense_line': [x for x in supplier_list_factor]})
				#self.pool.get('tms.direct.expense').create(cr, uid, vals, context)
			else:
				return True
		return True

################################ CREACION DE GASTOS CREADOS EN LA RUTA #################################################################

	def if_exist_product_payment_toll_station (self,cr,uid,id):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category', '=', 'highway_tolls'),('tms_category_default','=',1),('active','=', 1)], limit=1)
		if not prod_id:
								raise osv.except_osv(
			                        _('Error al Crear el Acuerdo !'),
			                        _('No se tiene un producto configurado de tipo Caseta por Defecto'))
		return prod_id

	def create_product_payment_toll_station_line (self, cr, uid, ids, context=None):
		amount_toll_station_route = 0.0
		prod_id = self.if_exist_product_payment_toll_station(cr,uid,ids)
		prod_uom = self.pool.get('product.uom')
		prod_uom_id = self.if_exist_product_uom_id(cr,uid,ids)      
		toll_station_list = []
		for agreement in self.browse(cr,uid,ids,context=context):
			for expense in agreement.agreement_direct_expense_line:
				if expense.product_id.tms_category == 'highway_tolls':
					return True
			for toll in agreement.route_id.tms_route_tollstation_ids:
				amount_axis_credit = 0.0
				amount_axis = 0.0
				if toll.credit:
					for axis in toll.tms_route_tollstation_costperaxis_ids:
						if axis.unit_type_id == agreement.unit_ids:
							amount_axis_credit += axis.cost_credit
				else:
					for axis in toll.tms_route_tollstation_costperaxis_ids:
						if axis.unit_type_id == agreement.unit_ids:
							amount_axis_credit += axis.cost_cash

				amount_toll_station_route = amount_axis_credit + amount_axis

			#for supplier in agreement.agreement_supplier_factor:
			if agreement.route_id.tms_route_tollstation_ids:
				this = self.get_current_instance(cr, uid, ids)
				vals =(0,0,{
						'agreement_id': this.id,
						'automatic_advance': False,
						'line_type': 'real_expense',
						'name': 'Toll Station Payment',
						'sequence': False,
						'product_id': prod_id[0],
						'price_unit': amount_toll_station_route,
						'product_uom_qty': 1,
						'product_uom': prod_uom_id[0],
						'discount': 0.00,
						'notes': 'Toll Station Payment from Route',
						'control': True
						})
				toll_station_list.append(vals)
				agreement.write({'agreement_direct_expense_line': [x for x in toll_station_list]})

				#self.pool.get('tms.direct.expense').create(cr, uid, vals, context)
			else:
				return True
		return True
############################## FACTOR PAYMENT DRIVER###################################################################

	def create_product_payment_driver_line (self, cr, uid, ids, context=None):
		factor_driver_list = []
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category', '=', 'salary'),('tms_default_salary','=',True),('active','=', 1)], limit=1)
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for Driver Payment,  (tms_category,=,salary) and (tms_default_salary=True) !!!'))
		product = prod_obj.browse(cr, uid, prod_id,	 context=None)
		factor = self.pool.get('tms.factor')
		fpos_obj = self.pool.get('account.fiscal.position')

		for agreement in self.browse(cr,uid,ids,context=context):
			if agreement.quotation_id:
				for expense in agreement.agreement_direct_expense_line:
					if expense.line_type == 'salary':
						return True
			if agreement.agreement_driver_factor:
				result = self.calculate(cr, uid, 'salary', ids, 'client', False)
				fpos = agreement.partner_id.property_account_position.id or False
				fpos = fpos and fpos_obj.browse(cr, uid, fpos, context=context) or False
				this = self.get_current_instance(cr, uid, ids)

				taxes_list = []
				for t in product[0].taxes_id:
					
					taxes_list.append(t.id)
				prod_uom_id = self.if_exist_product_uom_id(cr,uid,ids) 
				vals = (0,0,{
						# 'agreement_id': this.id,
						# 'automatic_advance': False,
						# 'line_type': 'real_expense',
						# 'name': product[0].name,
						# 'sequence': 10,
						# 'price_unit': result,
						# 'product_uom_qty': 1,
						# 'discount': 0.00,
						# 'notes': 'Driver Payment',
						# 'control': True,
						# 'product_id' : product[0].id,
						# 'product_uom': product[0].uom_id.id,
						# 'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)])],

						'agreement_id': this.id,
						'automatic_advance': False,
						'line_type': 'real_expense',
						'name': product[0].name,
						'sequence': False,
						'product_id': prod_id[0],
						'price_unit': result,
						'product_uom_qty': 1,
						'product_uom': prod_uom_id[0],
						'discount': 0.00,
						'notes': 'Driver Payment Function',
						'control': True,
						#'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)])],

						})
				factor_driver_list.append(vals)
				agreement.write({'agreement_direct_expense_line': [x for x in factor_driver_list]})
				#self.pool.get('tms.direct.expense').create(cr, uid, vals, context)

			else:
				return True
		return True

	def update_amount_payment_driver (self, cr, uid, ids, context=None):
		this = self.get_current_instance(cr, uid, ids)
		for rec in this:
			for a in rec.agreement_line:
				self.write(cr, uid, ids,{'price_unit':this.amount_driver_factor}) #{'name':seq_number, 'state':'confirmed'}, 'confirmed_by' : uid, 'date_confirmed':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
		return True

	########### FUNCION QUE REFRESCA EL WRITE

	def action_refresh (self,cr,uid,ids,context={}):
		return True

	############ FUNCION QUE CALCULA Y CREA LA LINEA DE FLETE EN BASE AL FACTOR AL CLIENTE

	def create_product_fleet_line (self, cr, uid, ids, context=None):

		prod_obj = self.pool.get('product.product')
#		prod_id = self.if_exist_product_fleet (cr,uid,ids)
		prod_id = prod_obj.search(cr, uid, [('tms_category', '=', 'freight'),('active','=', 1),('tms_default_freight','=',True)], limit=1)
		if not prod_id:
			raise osv.except_osv(
						_('Missing configuration !'),
						_('There is no product defined as Freight !!!'))
		product = prod_obj.browse(cr, uid, prod_id,	 context=None)
		factor = self.pool.get('tms.factor')
		prod_uom = self.pool.get('product.uom')
		fpos_obj = self.pool.get('account.fiscal.position')
		prod_uom_id = self.if_exist_product_uom_id(cr,uid,ids)      
		for agreement in self.browse(cr,uid,ids,context=context):
			if agreement.agreement_customer_factor:
				result = self.calculate(cr, uid, 'agreement', ids, 'client', False)
				fpos = agreement.partner_id.property_account_position.id or False
				fpos = fpos and fpos_obj.browse(cr, uid, fpos, context=context) or False

				this = self.get_current_instance(cr, uid, ids)
				vals = {
						'agreement_id': this.id,
						'automatic_advance': False,
						'line_type': 'product',
						'name': product[0].name,
						'product_id' : product[0].id,
						'product_uom': product[0].uom_id.id,
						'sequence': False,
						'price_unit': result,
						'product_uom_qty': 1,
						'discount': 0.00,
						'notes': 'Fleet',
						'control': True,
						#'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)])],
						}
				self.pool.get('tms.agreement.line').create(cr, uid, vals, context)
			else:
				return True
		return True

	#### APUNTADOR BROWSE HACIA MI CLASE

	def get_current_instance(self, cr, uid, id):
		lines = self.browse(cr,uid,id)
		obj = None
		for i in lines:
			obj = i
		return obj


	########### FUNCION QUE BUSCA LA UNIDAD DE MEDIDA BASADA EN EL NOMBRE UNIDADES
	def if_exist_product_uom_id (self,cr,uid,id):
		prod_uom = self.pool.get('product.uom')
		prod_uom_id = prod_uom.search(cr, uid, [('name','in',('Unit', 'Unit(s)', 'Unidad', 'Unidades'))], limit=1)#,('tms_category', '=', 'fleet')], limit=1)      
		if not prod_uom_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('No se encontro Unidad de Medida Definida como (Unit, Unit(s), Unidad, Unidades) !!!'))
		return prod_uom_id

	########### FUNCION QUE CALCULA EN BASE A FACTORES
	def calculate(self, cr, uid, record_type, record_ids, calc_type=None, travel_ids=False, context=None):
		result = 0.0

		if record_type == 'agreement':

			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):
				for factor in agreement.agreement_customer_factor:
					if factor.factor_type in ('distance', 'distance_real'):
						if not agreement.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for agreement !'),
								_('Agreement %s is not assigned to a Travel') % (agreement.name))
						x = float(agreement.route_id.distance) if factor.factor_type=='distance' else float(agreement.route_id.distance_extraction)

					elif factor.factor_type == 'weight':
						if not agreement.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(agreement.product_weight)

					elif factor.factor_type == 'qty':
						if not agreement.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(agreement.product_qty)

					elif factor.factor_type == 'volume':
						if not agreement.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(agreement.product_volume)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0


		elif record_type == 'salary':

			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):
				for factor in (agreement.agreement_driver_factor):
					if factor.factor_type in ('distance', 'distance_real'):
						if not agreement.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for agreement !'),
								_('Agreement %s is not assigned to a Travel') % (agreement.name))
						x = float(agreement.route_id.distance) if factor.factor_type=='distance' else float(agreement.route_id.distance_extraction)
					elif factor.factor_type == 'weight':
						if not agreement.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(agreement.product_weight)

					elif factor.factor_type == 'qty':
						if not agreement.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(agreement.product_qty)

					elif factor.factor_type == 'volume':
						if not agreement.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(agreement.product_volume)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0

		elif record_type == 'salary_route':

			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):
				for factor in (agreement.route_id.expense_driver_factor):
					if factor.factor_type in ('distance', 'distance_real'):
						if not agreement.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for agreement !'),
								_('Agreement %s is not assigned to a Travel') % (agreement.name))
						x = float(agreement.route_id.distance) if factor.factor_type=='distance' else float(agreement.route_id.distance_extraction)
					elif factor.factor_type == 'weight':
						if not agreement.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(agreement.product_weight)

					elif factor.factor_type == 'qty':
						if not agreement.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(agreement.product_qty)

					elif factor.factor_type == 'volume':
						if not agreement.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(agreement.product_volume)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0

		elif record_type == 'supplier':

			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):
				for factor in (agreement.agreement_supplier_factor):
					if factor.factor_type in ('distance', 'distance_real'):
						if not agreement.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for agreement !'),
								_('Agreement %s is not assigned to a Travel') % (agreement.name))
						x = float(agreement.route_id.distance) if factor.factor_type=='distance' else float(agreement.route_id.distance_extraction)
					elif factor.factor_type == 'weight':
						if not agreement.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(agreement.product_weight)

					elif factor.factor_type == 'qty':
						if not agreement.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(agreement.product_qty)

					elif factor.factor_type == 'volume':
						if not agreement.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(agreement.product_volume)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0

		elif record_type == 'expense' and travel_ids:
			travel_obj = self.pool.get('tms.travel')
			for travel in travel_obj.browse(cr, uid, travel_ids, context=context):
				res1 = res2 = weight = qty = volume = x = 0.0
				if travel.agreement_ids:
					for agreement in travel.agreement_ids:
						res1 += self.calculate(cr, uid, 'agreement', [agreement.id], 'driver', travel_ids=False)
						weight  += agreement.product_weight
						qty	 += agreement.product_qty
						volume  += agreement.product_volume
				if not res1:
					for factor in travel.expense_driver_factor:						
						if factor.factor_type == 'distance':
							x = float(travel.route_id.distance) if factor.factor_type=='distance' else float(travel.route_id.distance_extraction)

						elif factor.factor_type == 'weight':							
							if not weight:
								raise osv.except_osv(
									_('Could calculate Freight Amount !'),
									_('Agreements related to Travel %s has no Products with UoM Category = Weight or Product Qty = 0.0') % (travel.name))
							x = float(weight)

						elif factor.factor_type == 'qty':
							if not qty:
								raise osv.except_osv(
									_('Could calculate Freight Amount !'),
									_('Agreements related to Travel %s has no Products with Quantity > 0.0') % (travel.name))
							x = float(qty)

						elif factor.factor_type == 'volume':
							if not volume:
								raise osv.except_osv(
									_('Could calculate Freight Amount !'),
									_('Agreements related to Travel %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (travel.name))
							x = float(volume)

						elif factor.factor_type == 'travel':
							x = 0.0

						elif factor.factor_type == 'special':
							exec factor.factor_special_id.python_code
							
						res2 = ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0
				result += res1 + res2

		return result

	####################
	def action_test_print(self, cr, uid, ids, context=None):
		amount_toll_station_route = amount_driver_route = amount_factors_route = 0.0
		product_obj = self.pool.get('product.product')
		for agreement in self.browse(cr, uid, ids, context=context):
			
			for toll in agreement.route_id.tms_route_tollstation_ids:
				amount_axis = 0.0
				for axis in toll.tms_route_tollstation_costperaxis_ids:
					amount_axis += axis.cost_credit + axis.cost_cash
				amount_toll_station_route += amount_axis
			for route in agreement.route_id.expense_driver_factor:
				amount_driver_route +=route.total_amount + route.fixed_amount
		return True


	def action_confirmed(self, cr, uid, ids, context=None):
		self.action_mount_write(cr,uid,ids)
		self.write(cr, uid, ids,{'state':'confirmed', 'confirmed_by' : uid, 'date_confirmed':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}) #{'name':seq_number, 'state':'confirmed'}, 'confirmed_by' : uid, 'date_confirmed':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
		for obj in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [obj.id], body=_("Agreement <em>%s</em> <b>confirmed</b>.") % (obj.name),  context=context)
		return True


	def action_draft(self, cr,uid,ids,context={}):
		self.action_mount_write(cr,uid,ids)
		self.write(cr, uid, ids, {'state':'draft', 'drafted_by':uid,'date_drafted':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
		for obj in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [obj.id], body=_("Agreement <em>%s</em> <b>drafted </b>.") % (obj.name) ,context=context)
		return True


	def action_done(self,cr,uid,ids,context={}): 
		for rec in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [rec.id], body=_("Agreement <em>%s</em> <b>done</b>.") % (rec.name),  context=context)
		self.write(cr, uid, ids, {'state':'done','done_by':uid,'date_done':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})        
		return True    


	def action_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'cancel', 'cancelled_by':uid,'date_cancelled':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
		waybill_obj = self.pool.get('tms.waybill')
		waybill_id = waybill_obj.search(cr, uid,[('agreement_id','=',ids[0])])
		# if waybill_id:
		# 	for waybill in waybill_obj.browse(cr, uid, waybill_id, context):
		# 		if waybill.state != 'cancel':
		# 			raise osv.except_osv(
	 #                            _('Error!'),
	 #                            _('No se puede cancelar el Acuerdo, debe cancelar primero la Carta Porte Generada %s') % (waybill.name))
		for obj in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [obj.id], body=_("Agreement <em>%s</em> <b>cancelled</b>.") % (obj.name),  context=context)
		return True


	def on_factors_route(self, cr, uid, ids, route_id, context=None):
		factor_driver_list = []
		result = {}
		
		for rec in self.browse(cr, uid, ids, context=context):
			for agr in rec.agreement_driver_factor:
				if agr.control:
					agr.unlink()
		for route in self.pool.get('tms.route').browse(cr, uid, [route_id], context):
			if route.expense_driver_factor:
				product_obj = self.pool.get('product.product')
				product_id = product_obj.search(cr, uid, [('tms_category', '=', 'freight'),('tms_default_freight','=',True),('active','=', 1)], limit=1)
				product_browse = product_obj.browse(cr, uid, product_id, context=context)[0]
				for factor in route.expense_driver_factor:
					
					xline_factor = (0,0,{
							    		'name'          : product_browse.name,
								        'category'      : factor.category,
								        'factor_type'   : factor.factor_type,
								        'framework'     : factor.framework if factor.framework else False,
								        'range_start'   : factor.range_start if factor.range_start else 0.0,
								        'range_end'     : factor.range_end if factor.range_end else 0.0,
								        'factor'        : factor.factor if factor.factor else False,
								        'fixed_amount'  : factor.fixed_amount if factor.fixed_amount else 0.0,
								        'mixed'         : factor.mixed if factor.mixed else False,
								        'factor_special_id': factor.factor_special_id.id if factor.factor_special_id.id else False,
								        'variable_amount' : factor.variable_amount if factor.variable_amount else False,
								        'total_amount'  : factor.total_amount if factor.total_amount else 0.0,
								        'sequence'      : 0,
								        'notes'         : "Factor cargado de la ruta "+route.name,
								        'control'       : True,### Revisar si es necesario eliminarlo
								        'driver_helper' : False,

							})

					factor_driver_list.append(xline_factor)
					
#				shop.write({'salesman_information_ids' : [x for x in employees_list] })
			else:
				return {}
#		self.dummy_button(cr, uid, ids)
		return {'value' : {'agreement_driver_factor' : [x for x in factor_driver_list]}}



	def onchange_partner_id(self, cr, uid, ids, partner_id):
		if not partner_id:
			return {'value': {'partner_invoice_id': False, 
							  'partner_order_id': False, 
							  'payment_term': False, 
							  #'pricelist_id': False,
							  #'currency_id': False, 
							  'user_id': False}
					}
		addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['invoice', 'contact', 'default', 'delivery'])
		part = self.pool.get('res.partner').browse(cr, uid, partner_id)
		pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
		payment_term = part.property_payment_term and part.property_payment_term.id or False
		dedicated_salesman = part.user_id and part.user_id.id or uid
		val = {
			'partner_invoice_id': addr['invoice'] if addr['invoice'] else addr['default'],
			'partner_order_id': addr['contact'] if addr['contact'] else addr['default'],
			'payment_term': payment_term,
			'user_id': dedicated_salesman,
			#'pricelist_id': pricelist,
			#'currency_id': currency,
		}
		return {'value': val}

	def onchange_days_need(self,cr,uid,ids,hours):
		res = {'value':{'days_need':self._get_days_need(hours)},'warnin':{}}
		return res

	def button_calculate_gain(self, cr, uid, ids, context=None):
		return True


#############################################################################################
	_sql_constraints = [
		('name_uniq', 'unique(name)', 'Agreement must be unique !'),
	]

	_order = 'id desc'

	def _check_dates(self, cr, uid, ids, context=None):
		for agreement in self.browse(cr,uid,ids):
			date_start = agreement.date_start
			date_end = agreement.date_end
			if date_start:
				if date_end:
					if date_start < date_end:
						return True
				if not date_end:
					return True
		return False

	def _check_factors(self, cr, uid, ids, context=None):
		for agreement in self.browse(cr,uid,ids):
			d = 0
			c = 0
			s = 0
			for driver in agreement.agreement_driver_factor:
				d += 1
			for customer in agreement.agreement_customer_factor:
				c +=1
			for supplier in agreement.agreement_supplier_factor:
				s += 1
			if d > 1 or c  > 1 or s > 1:
				return False
		return True

	_constraints = [
		(_check_dates, 'Error ! You can not create Agreement start date is greater than the end date ', ['Fecha Inicio']),
		(_check_factors, 'Error ! No se puede definir mas de 1 linea por cada Factor Asignado ', ['Factores'])
	]


tms_agreement()

class tms_agreement_shipped_product(osv.Model):
	_name = 'tms.agreement.shipped_product'
	_description = 'Agreement Shipped Product'


	_columns = {
		'agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
		'name': fields.char('Description', size=256, required=True, select=True),
		'product_id': fields.many2one('product.product', 'Product', 
							domain=[
									('tms_category', '=','transportable'), 
									('tms_category', '=','move'), 
									('tms_category', '=','insurance'), 
									('tms_category', '=','highway_tolls'), 
									('tms_category', '=','other'),
									], change_default=True, required=True),
		'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
		'product_uom_qty': fields.float('Quantity (UoM)', digits=(16, 2), required=True),
		'notes': fields.text('Notes'),
		'agreement_partner_id': fields.related('agreement_id', 'partner_id', type='many2one', relation='res.partner', store=True, string='Customer'),
		'salesman_id':fields.related('agreement_id', 'user_id', type='many2one', relation='res.users', store=True, string='Salesman'),
		'shop_id': fields.related('agreement_id', 'shop_id', type='many2one', relation='sale.shop', string='Shop', store=True, readonly=True),
		'company_id': fields.related('agreement_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
		'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
	}
	_order = 'sequence, id desc'
	_defaults = {
		'product_uom_qty': 1,
		'sequence': 10,
	}

	def on_change_product_id(self, cr, uid, ids, product_id):
		res = {}
		if not product_id:
			return {}
		prod_obj = self.pool.get('product.product')
		for product in prod_obj.browse(cr, uid, [product_id], context=None):            
			res = {'value': {'product_uom' : product.uom_id.id,
							 'name': product.name}
				}
		return res



tms_agreement_shipped_product()


class tms_agreement_line(osv.Model):
	_name = 'tms.agreement.line'
	_description = 'Agreement Line'


	def _amount_line(self, cr, uid, ids, field_name, args, context=None):
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		res = {}
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			price = line.price_unit - line.price_unit *  (line.discount or 0.0) / 100.0
			taxes = tax_obj.compute_all(cr, uid, line.product_id.taxes_id, price, line.product_uom_qty, line.agreement_id.partner_invoice_id.id, line.product_id, line.agreement_id.partner_id)
			cur = line.agreement_id.currency_id

			amount_with_taxes = cur_obj.round(cr, uid, cur, taxes['total_included'])
			amount_tax = cur_obj.round(cr, uid, cur, taxes['total_included']) - cur_obj.round(cr, uid, cur, taxes['total'])
			
			price_subtotal = line.price_unit * line.product_uom_qty
			price_discount = price_subtotal * (line.discount or 0.0) / 100.0
			res[line.id] =  {   'price_total'   : amount_with_taxes,
								'price_amount': price_subtotal,
								'price_discount': price_discount,
								'price_subtotal': (price_subtotal - price_discount),
								'tax_amount'    : amount_tax,
								}
		return res



	_columns = {
		'agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
		'line_type': fields.selection([('product', 'Product'),('note', 'Note'),], 'Line Type', require=True),

		'name': fields.char('Description', size=256, required=True),
		'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
		'product_id': fields.many2one('product.product', 'Product', 
							domain=[('sale_ok', '=', True),
									('tms_category', '=','freight'), 
									('tms_category', '=','move'), 
									('tms_category', '=','insurance'), 
									('tms_category', '=','highway_tolls'), 
									('tms_category', '=','other'),
									], change_default=True),
		'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Sale Price')),
		'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'price_amount': fields.function(_amount_line, method=True, string='Price Amount', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'price_discount': fields.function(_amount_line, method=True, string='Discount', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'price_total'   : fields.function(_amount_line, method=True, string='Total Amount', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'tax_amount'   : fields.function(_amount_line, method=True, string='Tax Amount', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'tax_id': fields.many2many('account.tax', 'agreement_tax', 'agreement_line_id', 'tax_id', 'Taxes'),
		'product_uom_qty': fields.float('Quantity (UoM)', digits=(16, 2)),
		'product_uom': fields.many2one('product.uom', 'Unit of Measure '),
		'discount': fields.float('Discount (%)', digits=(16, 2), help="Please use 99.99 format..."),
		'notes': fields.text('Notes'),
		'agreement_partner_id': fields.related('agreement_id', 'partner_id', type='many2one', relation='res.partner', store=True, string='Customer'),
		'salesman_id':fields.related('agreement_id', 'user_id', type='many2one', relation='res.users', store=True, string='Salesman'),
		'company_id': fields.related('agreement_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
		'control': fields.boolean('Control'),
	}
	_order = 'sequence, id desc'

	_defaults = {
		'line_type': 'product',
		'discount': 0.0,
		'product_uom_qty': 1,
		'sequence': 10,
		'price_unit': 0.0,
	}


	def on_change_product_id(self, cr, uid, ids, product_id):
		res = {}
		if not product_id:
			return {}
		prod_obj = self.pool.get('product.product')
		for product in prod_obj.browse(cr, uid, [product_id], context=None):
			
			for x in product.taxes_id:
				print x.id
			res = {'value': {'product_uom' : product.uom_id.id,
							 'name': product.name,
							 'tax_id': [(6, 0, [x.id for x in product.taxes_id])],
							}
				}
		return res

	def on_change_amount(self, cr, uid, ids, product_uom_qty, price_unit, discount, product_id):
		res = {'value': {
					'price_amount': 0.0, 
					'price_subtotal': 0.0, 
					'price_discount': 0.0, 
					'price_total': 0.0,
					'tax_amount': 0.0, 
						}
				}
		if not (product_uom_qty and price_unit and product_id ):
			return res
		tax_factor = 0.00
		prod_obj = self.pool.get('product.product')
		for line in prod_obj.browse(cr, uid, [product_id], context=None)[0].taxes_id:
			tax_factor = (tax_factor + line.amount) if line.amount <> 0.0 else tax_factor
		price_amount = price_unit * product_uom_qty
		price_discount = (price_unit * product_uom_qty) * (discount/100.0)
		res = {'value': {
					'price_amount': price_amount, 
					'price_discount': price_discount, 
					'price_subtotal': (price_amount - price_discount), 
					'tax_amount': (price_amount - price_discount) * tax_factor, 
					'price_total': (price_amount - price_discount) * (1.0 + tax_factor),
						}
				}
		return res

tms_agreement_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
