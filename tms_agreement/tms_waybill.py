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


# Extra data fields for Waybills & Negotiations
class tms_waybill_extradata(osv.osv):
    _name = "tms.waybill.extradata"
    _inherit = "tms.waybill.extradata"
    _columns = {        
        'agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
        'agreement_control': fields.boolean('Agreement Control', readonly=True),

    }

tms_waybill_extradata()

class tms_waybill(osv.osv):
    _name = "tms.waybill"
    _inherit = "tms.waybill"
    _columns = {        
        'agreement_origin': fields.char('Source Agreement', size=256, help="Reference of the document that generated this agreement request.",readonly=True),
        'agreement': fields.boolean('Agreement', readonly=True),
        'agreement_id': fields.many2one('tms.agreement', 'Agreement Reference'),
    }


############### IMPORTANTEEEE!!!!!!!!!!!!!

############### PRUEBAS CON EL METODO SUPER BASICAMENTE SOBREESCRIBIMOS EL METODO ACTION_CONFIRM EN TMS_WAYBILL PARA QUE AL CONFIRMAR EN WAYBILL SE CONFIRME EN AGREEMENT ######

########## ELIMINAR LAS SIGUIENTES LINEAS AL TERMINAR EL MODULO DE AGREEMENT EXCEPTO EL METODO COPY YA QUE NO QUEREMOS ESOS CAMPOS DUPLICADOS EN WAYBILL

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'agreement_origin' : False,
            'agreement': False,
        })
        return super(tms_waybill, self).copy(cr, uid, id, default, context=context)   
    
    def action_confirm(self, cr, uid, ids, *args):
        res = super(tms_waybill, self).action_confirm(cr, uid, ids)
        agreement_obj = self.pool.get('tms.agreement')
        agreement_id = []
        for waybill in self.browse(cr, uid, ids, context=None):
            agreement_id = agreement_obj.search(cr, uid, [('name','=',waybill.agreement_origin)], limit=1)
#            agreement_b =  agreement_obj.browse(cr, uid, agreement_id, context=None)
#            print "EEEEEEEEEEEEEEEEEEEEEEEEEEELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL RESSSSSSSSUUUUULLLLTTTTTTTAAAAAAAADDDDOOOOO EEEEEESSSSSSS AGREEMENT", agreement_b.name
#            print "EEEEEEEEEEEEEEEEEEEEEEEEEEELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL RESSSSSSSSUUUUULLLLTTTTTTTAAAAAAAADDDDOOOOO EEEEEESSSSSSS", agreement_b.id
        # for agreement in agreement_obj.browse(cr, uid, agreement_id, context=None):
        #     print "EEEEEEEEEEEEEEEEEEEEEEEEEEELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL RESSSSSSSSUUUUULLLLTTTTTTTAAAAAAAADDDDOOOOO EEEEEESSSSSSS", agreement
        #     print "EEEEEEEEEEEEEEEEEEEEEEEEEEELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL RESSSSSSSSUUUUULLLLTTTTTTTAAAAAAAADDDDOOOOO EEEEEESSSSSSS", agreement.id
        #     print "EEEEEEEEEEEEEEEEEEEEEEEEEEELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL RESSSSSSSSUUUUULLLLTTTTTTTAAAAAAAADDDDOOOOO EEEEEESSSSSSS", agreement.name
        #     print "EEEEEEEEEEEEEEEEEEEEEEEEEEELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL RESSSSSSSSUUUUULLLLTTTTTTTAAAAAAAADDDDOOOOO EEEEEESSSSSSS", agreement.state
        #     agreement.write({'state':'confirmed'})

        return res

tms_waybill()

################HERENCIAS A TMS###################3
class tms_waybill_line(osv.osv):
    _name = "tms.waybill.line"
    _inherit = "tms.waybill.line"
    _columns = {        
        'agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
        'agreement_control': fields.boolean('Agreement Control', readonly=True),

    }

tms_waybill_line()

class tms_waybill_shipped_product(osv.osv):
    _name = "tms.waybill.shipped_product"
    _inherit = "tms.waybill.shipped_product"
    _columns = {        
        'agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', readonly=True),
        'agreement_control': fields.boolean('Agreement Control', readonly=True),

    }

tms_waybill_shipped_product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
