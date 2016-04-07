#!/usr/bin/env python
from suds.client import Client

url = 'http://motum.dnsalias.net/WS_RutasAutomaticas/RutasAutomaticas?wsdl'
url = '192.168.0.144/WS_RutasAutomaticas/RutasAutomaticas?wsdl'
client = Client(url)


usuario  = 'openerp'
password = 'openerppruebas'

print 'Usuario:  '+str(usuario)
print 'Password: '+str(password)

resultado = client.service.accesoServiciosMotum( usuario, password )
print 'Resultado de accesoServiciosMotum, Clave CLiente: '+str(resultado)
print '\n\n\n\n'



unidad       = 'La Mula'
nombre_ruta  = 'Zongolica-Orizaba'
fecha_inicio = '2012/12/12'
fecha_fin    = '2013/01/20'
print 'Unidad:       '+str(unidad)
print 'Ruta:         '+str(nombre_ruta)
print 'Fecha Inicio: '+str(fecha_inicio)
print 'Fecha Fin:    '+str(fecha_fin)

resultado = client.service.agregarRuta( resultado, unidad, nombre_ruta, fecha_inicio, fecha_fin )
print 'Resultado de agregarRuta, ID_Ruta: '+str(resultado)
print '\n\n\n\n'



# accesoServiciosMotum(xs:string usuario, xs:string calve, )
# agregarRuta(xs:long llave, xs:string unidad, xs:string nombreRuta, xs:dateTime fechaInicio, xs:dateTime fechaFin, )
# borrarRuta(xs:long llave, xs:long idRuta, )
# cambiarRuta(xs:long llave, xs:long idRuta, xs:string nombreRuta, xs:dateTime fechaInicio, xs:dateTime fechaFin, )


