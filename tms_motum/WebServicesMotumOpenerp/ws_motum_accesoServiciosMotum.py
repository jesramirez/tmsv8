#!/usr/bin/env python
from suds.client import Client

url = 'http://motum.dnsalias.net/WS_RutasAutomaticas/RutasAutomaticas?wsdl'
client = Client(url)


usuario  = 'openerp'
password = 'openerppruebas'

print 'Usuario:  '+str(usuario)
print 'Password: '+str(password)

resultado = client.service.accesoServiciosMotum( usuario, password )
print 'Resultado de accesoServiciosMotum: '+str(resultado)







# accesoServiciosMotum(xs:string usuario, xs:string calve, )
# agregarRuta(xs:long llave, xs:string unidad, xs:string nombreRuta, xs:dateTime fechaInicio, xs:dateTime fechaFin, )
# borrarRuta(xs:long llave, xs:long idRuta, )
# cambiarRuta(xs:long llave, xs:long idRuta, xs:string nombreRuta, xs:dateTime fechaInicio, xs:dateTime fechaFin, )


