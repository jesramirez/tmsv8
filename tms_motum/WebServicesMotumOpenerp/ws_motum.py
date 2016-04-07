#!/usr/bin/env python
from suds.client import Client


#url = 'http://www.webservicex.net/globalweather.asmx?WSDL'
url = 'http://motum.dnsalias.net/WS_RutasAutomaticas/RutasAutomaticas?wsdl'
#url = 'http://www.webservicex.net/globalweather.asmx?WSDL'
client = Client(url)

print type(client)
print 'COntenido del Web Service:::::::::::::::::::::::::::::::::::::::: '
print client


#resultado =  client.service.GetCitiesByCountry('germany')
#print 'Resultado Ciudades::::::::::::::::: '+resultado

