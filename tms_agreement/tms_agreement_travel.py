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

from datetime import date, datetime, time, timedelta
from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from pytz import timezone


class tms_travel_wizard(osv.osv_memory):
    _name = "tms.travel.wizard"
    _columns = {
        'travel_id': fields.many2one('tms.travel', 'Travel', required=False),        
        'wizard_id': fields.many2one('tms.agreement.travel', 'Wizard Id', required=False, ondelete='cascade'),# select=True, readonly=True),
    }

tms_travel_wizard()
class tms_agreement_travel(osv.osv_memory):
    _name = 'tms.agreement.travel'
    _description = 'Make Travel from Agreement'
    ########## Metodos para crear la factura ##########
    def button_generate_waybill(self,cr,uid,ids,context=None):

        context = context or {}
        active_id = context and context.get('active_id', False)
        waybill_obj = self.pool.get('tms.waybill')
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        waybill_active_id = this.waybill_created_id.id
#        print "000000000WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWAAAAIBIILLL PARA LA SALIDA", waybill_active_id
        self.create_travel_to_waybill_wizard(cr,uid,ids,active_id,context)  #Creamos el viaje para asociarlo con la carta porte
#        self.create_full_vouchers_advances_travel_to_waybill_wizard(cr,uid,ids,active_id,context) # Se asocio esta funcion directamente en create_travel_wizard ya no furula

        self.create_waybill_wizard(cr,uid,ids,active_id,context) # Creamos el la carta porte
        waybill_id = self.search_waybill_id(cr,uid,ids,active_id,context) # ESTE WAYBILL ESTA MAL
        waybill = waybill_obj.browse(cr, uid, waybill_id,context=context)
        self.create_waybill_lines_wizard(cr,uid,ids,active_id,context)
        self.create_shipped_product_to_waybill_wizard(cr,uid,ids,active_id,context)
        self.create_customer_factor_to_waybill_wizard(cr,uid,ids,active_id,context)
        #self.create_driver_factor_to_waybill_wizard(cr,uid,ids,active_id,context)
        self.create_agreement_lines_to_waybill_wizard(cr,uid,ids,active_id,context)
        self.create_extra_fields_to_waybill_wizard(cr,uid,ids,active_id,context)
        self.create_times_to_waybill_wizard(cr,uid,ids,active_id,context) # ESTA FUNCION ASIGNA UN CALCULO DE LOS TIEMPOS PARA WAYBILL
#        self.create_toll_station_to_waybill_wizard(cr,uid,ids,active_id,context) ### ESTA FUNCION AGREBABA CADA UNA DE LAS CASETAS A WAYBILL PERO SE CANCELO
        waybill_created_id = self.get_current_instance(cr,uid,ids).waybill_created_id.id
        travel_obj = self.pool.get('tms.travel')
        ### LAS SIGUIENTES LINEAS INDICAN SI DESPACHAR VIAJE ESTA ACTIVO EL VIAJE DE WAYBILL ES DESPACHADO
        if this.dispatch_travel:
            for w in waybill_obj.browse(cr, uid, [waybill_created_id],context=context):
                for travel in w.travel_ids:
                    if travel.departure == True or travel.departure_2 == True:
                        travel.action_dispatch()
                w.action_approve()

        return {
            'domain': "[('id','in', ["+','.join(map(str,[waybill_created_id]))+"])]",
            'name': _('Waybill Created'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'tms.waybill',
            'view_id': False,
            #'context': "{'agreement_origin': agreement.name , 'agreement': 'True'}",
            'type': 'ir.actions.act_window'
        }


#        return True #self.launch_payment(cr, uid, ids, context=context)

    def create_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_obj = self.pool.get('tms.agreement')
        waybill_obj = self.pool.get('tms.waybill')
        waybill_lines_obj = self.pool.get('tms.waybill.line')
#        lines_created = []
        waybill = waybill_obj.browse(cr, uid, ids, context=context)
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
#        amount = agreement.amount_total
#        print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMMMMMMMMMMMMMMMMMMOOOOOOOOOOOOOOOUUUUNT",amount
#        name_order = agreement.name
#        print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMMMMMMMMMMMMMMMMMMOOOOOOOOOOOOOOOUUUUNT",name_order
        this = self.get_current_instance(cr,uid,ids)
        this_travel_list = []
        this_travel_list.append(this.travel_created_id.id)
        #### ESTAS LINEAS LIGAN EL SEGUNDO VIAJE VACIO A LA CARTA PORTE ####

        #if this.travel_return_id:
        #    this_travel_list.append(this.travel_return_id.id)

#        print "IDDDDDDDDD DE TRAVEL MEDIANTE SELF BROWSE ESSSSSSSSSS", travel_active_id
        # list_travels=[]
        # for travels in this.travel_ids:
        #     list_travels.append(travels.travel_id.id)

        factor_list = []
        for factor in agreement.agreement_driver_factor:
            xline_factor = (0,0,{
                                        'name'          : 'Salary Operator',
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
                                        'notes'         : "Factor creado desde el Acuerdo"+agreement.name,
                                        'control'       : False,### Revisar si es necesario eliminarlo
                                        'driver_helper' : False,

                            })
            factor_list.append(xline_factor)
        for rec in self.browse(cr,uid,ids,context=context):
            # if rec.asign_travel:
            #     print "SIIIIIIIIIIIIIII HAYYYYYYYYYYYYYYYYYYYYYY             IDDDDDDDDDS EN one2many"
            #     vals = {
            #         #'name': False,
            #         'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            #         'shop_id': rec.shop_id.id,
            #         'sequence_id': rec.sequence_waybill_id.id,
            #         'partner_id' :agreement.partner_id.id,
            #         'currency_id' : agreement.currency_id.id,
            #         'partner_order_id' : agreement.partner_order_id.id,
            #         'partner_invoice_id' : agreement.partner_invoice_id.id,
            #         'departure_address_id' : agreement.departure_address_id.id,
            #         'arrival_address_id' : agreement.arrival_address_id.id,
            #         'upload_point' : agreement.upload_point,
            #         'download_point' : agreement.download_point,
            #         'agreement': True,
            #         'agreement_origin':agreement.name,
            #         'agreement_id': agreement.id,
            #         'travel_ids': [(6, 0, list_travels )],
            #         'expense_driver_factor': [x for x in factor_list]
            #         #'waybill_shipped_product': agreement.agreement_line[0]
            #         }
            #     print "El diccionario vals es: ", vals
            #     waybill_id = waybill_obj.create(cr, uid, vals, context)
            #     self.write(cr, uid, ids,{'waybill_created_id':waybill_id})
            #     #print "EL WAYBILL CHERMAN IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID CON EL QUE FUE CREADO EL WAYBILL ES ", waybill_created_id
            #     print "EL WAYBILL CHERMAN IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID CON EL QUE FUE CREADO EL WAYBILL ES ", waybill_id
            # else:
            vals = {
                #'name': False,
                'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'shop_id': rec.shop_id.id,
                'sequence_id': rec.sequence_waybill_id.id,
                'partner_id' :agreement.partner_id.id,
                'currency_id' : agreement.currency_id.id,
                'partner_order_id' : agreement.partner_order_id.id,
                'partner_invoice_id' : agreement.partner_invoice_id.id,
                'departure_address_id' : agreement.departure_address_id.id,
                'arrival_address_id' : agreement.arrival_address_id.id,
                'upload_point' : agreement.upload_point,
                'download_point' : agreement.download_point,
                'agreement': True,
                'agreement_origin':agreement.name,
                'travel_ids': [(6, 0, this_travel_list)],
                'agreement_id': agreement.id,
                'expense_driver_factor': [x for x in factor_list],
                #'waybill_shipped_product': agreement.agreement_line[0]
                }
            waybill_id = waybill_obj.create(cr, uid, vals, context)
            agreement.write({'waybill_ref_id': waybill_id})
            self.write(cr, uid, ids,{'waybill_created_id':waybill_id})
            #print "EL WAYBILL CHERMAN IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID CON EL QUE FUE CREADO EL WAYBILL ES ", waybill_created_id

            ######### AQUI INGRESAREMOS LOS FACTORES EN EL VIAJE
            # travel_obj = self.pool.get('tms.travel')
            # for travel in travel_obj.browse(cr, uid, [this.travel_created_id.id], context=None):
            #     travel.write({'expense_driver_factor': [x for x in factor_list]})
                     
            # Un create siempre me regresa el ID con el que se creo
#        for lines in agreement.agreement_line:
#            print "DENTRO DE LAS LINEAS", lines.name
#            lines_created.append(lines.id)
#        print "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLIIIISSSTA", lines_created
        return True

    def create_waybill_lines_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        waybill_obj = self.pool.get('tms.waybill')
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        waybill_id = self.search_waybill_id(cr,uid,ids,active_id,context)
        waybill = waybill_obj.browse(cr, uid, waybill_id,context=context)
        # for w in waybill.waybill_line:
        #     print w
        return True


############################################ CREANDO EL PRODUCTO EMBARCADO DESDE CARTA PORTE ########################

    def create_shipped_product_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        shipped_product = waybill.waybill_shipped_product

        for a in agreement.agreement_shipped_product:
            vals = {
                    'name': a.product_id.name,
                    'waybill_id': waybill.id,
                    'product_id': a.product_id.id,
                    'product_uom': a.product_uom.id,
                    'product_uom_qty': a.product_uom_qty,
                    'notes': a.notes,
                    'sequence': a.sequence,
                    'agreement_control': True,
                    }
            self.pool.get('tms.waybill.shipped_product').create(cr, uid, vals, context)

        return True

######################### FUNCION PARA GENERAR EL FACTOR CUSTOMER PARA EL FLEET ########################################

    def create_customer_factor_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        waybill_line= waybill.waybill_line
        prod_obj = self.pool.get('product.product')
        fleet_id = prod_obj.search(cr, uid, [('tms_category', '=', 'freight'),('active','=', 1),('tms_default_freight','=',True)], limit=1)
        #fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)

        factor_list = []
        for a in agreement.agreement_customer_factor:
            vals = (0,0,{
                    'name': a.name or False,
                    'category': a.category or False,
                    'factor_type': a.factor_type or False,
                    'range_start': a.range_start or False,
                    'range_end': a.range_end or False,
                    'factor': a.factor or False,
                    'fixed_amount': a.fixed_amount or False,
                    'mixed': a.mixed or False,
                    #'special_formula': a.especial_formula or False, 
                    'variable_amount': a.variable_amount or False,
                    #'waybill_id': waybill.id or False,
                    'expense_id': a.expense_id.id or False,
                    'route_id': a.route_id.id or False,
                    'travel_id': a.travel_id.id or False,
                    'sequence': a.sequence,
                    'notes': a.notes or False,
                    })
            factor_list.append(vals)

        for waybill in waybill_obj.browse(cr, uid, [waybill_active_id], context=context):
            waybill.write({'waybill_customer_factor': [x for x in factor_list]})


            #self.pool.get('tms.factor').create(cr, uid, vals, context)

###############3 ESTOS CAMPOS COMENTADOS OBTENIAN Y CREABAN LOS FACTORES DESDE LA RUTA PERO AHORA SE TOMAN DESDE EL ACUERDO!!!!!1
#        for route in agreement.route_id.expense_driver_factor:
#            print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ DRIVER ROUTE", route.name
#            print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ DRIVER ROUTE", route.id
#            vals = {
#                    'name': route.name or False,
#                    'category': route.category or False,
#                    'factor_type': route.factor_type or False,
#                    'range_start': route.range_start or False,
#                    'range_end': route.range_end or False,
#                    'factor': route.factor or False,
#                    'fixed_amount': route.fixed_amount or False,
#                    'mixed': route.mixed or False,
#                    #'special_formula': a.especial_formula or False, 
#                    'variable_amount': route.variable_amount or False,
#                    'waybill_id': waybill.id or False,
#                    'expense_id': route.expense_id.id or False,
#                    'route_id': route.route_id.id or False,
#                    'travel_id': route.travel_id.id or False,
#                    'sequence': route.sequence,
#                    'notes': route.notes or False,
#                    }
#            self.pool.get('tms.factor').create(cr, uid, vals, context)
        return True

######################### FUNCION PARA GENERAR EL FACTOR DRIVERS DESDE ROUTE Y AGREEMENT PARA EL FLEET ########################################

    def create_driver_factor_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        waybill_line= waybill.waybill_line
        prod_obj = self.pool.get('product.product')
        fleet_id = prod_obj.search(cr, uid, [('tms_category', '=', 'freight'),('active','=', 1),('tms_default_freight','=',True)], limit=1)
        #fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)

        for a in agreement.agreement_driver_factor:
            vals = {
                    'name': a.name or False,
                    'category': a.category or False,
                    'factor_type': a.factor_type or False,
                    'range_start': a.range_start or False,
                    'range_end': a.range_end or False,
                    'factor': a.factor or False,
                    'fixed_amount': a.fixed_amount or False,
                    'mixed': a.mixed or False,
                    #'special_formula': a.especial_formula or False, 
                    'variable_amount': a.variable_amount or False,
                    'waybill_id': waybill.id or False,
                    'expense_id': a.expense_id.id or False,
                    'route_id': a.route_id.id or False,
                    'travel_id': a.travel_id.id or False,
                    'sequence': a.sequence,
                    'notes': a.notes or False,
                    }
            #self.pool.get('tms.factor').create(cr, uid, vals, context)

        return True

############################### CREANDO LAS LINEAS DE LA CARTA PORTE A PARTIR DE LAS LINEAS DE AGREEMENT #######################3

    def create_agreement_lines_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        waybill_line= waybill.waybill_line
        prod_obj = self.pool.get('product.product')
        fleet_id = prod_obj.search(cr, uid, [('tms_category', '=', 'freight'),('active','=', 1),('tms_default_freight','=',True)], limit=1)
        #fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)

        for a in agreement.agreement_line:
            if a.control == False:
                vals = {
                        'waybill_id': waybill.id,
                        'line_type': a.line_type,
                        'product_id': a.product_id.id,
                        'product_uom': a.product_uom.id,
                        'product_uom_qty': a.product_uom_qty,
                        'price_unit': a.price_unit,
                        'price_discount': a.price_discount,
                        'name': a.name,
                        'sequence': a.sequence,
                        'agreement_control': True,
                        }
                self.pool.get('tms.waybill.line').create(cr, uid, vals, context)

        return True

######################### FUNCION PARA GENERAR LOS EXTRA FIELDS ########################################

    def create_extra_fields_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        waybill_line= waybill.waybill_line
        prod_obj = self.pool.get('product.product')
        fleet_id = prod_obj.search(cr, uid, [('tms_category', '=', 'freight'),('active','=', 1),('tms_default_freight','=',True)], limit=1)
        #fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)

        for a in agreement.agreement_extradata:
            vals = {
                    'name': a.name or False,
                    'notes': a.notes or False,
                    'sequence': a.sequence or False,
                    'mandatory': a.mandatory or False,
                    'type_extra': a.type_extra or False,
                    'value_char': a.value_char or False,
                    'value_text': a.value_text or False,
                    'value_integer': a.value_integer or False,
                    'value_float': a.value_float or False,
                    'value_date': a.value_date or False,
                    'value_datetime': a.value_datetime or False,
                    'value_extra': a.value_extra or False,
                    'waybill_id': waybill.id,
                    }
            self.pool.get('tms.waybill.extradata').create(cr, uid, vals, context)

        return True
######################### FUNCION PARA GENERAR EL VIAJE DESDE AGREEMENT ########################################

    def create_travel_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
#        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS", this.waybill_created_id.id
#        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
#        waybill_obj = self.pool.get('tms.waybill')
#        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
#        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS LLAMANDO LA CLASEEEE", waybill.id
        travel_obj = self.pool.get('tms.travel')
        context.update({'uid' : uid })
        real_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for rec in self.browse(cr,uid,ids,context=context):
            # if rec.asign_travel:
            #     print "TRRRRRRRRRRUUUUUUUUUUUEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE BOTON GENERAR TRAVELS"#, rec.travel_ids
            #     return True
            # else:
            factor_list = []
            for factor in agreement.agreement_driver_factor:
                xline_factor = (0,0,{
                                            'name'          : 'Salary Operator',
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
                                            'notes'         : "Factor creado desde el Acuerdo"+agreement.name,
                                            'control'       : False,### Revisar si es necesario eliminarlo
                                            'driver_helper' : False,

                                })
                factor_list.append(xline_factor)

            if agreement.route_id.id:
                vals = {
                            'shop_id': this.shop_id.id,
                            'company_id': rec.shop_id.company_id.id,
                            #'name': False,
                            'state': 'draft',
                            'route_id': agreement.route_id.id,
                            'kit_id':  rec.kit_id.id,
                            'unit_id': rec.unit_id.id,
                            'trailer1_id': rec.trailer1_id.id,
                            'dolly_id': rec.dolly_id.id,
                            'trailer2_id': rec.trailer2_id.id,
                            'employee_id': rec.employee_id.id,
                            'employee2_id': rec.employee2_id.id,
                            'date': real_date,
                            'distance_extraction': agreement.route_id.distance,
                            #'departure': agreement.departure.id,                
                            #'arrival': agreement.arrival,
                            'notes': agreement.notes or False,
                            'create_uid': uid,
                            'create_date': real_date,
                            'departure': agreement.departure,
                            'departure_2': agreement.departure_2,
                            'arrival': agreement.arrival,
                            'arrival_2': agreement.arrival_2,
                            'expense_driver_factor': [x for x in factor_list],
                        }
                
                travel_id = travel_obj.create(cr, uid, vals, context)
                self.write(cr, uid, ids,{'travel_created_id':travel_id})

            ########### CREAMOS LA RUTA DE VACIO SE NECESITAN VALIDACIONES
            if agreement.route_return_id.id:
                vals_2 = {
                        'shop_id': this.shop_id.id,
                        'company_id': rec.shop_id.company_id.id,
                        #'name': False,
                        'state': 'draft',
                        'route_id': agreement.route_return_id.id,
                        'distance_extraction': agreement.route_return_id.distance,
                        'kit_id':  rec.kit_id.id,
                        'unit_id': rec.unit_id.id,
                        'trailer1_id': rec.trailer1_id.id,
                        'dolly_id': rec.dolly_id.id,
                        'trailer2_id': rec.trailer2_id.id,
                        'employee_id': rec.employee_id.id,
                        'employee2_id': rec.employee2_id.id,
                        'date': real_date,
                        #'departure': agreement.departure.id,                
                        #'arrival': agreement.arrival,
                        'notes': agreement.notes or False,
                        'create_uid': uid,
                        'create_date': real_date,
                        'departure': agreement.departure,
                        'departure_2': agreement.departure_2,
                        'arrival': agreement.arrival,
                        'arrival_2': agreement.arrival_2,
                        'expense_driver_factor': [x for x in factor_list],
                    }
                travel_return_id = travel_obj.create(cr, uid, vals_2, context)
                self.write(cr, uid, ids,{'travel_return_id':travel_return_id})

            travel_obj = self.pool.get('tms.travel')
            travel = travel_obj.browse(cr, uid, travel_id, context=context)
            fuel_suppliers=[]
            for fuel_sup in travel.shop_id.tms_fuel_sequence_ids:
                fuel_suppliers.append(fuel_sup.partner_id.id)

            if rec.employee_id.tms_supplier_driver == False: ##### SOLO CREAMOS VALES Y ANTICIPOS PARA OPERADORES QUE NO SEAN PERMISIONARIOS
                for fuel in agreement.agreement_direct_expense_line:
                    if fuel.line_type == 'fuel' and fuel.credit == True:
                        vals = {

                                'state':'draft',
                                'travel_id': travel_id,
                                'partner_id': fuel.fuel_supplier_id.id,
                                'employee_id': rec.employee_id.id,
                                'product_id': fuel.product_id.id,
                                'product_uom_qty': fuel.product_uom_qty,
                                'product_uom': fuel.product_uom.id,
                                'tax_amount': fuel.tax_amount,
                                'price_total': fuel.price_total,
                                'notes': fuel.name,
                                'create_uid' : uid,
                                'create_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),       
                                'currency_id': agreement.currency_id.id,
                                }
                        self.pool.get('tms.fuelvoucher').create(cr, uid, vals, context)
                        
                    elif fuel.automatic == True:
                        vals = {

                                'state':'draft',
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                                'travel_id': travel.id,
                                'unit_id': False,
                                'employee_id': rec.employee_id.id,
                                'product_id': fuel.product_id.id,
                                'product_uom_qty': fuel.product_uom_qty,
                                'product_uom': fuel.product_uom.id,
                                'price_unit' : fuel.price_unit ,
                                'total': fuel.price_total,
                                'notes': fuel.name,
                                'create_uid' : uid,
                                'create_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),       
                                'currency_id': agreement.currency_id.id,
                                'auto_expense'  : True,

                                }
                        self.pool.get('tms.advance').create(cr, uid, vals, context)
        return True

######################### FUNCION PARA GENERAR LAS CASETAS DESDE LA RUTA DEL AGREEMENT########################################

    def create_toll_station_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        waybill_line= waybill.waybill_line
        toll_id = agreement_obj.if_exist_product_payment_toll_station(cr,uid,active_id)
        uom_id = agreement_obj.if_exist_product_uom_id(cr,uid,active_id)
        unit_category_id = agreement.unit_ids


        for toll in agreement.route_id.tms_route_tollstation_ids:
            if toll.credit:
                for axis in toll.tms_route_tollstation_costperaxis_ids:
                    if axis.unit_type_id == unit_category_id:
                        vals = {
                                'waybill_id': waybill.id,
                                'line_type': 'product',
                                'product_id': toll_id[0],
                                'product_uom': uom_id[0],
                                'product_uom_qty': 1,
                                'price_unit': axis.cost_credit,
                                'price_discount': 16,
                                'name': toll.name,
                                'sequence': False,
                                'agreement_control': True,
                                }
                        self.pool.get('tms.waybill.line').create(cr, uid, vals, context)
            else:
                for axis in toll.tms_route_tollstation_costperaxis_ids:
                    if axis.unit_type_id == unit_category_id:
                        vals = {
                                'waybill_id': waybill.id,
                                'line_type': 'product',
                                'product_id': toll_id[0],
                                'product_uom': uom_id[0],
                                'product_uom_qty': 1,
                                'price_unit': axis.cost_cash,
                                'price_discount': 16,
                                'name': toll.name,
                                'sequence': False,
                                'agreement_control': True,
                                }
                        self.pool.get('tms.waybill.line').create(cr, uid, vals, context)
            
        return True

################################################################################################################################

############################################# CREACION DE EXPENSES DESDE AGREEMENT LINE PARA TRAVEL #########################################################

    def create_full_vouchers_advances_travel_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        travel_active_id = this.travel_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        travel_obj = self.pool.get('tms.travel')
        travel = travel_obj.browse(cr, uid, travel_active_id, context=context)

#        waybill_line= waybill.waybill_line
#        fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)
#        print "EL RESULTADO DE LA BUSQUEDA DE PRODUCTOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO ES IGUALLLLLLLLLLL 11111111111", fleet_id[0]
        fuel_suppliers=[]
        
        for fuel_sup in travel.shop_id.tms_fuel_sequence_ids:
            fuel_suppliers.append(fuel_sup.partner_id.id)

        for rec in self.browse(cr,uid,ids,context=context):
            # if not rec.asign_travel:
            for fuel in agreement.agreement_direct_expense_line:
                if fuel.line_type == 'fuel' and fuel.credit == True:
                    vals = {

                            'state':'draft',
                            'travel_id': travel.id,
                            'partner_id': fuel.fuel_supplier_id.id,
                            'product_id': fuel.product_id.id,
                            'product_uom_qty': fuel.product_uom_qty,
                            'product_uom': fuel.product_uom.id,
                            'tax_amount': fuel.tax_amount,
                            'price_total': fuel.price_total,
                            'notes': fuel.name,
                            'create_uid' : uid,
                            'create_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),       
                            'currency_id': agreement.currency_id.id,
                            }
                    self.pool.get('tms.fuelvoucher').create(cr, uid, vals, context)

                elif fuel.automatic == True:
                    vals = {

                            'state':'draft',
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                            'travel_id': travel.id,
                            'unit_id': False,
                            'employee_id': rec.employee_id.id,
                            'product_id': fuel.product_id.id,
                            'product_uom_qty': fuel.product_uom_qty,
                            'product_uom': fuel.product_uom.id,
                            'price_unit' : fuel.price_unit ,
                            'total': fuel.price_total,
                            'notes': fuel.name,
                            'create_uid' : uid,
                            'create_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),       
                            'currency_id': agreement.currency_id.id,
                            'auto_expense'  : True,

                            }
                    self.pool.get('tms.advance').create(cr, uid, vals, context)



#        for a in agreement.agreement_line:
#            if a.control == False:
#                vals = {
#                        'waybill_id': waybill.id,
#                        'line_type': a.line_type,
#                        'product_id': a.product_id.id,
#                        'product_uom': a.product_uom.id,
#                        'product_uom_qty': a.product_uom_qty,
#                        'price_unit': a.price_unit,
#                        'price_discount': a.price_discount,
#                        'name': a.name,
#                        'sequence': a.sequence,
#                        'agreement_control': True,
#                        }
#                self.pool.get('tms.waybill.line').create(cr, uid, vals, context)

        return True

################################################################################################################################

######################### FUNCION PARA GENERAR LOS TIEMPOS PARA INTRODUCIRLOS EN WAYBILL########################################

    def create_times_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        waybill_active_id = this.waybill_created_id.id
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)

        date_start = datetime.strptime(this.date_start, '%Y-%m-%d %H:%M:%S')
        time01 = agreement.hours_start_upload
        time02 = agreement.hours_upload_end_upload
        time03 = agreement.hours_end_upload_lib_docs
        time04 = agreement.hours_lib_docs_prog_download
        time05 = agreement.hours_prog_download_start_download
        time06 = agreement.hours_start_download_end_download
        time07 = agreement.hours_end_download_lib_docs_download
        time08 = agreement.hours_lib_docs_download_end_travel
        time_total_hours = agreement.hours_total_travel

        new_time01 = date_start + timedelta(hours=time01)
        new_time02 = new_time01 + timedelta(hours=time02)
        new_time03 = new_time02 + timedelta(hours=time03)
        new_time04 = new_time03 + timedelta(hours=time04)
        new_time05 = new_time04 + timedelta(hours=time05)
        new_time06 = new_time05 + timedelta(hours=time06)
        new_time07 = new_time06 + timedelta(hours=time07)
        new_time08 = new_time07 + timedelta(hours=time08)

        waybill.write({
                        'date_start': this.date_start,
                        'date_up_start_sched': new_time01, 
                        'date_up_end_sched': new_time02,
                        'date_up_docs_sched': new_time03,
                        'date_appoint_down_sched': new_time04,
                        'date_down_start_sched': new_time05,
                        'date_down_end_sched': new_time06,
                        'date_down_docs_sched': new_time07,
                        'date_end':  new_time08,
                        })

        return True

################################################################################################################################


    def search_waybill_id (self, cr, uid, ids, active_id, context=None):
        context = context or {}
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, ids, context=context)
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)

        waybill_agreement = waybill_obj.search(cr, uid, [('agreement_origin','=',agreement.name)], limit=1)
        # if waybill_agreement:
        #     print "TTTTTTTTTTTTTTTTTRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRUUUUUUUUUUUUUUEEEEEEEEEEEEE", waybill_agreement[0]
        return waybill_agreement[0]


    def get_current_instance(self, cr, uid, ids):
        lines = self.browse(cr,uid,ids)
        obj = None
        for i in lines:
            obj = i
        return obj

    _columns = {
        'sequence_waybill_id': fields.many2one('ir.sequence', 'Waybill sequence', required=True),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=False),
        'waybill_created_id': fields.many2one('tms.waybill', 'ID Waybill Created', required=False, readonly=True), # Registro temporal del ID que crea de la carta porte
        #'unit_type_id': fields.many2one('tms.unit.category', 'Unit category', required=True),
        'travel_created_id': fields.many2one('tms.travel', 'ID Travel Created', required=False, readonly=True), # Registro temporal del ID que crea del viaje
        'travel_return_id': fields.many2one('tms.travel', 'ID Travel Created Uncharged', required=False, readonly=True), # Registro temporal del ID que crea del viaje
        'kit_id': fields.many2one('tms.unit.kit', 'Kit', required=False),
        'unit_id': fields.many2one('fleet.vehicle', 'Unit', required=False, domain=[('fleet_type', '=', 'tractor')], ),
        'trailer1_id': fields.many2one('fleet.vehicle', 'Trailer1', required=False,  domain=[('fleet_type', '=', 'trailer')]),
        'dolly_id': fields.many2one('fleet.vehicle', 'Dolly', required=False,        domain=[('fleet_type', '=', 'dolly')]),
        'trailer2_id': fields.many2one('fleet.vehicle', 'Trailer2', required=False,  domain=[('fleet_type', '=', 'trailer')]),
        'employee_id': fields.many2one('hr.employee', 'Driver', required=False, domain=[('tms_category', '=', 'driver')]),
        'employee2_id': fields.many2one('hr.employee', 'Driver 2', required=False, domain=[('tms_category', '=', 'driver')]),
        #'asign_travel': fields.boolean('Asigned Travel Exist?'),
        #'travel_ids': fields.one2many('tms.travel.wizard', 'wizard_id', 'Travel', required=False, readonly=False), # Asignar un viaje existente
        'dispatch_travel': fields.boolean('Dispatch Travel'),
        'date_start': fields.datetime('Date Start', required=True, help="Esta Fecha/Hora es la Base para Poder Calcular las fechas de la carta Porte, hace referencia a la Fecha/Hora Base de Salida o Inicio del Viaje"),
#        'date_end': fields.datetime('Date End', required=True),
    }

    def _get_active_shop(self,cr,uid,context=None): # esta funcion en el wizard le va agregar por defecto la session en la que estamos
        res_obj = self.pool.get('res.users')
        res = res_obj.browse(cr, uid, uid, context=context)
        shop_obj = self.pool.get('sale.shop')
        shop = shop_obj.search(cr, uid, [('company_id','=',res.company_id.id)], limit=1)
        # shop_id = shop[0]
        # print "#######################################################  SHOP [0]", shop_id
        if not shop:
            return None
        # return shop_id
        return shop[0]

    _defaults = {
        'date_start': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'shop_id': _get_active_shop,

    }

    def onchange_kit_id(self, cr, uid, ids, kit_id):
        if not kit_id:
            return {}        
        kit = self.pool.get('tms.unit.kit').browse(cr, uid, kit_id)
        return {'value' : {'unit_id': kit.unit_id.id, 'trailer1_id': kit.trailer1_id.id, 'dolly_id': kit.dolly_id.id, 'trailer2_id': kit.trailer2_id.id, 'employee_id': kit.employee_id.id}}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
