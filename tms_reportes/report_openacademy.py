# -*- coding: utf-8 -*-

from openerp.report import report_sxw
from openerp.tools.translate import _
#from report_webkit import report_helper
#from report_webkit import webkit_report
import time
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

class advance_report(report_sxw.rml_parse): # report_sxw es para decirle que va a tomar esa libreria de python
    def __init__(self, cr, uid, name,context=None): # Esta clase no genera nada en base de datos
        super(advance_report, self).__init__(cr, uid, name, context=context) # con super tomamos la clase super ya explicada anteriormente
        
        self.localcontext.update({ # un diccionario definido como localcontext que update va contener todos los parametros para nuestro reporte
            'time': time,
        })
    

report_sxw.report_sxw( 
    'report.tms.advance', #report.%s   donde %s es el nombre del reporte en el xml siempre va report mas el nombre de nuestra clase
    'tms.advance', # aqui es el nombre de la clase de nuestra clase session que contendra nuestro reporte
    'tms_reportess/Anticipos.rml',#addons/path_rml_del_xml la ruta de nuestro rml se encuentra en nuestro sxw
    parser=advance_report,# por ultimo un parse con el nombre de la clase
    header=False # le decimos que nuestra cabecera sea False
)

class expense_report(report_sxw.rml_parse): # report_sxw es para decirle que va a tomar esa libreria de python
    def __init__(self, cr, uid, name,context=None): # Esta clase no genera nada en base de datos
        super(expense_report, self).__init__(cr, uid, name, context=context) # con super tomamos la clase super ya explicada anteriormente
        
        self.localcontext.update({ # un diccionario definido como localcontext que update va contener todos los parametros para nuestro reporte
            'time': time,
        })
    

report_sxw.report_sxw( 
    'report.tms.expense', #report.%s   donde %s es el nombre del reporte en el xml siempre va report mas el nombre de nuestra clase
    'tms.expense', # aqui es el nombre de la clase de nuestra clase session que contendra nuestro reporte
    'tms_reportess/Comprobacion.rml',#addons/path_rml_del_xml la ruta de nuestro rml se encuentra en nuestro sxw
    parser=expense_report,# por ultimo un parse con el nombre de la clase
    header=False # le decimos que nuestra cabecera sea False
)


class fuelvoucher_report(report_sxw.rml_parse): # report_sxw es para decirle que va a tomar esa libreria de python
    def __init__(self, cr, uid, name,context=None): # Esta clase no genera nada en base de datos
        super(fuelvoucher_report, self).__init__(cr, uid, name, context=context) # con super tomamos la clase super ya explicada anteriormente
        
        self.localcontext.update({ # un diccionario definido como localcontext que update va contener todos los parametros para nuestro reporte
            'time': time,
        })
    
    

report_sxw.report_sxw( 
    'report.tms.fuelvoucher', #report.%s   donde %s es el nombre del reporte en el xml siempre va report mas el nombre de nuestra clase
    'tms.fuelvoucher', # aqui es el nombre de la clase de nuestra clase session que contendra nuestro reporte
    'tms_reportess/Combustible.rml',#addons/path_rml_del_xml la ruta de nuestro rml se encuentra en nuestro sxw
    parser=fuelvoucher_report,# por ultimo un parse con el nombre de la clase
    header=False # le decimos que nuestra cabecera sea False
)

class tms_report_webkit(report_sxw.rml_parse):
   def __init__(self, cr, uid, name, context):
        super(tms_report_webkit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw(
    'report.tms.waybill.webkit',
    'tms.waybill',
    'tms_reportess/Cartaporte.mako',
    parser=tms_report_webkit,
    header=False
)

class maintenance_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context=None):
        super(maintenance_report,self).__init__(cr,uid,name,context=context)

        self.localcontext.update({
            'time':time
            })

report_sxw.report_sxw(
    'report.tms.maintenance.order',
    'tms.maintenance.order',
    'tms_reportess/mtto_report.rml',
    parser=maintenance_report,
    header=False,
    )


