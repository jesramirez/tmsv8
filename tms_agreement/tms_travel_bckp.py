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

from osv import osv, fields
import time
from datetime import datetime, date
from osv.orm import browse_record, browse_null
from osv.orm import except_orm
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc
import openerp

class tms_travel_wizard(osv.osv_memory):
    _name = "tms.travel.wizard"
    _columns = {
        'travel_id': openerp.osv.fields.many2one('tms.travel', 'Travel', required=True),        
        'wizard_id': openerp.osv.fields.many2one('tms.agreement.travel', 'Wizard Id', required=False, ondelete='cascade'),# select=True, readonly=True),
    }

tms_travel_wizard()
class tms_agreement_travel(osv.osv_memory):
    _name = 'tms.agreement.travel'
    _description = 'Make Travel from Agreement'
    ########## Metodos para crear la factura ##########
    def button_generate_waybill(self,cr,uid,ids,context=None):
        """Check the order:
        if the order is not paid: continue payment,
        if the order is paid print ticket.
        """
        context = context or {}
        active_id = context and context.get('active_id', False)
        waybill_obj = self.pool.get('tms.waybill')
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        waybill_active_id = this.waybill_created_id.id

        self.create_travel_to_waybill_wizard(cr,uid,ids,active_id,context)  #Creamos el viaje para asociarlo con la carta porte
#        self.create_full_vouchers_advances_travel_to_waybill_wizard(cr,uid,ids,active_id,context)

        self.create_waybill_wizard(cr,uid,ids,active_id,context) # Creamos el la carta porte
        waybill_id = self.search_waybill_id(cr,uid,ids,active_id,context)
        print "IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID", waybill_id
        waybill = waybill_obj.browse(cr, uid, waybill_id,context=context)
        self.create_waybill_lines_wizard(cr,uid,ids,active_id,context)
        self.create_shipped_product_to_waybill_wizard(cr,uid,ids,active_id,context)
        self.create_customer_factor_to_waybill_wizard(cr,uid,ids,active_id,context)
        self.create_driver_factor_to_waybill_wizard(cr,uid,ids,active_id,context)
        self.create_agreement_lines_to_waybill_wizard(cr,uid,ids,active_id,context)
        self.create_extra_fields_to_waybill_wizard(cr,uid,ids,active_id,context)
        self.create_toll_station_to_waybill_wizard(cr,uid,ids,active_id,context)
        return True #self.launch_payment(cr, uid, ids, context=context)

    def create_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        print "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",active_id

        context = context or {}
        agreement_obj = self.pool.get('tms.agreement')
        waybill_obj = self.pool.get('tms.waybill')
        print "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWw", waybill_obj
        waybill_lines_obj = self.pool.get('tms.waybill.line')
#        lines_created = []
        waybill = waybill_obj.browse(cr, uid, ids, context=context)
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMMMMMMMMMMMMMMMMMMOOOOOOOOOOOOOOOUUUUNT",active_id
#        amount = agreement.amount_total
#        print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMMMMMMMMMMMMMMMMMMOOOOOOOOOOOOOOOUUUUNT",amount
#        name_order = agreement.name
#        print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMMMMMMMMMMMMMMMMMMOOOOOOOOOOOOOOOUUUUNT",name_order
        this = self.get_current_instance(cr,uid,ids)
        travel_active_id = this.travel_created_id.id
        print "IDDDDDDDDD DE TRAVEL MEDIANTE SELF BROWSE ESSSSSSSSSS", travel_active_id
        list_travels=[]
        for travels in this.travel_ids:
            list_travels.append(travels.travel_id.id)

        print "LISSSSSSSSSSSSSSSSSSSSSSSSSSSSSTTTTTTTTAAAAAAAAAA TRRRRRAAAAAAAAAAVVVVVVVVEEEEEEEELLLLLLLLLLSSSSS", list_travels

        for rec in self.browse(cr,uid,ids,context=context):
            if rec.asign_travel:
                print "SIIIIIIIIIIIIIII HAYYYYYYYYYYYYYYYYYYYYYY             IDDDDDDDDDS EN one2many"
                vals = {
                    #'name': False,
                    'date_order': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'shop_id': rec.shop_id.id,
                    'sequence_id': rec.sequence_waybill_id.id,
                    'partner_id' :agreement.partner_id.id,
                    'currency_id' : agreement.currency_id.id,
                    'partner_order_id' : agreement.partner_order_id.id,
                    'partner_invoice_id' : agreement.partner_invoice_id.id,
                    'departure_address_id' : agreement.departure_address_id.id,
                    'arrival_address_id' : agreement.arrival_address_id.id,
                    'upload_point' : agreement.upload_point.name,
                    'download_point' : agreement.download_point.name,
                    'agreement': True,
                    'agreement_origin':agreement.name,
                    'travel_ids': [(6, 0, list_travels )],
                    #'waybill_shipped_product': agreement.agreement_line[0]
                    }
                print "El diccionario vals es: ", vals
                waybill_id = waybill_obj.create(cr, uid, vals, context)
                self.write(cr, uid, ids,{'waybill_created_id':waybill_id})
                #print "EL WAYBILL CHERMAN IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID CON EL QUE FUE CREADO EL WAYBILL ES ", waybill_created_id
                print "EL WAYBILL CHERMAN IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID CON EL QUE FUE CREADO EL WAYBILL ES ", waybill_id
            else:
                vals = {
                    #'name': False,
                    'date_order': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'shop_id': rec.shop_id.id,
                    'sequence_id': rec.sequence_waybill_id.id,
                    'partner_id' :agreement.partner_id.id,
                    'currency_id' : agreement.currency_id.id,
                    'partner_order_id' : agreement.partner_order_id.id,
                    'partner_invoice_id' : agreement.partner_invoice_id.id,
                    'departure_address_id' : agreement.departure_address_id.id,
                    'arrival_address_id' : agreement.arrival_address_id.id,
                    'upload_point' : agreement.upload_point.name,
                    'download_point' : agreement.download_point.name,
                    'agreement': True,
                    'agreement_origin':agreement.name,
                    'travel_ids': [(6, 0, [travel_active_id] )],
                    #'waybill_shipped_product': agreement.agreement_line[0]
                    }
                print "El diccionario vals es: ", vals
                waybill_id = waybill_obj.create(cr, uid, vals, context)
                self.write(cr, uid, ids,{'waybill_created_id':waybill_id})
                #print "EL WAYBILL CHERMAN IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID CON EL QUE FUE CREADO EL WAYBILL ES ", waybill_created_id
                print "EL WAYBILL CHERMAN IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID CON EL QUE FUE CREADO EL WAYBILL ES ", waybill_id

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
        print "IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID WAAAAAAAAYYYYYYYBILLLLLL", waybill_id
        waybill = waybill_obj.browse(cr, uid, waybill_id,context=context)
        for w in waybill.waybill_line:
            print w
        return True


############################################ CREANDO EL PRODUCTO EMBARCADO DESDE CARTA PORTE ########################

    def create_shipped_product_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS", this.waybill_created_id.id
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS LLAMANDO LA CLASEEEE", waybill.id
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
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS", this.waybill_created_id.id
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS LLAMANDO LA CLASEEEE", waybill.id
        waybill_line= waybill.waybill_line
        fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)
        print "EL RESULTADO DE LA BUSQUEDA DE PRODUCTOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO ES IGUALLLLLLLLLLL 11111111111", fleet_id[0]

        for a in agreement.agreement_customer_factor:
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
            self.pool.get('tms.factor').create(cr, uid, vals, context)
        for route in agreement.route_id.expense_driver_factor:
            print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ DRIVER ROUTE", route.name
            print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ DRIVER ROUTE", route.id
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
                    'waybill_id': waybill.id or False,
                    'expense_id': route.expense_id.id or False,
                    'route_id': route.route_id.id or False,
                    'travel_id': route.travel_id.id or False,
                    'sequence': route.sequence,
                    'notes': route.notes or False,
                    }
            self.pool.get('tms.factor').create(cr, uid, vals, context)
        return True

######################### FUNCION PARA GENERAR EL FACTOR DRIVERS DESDE ROUTE Y AGREEMENT PARA EL FLEET ########################################

    def create_driver_factor_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS", this.waybill_created_id.id
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS LLAMANDO LA CLASEEEE", waybill.id
        waybill_line= waybill.waybill_line
        fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)
        print "EL RESULTADO DE LA BUSQUEDA DE PRODUCTOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO ES IGUALLLLLLLLLLL 11111111111", fleet_id[0]

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
            self.pool.get('tms.factor').create(cr, uid, vals, context)

        return True

############################### CREANDO LAS LINEAS DE LA CARTA PORTE A PARTIR DE LAS LINEAS DE AGREEMENT #######################3

    def create_agreement_lines_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS", this.waybill_created_id.id
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS LLAMANDO LA CLASEEEE", waybill.id
        waybill_line= waybill.waybill_line
        fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)
        print "EL RESULTADO DE LA BUSQUEDA DE PRODUCTOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO ES IGUALLLLLLLLLLL 11111111111", fleet_id[0]

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
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS", this.waybill_created_id.id
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS LLAMANDO LA CLASEEEE", waybill.id
        waybill_line= waybill.waybill_line
        fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)
        print "EL RESULTADO DE LA BUSQUEDA DE PRODUCTOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO ES IGUALLLLLLLLLLL 11111111111", fleet_id[0]

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
        print "COOOOOOOOONNNNNNNNNNNNNNNTTTTTTTTTTEEEEEEEEEEEXXXXXXXXXXXTTTTTTTTTTT", context
        real_date = time.strftime( DEFAULT_SERVER_DATETIME_FORMAT)
        print "DATEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE MAAAAAAAACCCCCHHHHHIIIIIIINNNNNNNNEEEEEEE",  real_date
        for rec in self.browse(cr,uid,ids,context=context):
            if rec.asign_travel:
                print "TRRRRRRRRRRUUUUUUUUUUUEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE BOTON GENERAR TRAVELS"#, rec.travel_ids
            else:
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
                        #'departure': agreement.departure.id,                
                        #'arrival': agreement.arrival,
                        'notes': agreement.notes or False,
                        'create_uid': uid,
                        'create_date': real_date,
                    }
                print "El diccionario vals es: ", vals
                travel_id = travel_obj.create(cr, uid, vals, context)
                print "IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID DE TRAVEL", travel_id           
                self.write(cr, uid, ids,{'travel_created_id':travel_id})
            #print "EL WAYBILL CHERMAN IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID CON EL QUE FUE CREADO EL WAYBILL ES ", waybill_created_id
                print "EL TRAVEL CHERMAN IDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDIDID CON EL QUE FUE CREADO EL WAYBILL ES ", travel_id

        return True

######################### FUNCION PARA GENERAR LAS CASETAS DESDE LA RUTA DEL AGREEMENT########################################

    def create_toll_station_to_waybill_wizard (self,cr,uid,ids,active_id,context=None):
        context = context or {}
        agreement_lines = []
        vals ={}
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)
        this = self.get_current_instance(cr,uid,ids)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS", this.waybill_created_id.id
        waybill_active_id = this.waybill_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, waybill_active_id, context=context)
        print "EL ID DE WAYBILLLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS LLAMANDO LA CLASEEEE", waybill.id
        waybill_line= waybill.waybill_line
        toll_id = agreement_obj.if_exist_product_payment_toll_station(cr,uid,active_id)
        uom_id = agreement_obj.if_exist_product_uom_id(cr,uid,active_id)
        print "EL RESULTADO DE LA BUSQUEDA DE PRODUCTOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO ES IGUALLLLLLLLLLL 11111111111", toll_id[0]
        print "EL RESULTADO DE LA BUSQUEDA DE PRODUCTOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO ES IGUALLLLLLLLLLL 11111111111", uom_id[0]
        unit_category_id = this.unit_type_id


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
            print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ DRIVER TOLLLLLLLL", toll.name
            print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ DRIVER TOLLLLLLLL", toll.id

            
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
        print "EL ID DE TRAVELLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS", this.travel_created_id.id
        travel_active_id = this.travel_created_id.id
        # Iteracion del Waybill Creado para generar las lineas
        travel_obj = self.pool.get('tms.travel')
        travel = travel_obj.browse(cr, uid, travel_active_id, context=context)
        print "EL ID DE TRAVELLLLLLLLLLLLLLLL ESSSSSSSSSS CON EL QUE SE CREO EN LA CLASE ANTERIOR SS LLAMANDO LA CLASEEEE", str(travel.id)

#        waybill_line= waybill.waybill_line
#        fleet_id = agreement_obj.if_exist_product_fleet (cr,uid,active_id)
#        print "EL RESULTADO DE LA BUSQUEDA DE PRODUCTOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO ES IGUALLLLLLLLLLL 11111111111", fleet_id[0]
        fuel_suppliers=[]
        
        for fuel_sup in travel.shop_id.tms_fuel_sequence_ids:
            fuel_suppliers.append(fuel_sup.partner_id.id)

        for rec in self.browse(cr,uid,ids,context=context):
            if not rec.asign_travel:
                for fuel in agreement.agreement_direct_expense_line:
                    if fuel.line_type == 'fuel' and fuel.credit == True:
                        vals = {

                                'state':'draft',
                                'travel_id': travel.id,
                                'partner_id': fuel_suppliers[0],
                                'product_id': fuel.product_id.id,
                                'product_uom_qty': fuel.product_uom_qty,
                                'product_uom': fuel.product_uom.id,
                                'tax_amount': fuel.tax_amount,
                                'price_total': fuel.price_total,
                                'notes': fuel.name,
                                'create_uid' : uid,
                                'create_date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),       
                                'currency_id': agreement.currency_id.id,
                                }
                        self.pool.get('tms.fuelvoucher').create(cr, uid, vals, context)
                        print "AQUIIIIIIIIIII                   CREAMOOOOOOSSSS             LOS VALES DE COMBUSTIBLE"
                        print "AQUIIIIIIIIIII                   CREAMOOOOOOSSSS             LOS VALES DE COMBUSTIBLE", fuel.id
                        print "AQUIIIIIIIIIII                   CREAMOOOOOOSSSS             LOS VALES DE COMBUSTIBLE", fuel.name
                        print "AQUIIIIIIIIIII                   CREAMOOOOOOSSSS             LOS VALES DE COMBUSTIBLE", fuel.product_id

                    elif fuel.automatic == True:
                        vals = {

                                'state':'draft',
                                'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), 
                                'travel_id': travel.id,
                                'unit_id': False,
                                'employee_id': False,
                                'product_id': fuel.product_id.id,
                                'product_uom_qty': fuel.product_uom_qty,
                                'product_uom': fuel.product_uom.id,
                                'price_unit' : fuel.price_unit ,
                                'total': fuel.price_total,
                                'notes': fuel.name,
                                'create_uid' : uid,
                                'create_date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),       
                                'currency_id': agreement.currency_id.id,
                                'auto_expense'  : True,

                                }
                        self.pool.get('tms.advance').create(cr, uid, vals, context)      
                        print "AQUIIIIIIIIIII                   CREAMOOOOOOSSSS             LOS ANTICIPOS AUTOMATICOS DICCIONARIO DE VALORES", vals
                        print "AQUIIIIIIIIIII                   CREAMOOOOOOSSSS             LOS ANTICIPOS AUTOMATICOS", fuel.id
                        print "AQUIIIIIIIIIII                   CREAMOOOOOOSSSS             LOS ANTICIPOS AUTOMATICOS", fuel.name
                        print "AQUIIIIIIIIIII                   CREAMOOOOOOSSSS             LOS ANTICIPOS AUTOMATICOS", fuel.product_id



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


    def search_waybill_id (self, cr, uid, ids, active_id, context=None):
        context = context or {}
        waybill_obj = self.pool.get('tms.waybill')
        waybill = waybill_obj.browse(cr, uid, ids, context=context)
        print "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW", waybill
        agreement_obj = self.pool.get('tms.agreement')
        agreement = agreement_obj.browse(cr, uid, active_id, context=context)

        waybill_agreement = waybill_obj.search(cr, uid, [('agreement_origin','=',agreement.name)], limit=1)
        if waybill_agreement:
            print "TTTTTTTTTTTTTTTTTRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRUUUUUUUUUUUUUUEEEEEEEEEEEEE", waybill_agreement[0]
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
        'unit_type_id': fields.many2one('tms.unit.category', 'Unit category', required=True),
        'travel_created_id': fields.many2one('tms.travel', 'ID Travel Created', required=False, readonly=True), # Registro temporal del ID que crea del viaje
        'kit_id': openerp.osv.fields.many2one('tms.unit.kit', 'Kit', required=False),
        'unit_id': openerp.osv.fields.many2one('fleet.vehicle', 'Unit', required=False, domain=[('fleet_type', '=', 'tractor')], ),
        'trailer1_id': openerp.osv.fields.many2one('fleet.vehicle', 'Trailer1', required=False,  domain=[('fleet_type', '=', 'trailer')]),
        'dolly_id': openerp.osv.fields.many2one('fleet.vehicle', 'Dolly', required=False,        domain=[('fleet_type', '=', 'dolly')]),
        'trailer2_id': openerp.osv.fields.many2one('fleet.vehicle', 'Trailer2', required=False,  domain=[('fleet_type', '=', 'trailer')]),
        'employee_id': openerp.osv.fields.many2one('hr.employee', 'Driver', required=False, domain=[('tms_category', '=', 'driver')]),
        'employee2_id': openerp.osv.fields.many2one('hr.employee', 'Driver 2', required=False, domain=[('tms_category', '=', 'driver')]),
        'asign_travel': openerp.osv.fields.boolean('Asigned Travel Exist?'),
        'travel_ids': fields.one2many('tms.travel.wizard', 'wizard_id', 'Travel', required=False, readonly=False), # Asignar un viaje existente

    }
    _defaults = {
    #    'shop_id': : lambda self, cr, uid, context: context.get('shop_id', False) and self.pool.get('tms.agreement').browse(cr, uid, active_id, context=context)

    }

    def onchange_kit_id(self, cr, uid, ids, kit_id):
        if not kit_id:
            return {}        
        kit = self.pool.get('tms.unit.kit').browse(cr, uid, kit_id)
        return {'value' : {'unit_id': kit.unit_id.id, 'trailer1_id': kit.trailer1_id.id, 'dolly_id': kit.dolly_id.id, 'trailer2_id': kit.trailer2_id.id, 'employee_id': kit.employee_id.id}}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
