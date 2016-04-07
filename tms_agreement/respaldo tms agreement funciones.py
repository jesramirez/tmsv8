	def action_mount_write(self,cr,uid,ids,context={}):
		factor_obj = self.pool.get('tms.indirect.expense')
		context = context or {}
		amount_total = 0.0
		for rec in self.browse(cr,uid,ids,context=context):
		# 	rec.write({})
			for lines in rec.agreement_line:
				if lines.control:
					lines.unlink()
			for expense in rec.agreement_direct_expense_line:
				if expense.control:
					expense.unlink()
			for route in rec.agreement_driver_factor:
				if route.control:
					route.unlink()
			rec.create_product_fleet_line()
#			self.create_product_payment_supplier_line(cr, uid, ids) ### ESTO LO AGREGUE HOY
			rec.create_product_payment_driver_line()
			rec.create_product_payment_toll_station_line()
			rec.create_factor_driver_route_line()

		for r in self.browse(cr,uid,ids,context=context):
			amount_total = r.amount_total
			self.action_refresh(cr,uid,ids)
		#	r.action_calculate_indirect_mount()
		self.message_post(cr, uid, ids, body=_("Total Cost for Agreement = <b><em>%s</em></b>.") % (amount_total) ,context=context)
		return True 

############### REVISAR FUNCIONES PARA PODER GENERAR TODO DE UN JALON
	def write(self, cr, uid, ids, vals, context=None):
		super(tms_agreement, self).write(cr, uid, ids, vals, context=context)
		for rec in self.browse(cr,uid,ids):
			for lines in rec.agreement_line:
				if lines.control:
					lines.unlink()
			for expense in rec.agreement_direct_expense_line:
				if expense.control:
					expense.unlink()
			for route in rec.agreement_driver_factor:
				if route.control:
					route.unlink()
			self.create_product_fleet_line(cr,uid,ids)
#			self.create_product_payment_supplier_line(cr, uid, ids) ### ESTO LO AGREGUE HOY
			self.create_product_payment_driver_line(cr,uid,ids)
			self.create_product_payment_toll_station_line(cr,uid,ids)
			self.create_factor_driver_route_line(cr,uid,ids)
			for refres in self.browse(cr,uid,ids):
				self.action_refresh(cr,uid,ids)
		return True

##################################### FUNCION QUE ELIMINA LAS LINEAS Y GASTOS CREADOS POR FUNCIONES ########################
	def action_drop_lines_control (self, cr,uid,ids,context={}):
		for agreement in self.browse(cr,uid,ids):
			for lines in agreement.agreement_line:
				if lines.control:
					lines.unlink()
			for expense in agreement.agreement_direct_expense_line:
				if expense.control:
					expense.unlink()
		return True		

	def create_lines_factors (self, cr, uid, ids, context=None):
		self.create_product_fleet_line(cr,uid,ids)
#		self.create_product_payment_supplier_line(cr, uid, ids) ### ESTO LO AGREGUE HOY
		self.create_product_payment_driver_line(cr,uid,ids)
		self.create_product_payment_toll_station_line 
		self.create_factor_driver_route_line
		return True

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
						})
		return super(tms_agreement, self).copy(cr, uid, id, default, context=context)


################################################ BUTTONS ACTIONS ###################################
	def action_calculate_indirect_mount(self, cr,uid,ids,context={}):
		amount_total_rec = amount_not_automatic = 0.0
		indirect_expense = self.pool.get('tms.indirect.expense').browse (cr, uid, ids)
		for rec in self.browse(cr, uid, ids):
# 			print "productos: ",tuple(w.product_id.id for w in rec.agreement_indirect_expense_line)
# 			print "periodos: ", tuple(x.id for x in rec.account_periods_ids)
# 			for product in rec.agreement_indirect_expense_line:
# 				suma = suma01 = 0.0
# 				if product.automatic:             
# #					cr.execute("""
# #						select sum(account_monthly_balance.debit-account_monthly_balance.credit) as saldo 
# #							from account_monthly_balance, tms_indirect_expense, account_period, tms_agreement 
# #							where account_id in ( 
# #							select tms_product_account_rel.account_id 
# #							from tms_product_account_rel
# #							where tms_product_account_rel.product_id = %s 
# #							) and account_monthly_balance.period_id in ( 
# #							select period_id from tms_agreement_account_period_rel 
# #							where agreement_id=%s order by period_id 
# #							)""", (product.product_id.id, rec.id))
# #					suma = cr.fetchall()
# 					print "EL resultado de la suma de las cuentas es igual a ::::::", suma
# #					print "El resultado del query es ::::::::::::::::::::::::::::", cr.fetchall()
# 					suma01 = suma[0][0]
# 					if suma01 == 0 or suma01 == None:
# 						suma01 = 0.0
# 					print "EL resultado de la suma de las cuentas es igual a ::::::", suma01
# 					product.write( {'total_mount_indirect':suma01})
# #					print product.product_id.name, " = ", suma[0][0]
# 					amount_total_rec = suma01 + amount_total_rec
# 				else:
# 					print "El gasto indirecto es de: ", product.total_mount_indirect
# 					amount_not_automatic = product.total_mount_indirect + amount_not_automatic
# 			total_expenses = amount_total_rec + amount_not_automatic            
# 			print "TOTAL ", " = ", amount_total_rec
# 			print "TOTAL ", " = ", amount_not_automatic
# 			print "TOTAL ", " = ", amount_total_rec + amount_not_automatic
# 			print "TOTAL ", " = ", total_expenses

# 			print "#######################******************----------"
				rec.write({'indirect_amount':0.0})
			#self.message_post(cr, uid, ids, body=_("Indirect Amount = <b><em>%s</em></b>.") % (rec.indirect_amount) ,context=context)
		return True

###########################################FUNCION QUE ELIMINA TODOS LOS GASTOS 

	def unlink_indirect_expenses (self, cr, uid, ids, context=None):
		line_obj = self.pool.get('tms.indirect.expense')
		for agreement in  self.browse(cr, uid, ids):
			for line in agreement.agreement_indirect_expense_line:
				line.unlink()
		return True

	def create(self, cr, uid, vals, context=None):
		shop = self.pool.get('sale.shop').browse(cr, uid, vals['shop_id'])
		seq_id = shop.tms_agreement_seq.id
		if shop.tms_agreement_seq:
			seq_number = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
			vals['name'] = seq_number
		else:
			raise osv.except_osv(_('Travel Sequence Error !'), _('You have not defined Travel Sequence for shop ' + shop.name))
		return super(tms_agreement, self).create(cr, uid, vals, context=context)

	def get_current_instance(self, cr, uid, id):
		lines = self.browse(cr,uid,id)
		obj = None
		for i in lines:
			obj = i
		return obj


	def create_product_ (self, cr, uid, ids, context=None):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category','=','freight'),('tms_default_freight','=',True)], limit=1)#,('tms_category', '=', 'fleet')], limit=1)
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for freight  tms_category = Freight and Default!!!'))
		return True

######################## FACTOR PAYMENT CUSTOMER#######################
	def if_exist_unit_of_messure_category (self,cr,uid,id):
		prod_uom_cat = self.pool.get('product.uom.categ')
		prod_uom_cat_id = prod_uom_cat.search(cr, uid, [('name','in',('Unit', 'Unit(s)', 'Unidad', 'Unidades'))], limit=1)#,('tms_category', '=', 'fleet')], limit=1)      
		if not prod_uom_cat_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('It was found measuring unit Unit Type !!!'))
		return prod_uom_cat_id

	def if_exist_product_uom_id (self,cr,uid,id):
		prod_uom = self.pool.get('product.uom')
		prod_uom_id = prod_uom.search(cr, uid, [('name','in',('Unit', 'Unit(s)', 'Unidad', 'Unidades'))], limit=1)#,('tms_category', '=', 'fleet')], limit=1)      
		if not prod_uom_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('It was found measuring unit Unit Type !!!'))
		return prod_uom_id

	def if_exist_product_fleet (self,cr,uid,id):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category','=','freight'),('tms_default_freight','=',True)], limit=1)#,('tms_category', '=', 'fleet')], limit=1)
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for freight  tms_category = Freight !!!'))
		return prod_id


	def create_product_fleet_line (self, cr, uid, ids, context=None):
		print "############################################"
		print "########################################### CREANDO NUEVAMENTE LA LINEA DEL FLETE"
		print "########################################### CREANDO NUEVAMENTE LA LINEA DEL FLETE"
		print "########################################### CREANDO NUEVAMENTE LA LINEA DEL FLETE"
		print "########################################### CREANDO NUEVAMENTE LA LINEA DEL FLETE"


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
			for line in agreement.agreement_line:
				if line.control:
					line.unlink()
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
						'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)])],
						}
				self.pool.get('tms.agreement.line').create(cr, uid, vals, context)
			else:
				return True
		return True

	def calculate(self, cr, uid, record_type, record_ids, calc_type=None, travel_ids=False, context=None):
		result = 0.0

		if record_type == 'agreement':
			print "==================================="
			print "Calculando"
			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):
				print "Recorriendo agreements"
				for factor in agreement.agreement_customer_factor:
					print "Recorriendo factors"
					print "Tipo de factor: ", factor.factor_type
					if factor.factor_type in ('distance', 'distance_real'):
						print "Tipo Distancia"
						print "####################################################### DISTANCIA"
						if not agreement.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for agreement !'),
								_('agreement %s is not assigned to a Travel') % (agreement.name))
						print agreement.route_id.distance
						x = (float(agreement.route_id.distance) if factor.factor_type=='distance' else float(agreement.route_id.distance_extraction)) if factor.framework == 'Any' or factor.framework == agreement.route_id.framework else 0.0

					elif factor.factor_type == 'weight':
						print "agreement.product_weight", agreement.product_weight
						print "####################################################### PESO"
						if not agreement.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(agreement.product_weight)

					elif factor.factor_type == 'qty':
						if not agreement.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(agreement.product_qty)

					elif factor.factor_type == 'volume':
						if not agreement.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(agreement.product_volume)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						print "# TRAVELLLLLLLLLLLLLLLLLLLLLLLLLL ###########################3", factor.fixed_amount
						print "# TRAVELLLLLLLLLLLLLLLLLLLLLLLLLL ###########################3", factor.fixed_amount
						print "# TRAVELLLLLLLLLLLLLLLLLLLLLLLLLL ###########################3", factor.fixed_amount
						print "# TRAVELLLLLLLLLLLLLLLLLLLLLLLLLL ###########################3", factor.fixed_amount
						print "# TRAVELLLLLLLLLLLLLLLLLLLLLLLLLL ###########################3", factor.fixed_amount
						print "# TRAVELLLLLLLLLLLLLLLLLLLLLLLLLL ###########################3", factor.fixed_amount
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0
					print "factor.fixed_amount : ", factor.fixed_amount
					print "factor.mixed : ", factor.mixed
					print "factor.factor_type : ", factor.factor_type
					print "factor.factor : ", factor.factor
					print "x : ", x



		elif record_type == 'salary':
			print "==================================="
			print "Calculando"
			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):
				print "Recorriendo agreements"
				for factor in (agreement.agreement_driver_factor):
					print "Recorriendo factors"
					print "Tipo de factor: ", factor.factor_type
					if factor.factor_type in ('distance', 'distance_real'):
						print "Tipo Distancia"
						print "####################################################### DISTANCIA"
						if not agreement.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for agreement !'),
								_('agreement %s is not assigned to a Travel') % (agreement.name))
						print agreement.route_id.distance
						x = (float(agreement.route_id.distance) if factor.factor_type=='distance' else float(agreement.route_id.distance_extraction)) if factor.framework == 'Any' or factor.framework == agreement.route_id.framework else 0.0
					elif factor.factor_type == 'weight':
						print "agreement.product_weight", agreement.product_weight
						if not agreement.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(agreement.product_weight)

					elif factor.factor_type == 'qty':
						if not agreement.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(agreement.product_qty)

					elif factor.factor_type == 'volume':
						if not agreement.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(agreement.product_volume)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0
					print "##################### FINALIZANDOOOO EL CALCULO DE FACTOR POR CLIENTE"
					print "factor.fixed_amount : ", factor.fixed_amount
					print "factor.mixed : ", factor.mixed
					print "factor.factor_type : ", factor.factor_type
					print "factor.factor : ", factor.factor
					print "x : ", x


		elif record_type == 'salary_route':
			print "==================================="
			print "Calculando"
			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):
				print "Recorriendo agreements"
				for factor in (agreement.route_id.expense_driver_factor):
					print "Recorriendo factors"
					print "Tipo de factor: ", factor.factor_type
					if factor.factor_type in ('distance', 'distance_real'):
						print "Tipo Distancia"
						print "####################################################### DISTANCIA"
						if not agreement.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for agreement !'),
								_('agreement %s is not assigned to a Travel') % (agreement.name))
						print agreement.route_id.distance
						x = (float(agreement.route_id.distance) if factor.factor_type=='distance' else float(agreement.route_id.distance_extraction)) if factor.framework == 'Any' or factor.framework == agreement.route_id.framework else 0.0
					elif factor.factor_type == 'weight':
						print "agreement.product_weight", agreement.product_weight
						if not agreement.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(agreement.product_weight)

					elif factor.factor_type == 'qty':
						if not agreement.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(agreement.product_qty)

					elif factor.factor_type == 'volume':
						if not agreement.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(agreement.product_volume)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0
					print "factor.fixed_amount : ", factor.fixed_amount
					print "factor.mixed : ", factor.mixed
					print "factor.factor_type : ", factor.factor_type
					print "factor.factor : ", factor.factor
					print "x : ", x



		elif record_type == 'supplier':
			print "==================================="
			print "Calculando"
			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):
				print "Recorriendo agreements"
				for factor in (agreement.agreement_supplier_factor):
					print "Recorriendo factors"
					print "Tipo de factor: ", factor.factor_type
					if factor.factor_type in ('distance', 'distance_real'):
						print "Tipo Distancia"
						print "####################################################### DISTANCIA"
						if not agreement.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for agreement !'),
								_('agreement %s is not assigned to a Travel') % (agreement.name))
						print agreement.route_id.distance
						x = (float(agreement.route_id.distance) if factor.factor_type=='distance' else float(agreement.route_id.distance_extraction)) if factor.framework == 'Any' or factor.framework == agreement.route_id.framework else 0.0
					elif factor.factor_type == 'weight':
						print "agreement.product_weight", agreement.product_weight
						if not agreement.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(agreement.product_weight)

					elif factor.factor_type == 'qty':
						if not agreement.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(agreement.product_qty)

					elif factor.factor_type == 'volume':
						if not agreement.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(agreement.product_volume)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0
					print "factor.fixed_amount : ", factor.fixed_amount
					print "factor.mixed : ", factor.mixed
					print "factor.factor_type : ", factor.factor_type
					print "factor.factor : ", factor.factor
					print "x : ", x


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
							x = (float(travel.route_id.distance) if factor.factor_type=='distance' else float(travel.route_id.distance_extraction)) if factor.framework == 'Any' or factor.framework == travel.framework else 0.0

						elif factor.factor_type == 'weight':							
							if not weight:
								raise osv.except_osv(
									_('Could calculate Freight Amount !'),
									_('agreements related to Travel %s has no Products with UoM Category = Weight or Product Qty = 0.0') % (travel.name))
							x = float(weight)

						elif factor.factor_type == 'qty':
							if not qty:
								raise osv.except_osv(
									_('Could calculate Freight Amount !'),
									_('agreements related to Travel %s has no Products with Quantity > 0.0') % (travel.name))
							x = float(qty)

						elif factor.factor_type == 'volume':
							if not volume:
								raise osv.except_osv(
									_('Could calculate Freight Amount !'),
									_('agreements related to Travel %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (travel.name))
							x = float(volume)

						elif factor.factor_type == 'travel':
							x = 0.0

						elif factor.factor_type == 'special':
							exec factor.factor_special_id.python_code
							
						res2 = ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0
				result += res1 + res2
		print "result :", result

		return result

    
#########################################BORRAR LOS REGISTROS AL HACER UN DRAFT #################

	def unlink_lines_fleet_driver_supplier (self, cr, uid, ids, context=None):
		line_obj = self.pool.get('tms.agreement.line')
		for agreement in  self.browse(cr, uid, ids):
			for line in agreement.agreement_line:
				payment = line_obj.search(cr, uid, [('name','in',('Driver Payment', 'Pago al Operador'))], limit=2)
				supplier = line_obj.search(cr, uid, [('name','in',('Supplier Payment', 'Pago a Proveedores'))], limit=2)
				if payment:
					line.unlink()
				elif supplier:
					line.unlink()
		return True


############################## FACTOR PAYMENT DRIVER###################################################################

	def if_exist_product_payment_driver (self,cr,uid,id):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category','=','salary')], limit=1)#,('tms_category', '=', 'fleet')], limit=1)
		print "PAYYYYYYYYYYMMMMMMMMMMMMMMMEEEEEEEEENNNNNNNNTTT DDDDDRRRIIIIIIIVVVVVVEEEEERRRRR", prod_id
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for Driver Payment,  (tms_category,=,salary) !!!'))
#			self.create_product_payment_driver(cr,uid,id)
#			prod_id = prod_obj.search(cr, uid, [('name','in',('Driver Payment', 'Pago al Operador'))], limit=1)#,('tms_category', '=', 'fleet')], limit=1)
#			print "ID de BUSQUEDA despues de crear el producto es: : : : : :", prod_id
		return prod_id

	def create_product_payment_driver_line (self, cr, uid, ids, context=None):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category', '=', 'salary'),('active','=', 1)], limit=1)
		factor_obj = self.pool.get('tms.indirect.expense')
		print "################################################## CREANDO EL PAGO DEL OPERADORRRRRRRRRRRRRR NECESITAMOS CALCULARLO CON LOS FACTORES"
		print "################################################## CREANDO EL PAGO DEL OPERADORRRRRRRRRRRRRR NECESITAMOS CALCULARLO CON LOS FACTORES"
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for Driver Payment,  (tms_category,=,salary) !!!'))
		product = prod_obj.browse(cr, uid, prod_id,	 context=None)
		factor = self.pool.get('tms.factor')
		fpos_obj = self.pool.get('account.fiscal.position')

		for agreement in self.browse(cr,uid,ids,context=context):
			print "##################################### DENTRO DEL PAGO OPERADOR BROWSE"
			print "##################################### DENTRO DEL PAGO OPERADOR BROWSE"
			for line in agreement.agreement_driver_factor:
				if line.control:
					line_obj.unlink(cr, uid, [line.id])
			if agreement.agreement_driver_factor:
				print "################################################ AGREEMENT PAYMENT DRIVER FACTOR", agreement.agreement_driver_factor
				result = self.calculate(cr, uid, 'salary', ids, 'client', False)
				fpos = agreement.partner_id.property_account_position.id or False
				fpos = fpos and fpos_obj.browse(cr, uid, fpos, context=context) or False
				this = self.get_current_instance(cr, uid, ids)
				vals = {
						'agreement_id': this.id,
						'automatic_advance': False,
						'line_type': 'real_expense',
						'name': product[0].name,
						'sequence': False,
						'price_unit': result,
						'product_uom_qty': 1,
						'discount': 0.00,
						'notes': 'Driver Payment',
						'control': True,
						'product_id' : product[0].id,
						'product_uom': product[0].uom_id.id,
						'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)])],

						}
				print "El diccionario vals es: ", vals
				self.pool.get('tms.direct.expense').create(cr, uid, vals, context)
			else:
				return True
		return True

	def update_amount_payment_driver (self, cr, uid, ids, context=None):
		this = self.get_current_instance(cr, uid, ids)
		for rec in this:
			for a in rec.agreement_line:
				self.write(cr, uid, ids,{'price_unit':this.amount_driver_factor}) #{'name':seq_number, 'state':'confirmed'}, 'confirmed_by' : uid, 'date_confirmed':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
		return True


##################################SUPLIER PAYMENT FACTOR###############################################################

	def if_exist_product_payment_supplier (self,cr,uid,id):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category','=','real_expense')], limit=1)#,('tms_category', '=', 'fleet')], limit=1)
		print "LA BUSQUEDA DE PROVEEDORES ES IGUAL", prod_id
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for Driver Payment,  name = Supplier Payment or Pago al Proveedores !!!'))
		return prod_id

	def create_product_payment_supplier_line (self, cr, uid, ids, context=None):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category', '=', 'real_expense'),('active','=', 1)], limit=1)
		factor_obj = self.pool.get('tms.indirect.expense')
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for Driver Payment,  (tms_category,=,salary) !!!'))
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
				vals = {
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
						'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)])],
						}
				print "El diccionario vals es: ", vals
				self.pool.get('tms.direct.expense').create(cr, uid, vals, context)
			else:
				return True
		return True
################################ CREACION DE GASTOS CREADOS EN LA RUTA #################################################################

	def if_exist_product_payment_toll_station (self,cr,uid,id):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category','=','highway_tolls',)], limit=1)#,('tms_category', '=', 'fleet')], limit=1)
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for Highway Tolls,  tms_category = highway_tolls !!!'))
		return prod_id

	def create_product_payment_toll_station_line (self, cr, uid, ids, context=None):
		amount_toll_station_route = 0.0
		prod_id = self.if_exist_product_payment_toll_station(cr,uid,ids)
		prod_uom = self.pool.get('product.uom')
		prod_uom_id = self.if_exist_product_uom_id(cr,uid,ids)      

		
		for agreement in self.browse(cr,uid,ids,context=context):
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
				vals = {
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
						}
				self.pool.get('tms.direct.expense').create(cr, uid, vals, context)
			else:
				return True
		return True


	def create_factor_driver_route_line (self, cr, uid, ids, context=None):
		prod_obj = self.pool.get('product.product')
		prod_id = prod_obj.search(cr, uid, [('tms_category', '=', 'salary'),('active','=', 1)], limit=1)
		factor_obj = self.pool.get('tms.indirect.expense')
		if not prod_id:
			raise osv.except_osv(
                        _('Error !'),
                        _('Product not found for Driver Payment,  (tms_category,=,salary) !!!'))
		product = prod_obj.browse(cr, uid, prod_id,	 context=None)
		factor = self.pool.get('tms.factor')
		fpos_obj = self.pool.get('account.fiscal.position')

		for agreement in self.browse(cr,uid,ids,context=context):

			for route in agreement.route_id.expense_driver_factor:
				if route:
					result = self.calculate(cr, uid, 'salary_route', ids, 'client', False)
					fpos = agreement.partner_id.property_account_position.id or False
					fpos = fpos and fpos_obj.browse(cr, uid, fpos, context=context) or False
					this = self.get_current_instance(cr, uid, ids)
					vals = {
							'name': route.name or False,
							'category': route.category or False,
							'factor_type': route.factor_type or False,
							'range_start': route.range_start or False,
							'range_end': route.range_end or False,
							'factor': route.factor or False,
							'fixed_amount': route.fixed_amount or False,
							'mixed': route.mixed or False,
							#'special_formula': a.especial_formula or False, 
							'variable_amount': route.variable_amount or False,
							'agreement_id': agreement.id,
							'expense_id': route.expense_id.id or False,
							'route_id': route.route_id.id or False,
							'travel_id': route.travel_id.id or False,
							'sequence': route.sequence,
							'notes': route.notes or False,
							'control': True,
						}
					self.pool.get('tms.factor').create(cr, uid, vals, context)
				else: 
					print "#################### NOOOOOOOOOOO AYYYYYYYYY FACTOOOOOOOOOOOOOR EEENNNN RRRRROUUUUUUTTTTTTTTAAAAAAA"
		return True
