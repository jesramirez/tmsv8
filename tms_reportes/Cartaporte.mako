<html>

<head>
<style type="text/css">
        ${css}
    </style>
    <title>CARTA PORTE.pdf</title>
    <meta charset="UTF-8">
</head>
<body>

%for o in objects:




<table style="font-size:60%" border="0" cellspacing="0">
	
	<tr>
		<td rowspan="3" width="20%"><img src="data:image/jpeg;base64,${o.company_id.logo}" style="max-width:100%;height:auto;"/></td>
		<td rowspan="4" colspan="3" width="60%"> <center><b>${o.shop_id.company_id.name or ''} <br/>DIVISION TRANSPORTES DE CARGA <br/>${o.shop_id.company_id.street or ''} ${o.shop_id.company_id.l10n_mx_street3 or ''} ${o.shop_id.company_id.l10n_mx_street4 or ''} ${o.shop_id.company_id.street2 or ''} ${o.shop_id.company_id.zip or ''} ${o.shop_id.company_id.city or ''} ${o.shop_id.company_id.state_id.name or ''} ${o.shop_id.company_id.country_id.name or ''} <br/> ${o.shop_id.company_id.vat or ''} <br/>SERVICIO PUBLICO FEDERAL
		</b></center>
		</td>
		<td bgcolor="black" colspan="2" width="20%"><font color="white"><center><b>Carta Porte: Translado</b></center></font></td>
	</tr>
	<tr>
		<td style="border-left:2px solid #000000;border-right:2px solid #000000" colspan="2"><center>${o.name}</center></td>
	</tr>
	<tr>
		<td bgcolor="black" colspan="2"><font color="white"><center><b>Fecha/Hora</b></center></font></td>
	</tr>

	<tr>
		<td><center>AUTORIZACION S.C.T. CLAVE CR0933</center></td>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000;border-right:2px solid #000000" colspan="2"><center>${o.date_order}</center></td>
	</tr>
	<tr>
		<td style="border-bottom:2px solid #000000" colspan="3" width="50%"><b>LUGAR Y FECHA DE EXPEDICION: </b> ${o.shop_id.company_id.city or ''}, ${o.shop_id.company_id.state_id.name or ''} ${o.date_order or ''}</td>
		<td style="border-bottom:2px solid #000000" colspan="3" width="50%">PERSONA MORAL DE REGIMEN SIMPLIFICADO<br/> CONFORME A LA LEY DE ISR</td>
	</tr>
	</tr>
	<tr>
	<td style="border-left:2px solid #000000" colspan="3" width="50%"><b>Cliente:</b> ${o.partner_id.name} </td>
	<td style="border-right:2px solid #000000" colspan="3" width="50%"><b>RFC:</b> ${o.partner_id.vat}</td>
	</tr>

	<tr>
	<td style="border-left:2px solid #000000" colspan="3" width="50%"><b>Direccion:</b> ${o.partner_id.street or ''} ${o.partner_id.l10n_mx_street3 or ''} </td>
	<td style="border-right:2px solid #000000" colspan="3" width="50%"><b>Colonia:</b> ${o.partner_id.street2 or ''}	</td>
	</tr>
	<tr>
	<td style="border-bottom:2px solid #000000; border-left:2px solid #000000" colspan="3" width="50%"><b>Ciudad y Edo:</b> ${o.partner_id.city or ''}, ${o.partner_id.state_id.name or ''}</td>
		
		<td style="border-bottom:2px solid #000000" colspan="2"><b>C.P.</b> ${o.partner_id.zip or ''}</td>
		<td style="border-bottom:2px solid #000000; border-right:2px solid #000000" colspan="1"><b>Tel:</b> ${o.partner_id.phone or ''}</td>
	</tr>

	<tr>
		<td style="border-left:2px solid #000000;border-right:2px solid #000000" colspan="3" width="50%"><b>Origen:</b> ${o.departure_address_id.name or ''}</td>
		<td style="border-right:2px solid #000000" colspan="3" width="50%"><b>Destino:</b> ${o.arrival_address_id.name or ''}</td>
	</tr>
	<tr>
		<td style="border-left:2px solid #000000;border-right:2px solid #000000" colspan="3"><b>RFC:</b> ${o.departure_address_id.vat or ''}</td>
		<td style="border-right:2px solid #000000" colspan="3"><b>RFC:</b> ${o.arrival_address_id.vat or ''}</td>
	</tr>
	<tr>
		<td style="border-left:2px solid #000000;border-right:2px solid #000000" colspan="3"><b>Dirección:</b> ${o.departure_address_id.street or ''}</td>
		<td style="border-right:2px solid #000000" colspan="3"><b>Dirección:</b> ${o.arrival_address_id.street or ''}</td>
	</tr>
	<tr>
		<td style="border-left:2px solid #000000;border-right:2px solid #000000" colspan="3"><b>Colonia:</b> ${o.departure_address_id.street2 or ''}</td>
		<td style="border-right:2px solid #000000" colspan="3"><b>Colonia:</b> ${o.arrival_address_id.street2 or ''}</td>
	</tr>
	<tr>
		<td style="border-left:2px solid #000000" colspan="2"><b>Ciudad y Edo:</b> ${o.departure_address_id.city or ''}, ${o.departure_address_id.state_id.name or ''}<b>C.P.</b>${o.departure_address_id.zip or ''}</td>

		<td style="border-right:2px solid #000000" width="20%"><b>Tel:</b> ${o.departure_address_id.phone or ''}</td>
	
		<td colspan="2"><b>Ciudad y Edo:</b> ${o.arrival_address_id.city or ''}, ${o.arrival_address_id.state_id.name or ''} <b>C.P.</b> ${o.arrival_address_id.zip or ''}</td>
		<td style="border-right:2px solid #000000"><b>Tel:</b> ${o.arrival_address_id.phone or ''}</td>

	</tr>
	<tr>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000;border-right:2px solid #000000" colspan="3"><b>Recoger en:</b> ${o.upload_point or ''}</td>
		<td style="border-bottom:2px solid #000000;border-right:2px solid #000000" colspan="3"><b>Entregar en:</b> ${o.download_point or ''}</td>
	</tr>
</table>




<table style="font-size:60%" border="0" cellspacing="0">
	<tr>
	

		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000" colspan="2"><b>Condiciones de pago:</b>
		%if o.agreement_origin:
			${o.agreement_id.payment_term.name or ''}<br/>
		%else:
			
		%endif
		</td>
		<td style="border-bottom:2px solid #000000" colspan="2"><b>Cuota por tonelada:</b>$ 1.00<br/></td>
				
		<td style="border-bottom:2px solid #000000; border-right:2px solid #000000" colspan="2"><b>Valor Declarado:</b>$ 1.00<br/></td>

		

	</tr>
	<tr>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000" width="17.5%"><center><b>CANTIDAD</b></center></td>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000" rowspan="2" width="17.5"><center><b> QUE EL REMITENTE <br>DICE CONTIENE</br> </b></center></td>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000" rowspan="2" width="17.5%"><center><b> PESO TONS.</b></center></td>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000" width="17.5%"><center><b>VOLUMEN</b></center></td>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000" rowspan="2" width="15%"><center><b>CONCEPTO</b></center></td>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000;border-right:2px solid #000000" rowspan="2" width="15%"><center><b>IMPORTE</b></center></td>
	</tr>
	<tr>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000"><center><b>NUM. AMBALAJE</b></center></td>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000"><center><b>MTS PESO ESTIM</b></center></td>
	</tr>
	<tr>
	
		<td valign="top" style="border-bottom:2px solid #000000;border-left:2px solid #000000">
		%for x in o.waybill_line:
			${x.product_uom_qty or ''}<br/>
		%endfor
		</td>
			
			<td valign="top" style="border-bottom:2px solid #000000;border-left:2px solid #000000">
			%for p in o.waybill_shipped_product:
				${p.product_id.name or ''}
				${p.notes or ''}<br/>

			%endfor
			</td>
			<td valign="top" style="border-bottom:2px solid #000000;border-left:2px solid #000000">
			%for p in o.waybill_shipped_product:
				${p.product_uom_qty or ''}<br/>
			%endfor
			</td>
			<td valign="top" style="border-bottom:2px solid #000000;border-left:2px solid #000000">
			%for p in o.waybill_shipped_product:
				${p.product_uom.category_id.name or ''} <br/>
			%endfor
			</td>
				
		        <td valign="top" style="border-bottom:2px solid #000000;border-left:2px solid #000000">
		        %for w in o.waybill_line:
		        	${w.product_id.name or ''}<br/>
		        %endfor
		        </td>
				<td valign="top" style="border-bottom:2px solid #000000;border-left:2px solid #000000;border-right:2px solid #000000">
				$ 1.00</td>
	</tr>

	<tr>
		<td style="border-left:2px solid #000000;border-right:2px solid #000000" colspan="4"><b> Pedimento:</b></td>
		<td><b>SUBTOTAL</b></td>
		<td style="border-left:2px solid #000000;border-right:2px solid #000000">$ 1.00</td>
	</tr>
	
	<tr>
					<td style="border-left:2px solid #000000;border-right:2px solid #000000" colspan="4"><b>Ruta:</b> 
					%for v in o.travel_ids:
						${v.route_id.departure_id.name or ''}    A    ${v.route_id.arrival_id.name or ''}
					%endfor</td>
					
						
						
						<td valign="top"rowspan="4">
						%for t in o.tax_line:
							${t.tax_id.name or ''} <br/>
						%endfor </td>

						<td valign="top" style="border-left:2px solid #000000;border-right:2px solid #000000" rowspan="4">
						%for t in o.tax_line:
							$ 1.00<br/>
						%endfor </td>
						
						
						
						</tr>
						
						
				
	<tr>
					
					<td style="border-left:2px solid #000000;border-right:2px solid #000000" colspan="4"><b>Operador:</b> 
					%for v in o.travel_ids:
						${v.employee_id.name or ''}
						%endfor</td>
					</tr>

					<tr>

					%for v in o.travel_ids:
					<td style="border-left:2px solid #000000"><b>Carro:</b> ${v.unit_id.name or ''}<br/><b>Placas:</b>${v.unit_id.license_plate or ''}</td>
					<td><b>Remolque1:</b>${v.trailer1_id.name or ''}<br/><b>Placas:</b>${v.trailer1_id.license_plate or ''} </td>
					%if v.dolly_id.name:
						<td><b>Dolly:</b>${v.dolly_id.name or ''}<br/><b>Placas:</b>${v.dolly_id.license_plate} </td>
						<td style="border-right:2px solid #000000"><b>Remolque2:</b>${v.trailer2_id.name or ''}<br/><b>Placas2:</b>${v.trailer2_id.license_plate or ''}</td>
						
						%else:
							<td></td>
							<td style="border-right:2px solid #000000"> </td>

					%endif

					</tr>
					%endfor

					<tr>
	
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000" colspan="2"><b>Obs. </b> ${o.notes or ''}</td>
		<td style="border-bottom:2px solid #000000;border-right:2px solid #000000" colspan="2"><b>Inst.</b></td>
	
	</tr>
	<tr>
	
		<td style="border-bottom:2px solid #000000;border-right:2px solid #000000;border-left:2px solid #000000" colspan="4"></td>
		<td style="border-bottom:2px solid #000000"><b>TOTAL</b></td>
		<td style="border-bottom:2px solid #000000;border-left:2px solid #000000;border-right:2px solid #000000">$ 1.00</td>
	</tr>
	
	</table>
%endfor





<table style="font-size:50%" border="0">
<tr>
<td>
<center>CONTRATO DE PRESTACIÓN DE SERVICIOS QUE AMPARA ESTA CARTA DE PORTE</center>
</td>
</tr>
<tr>
<td align="justify">
PRIMERA.- Para los efectos del presente contrato de tranporte se denomina "porteador" al transportista y "Remitente" al usuario que contrate el servicio.
SEGUNDA.- El "Remitente" es reponsable de que la información proporcionada al "Porteador" sea veraz y que la documentación que entregue para efectis del transporte sea la correcta.
TERCERA.- El "Remitente debe declara al "Porteador" el tipo de mercancía o efectos de que se trate, peso, medidas y/o número de la carga que entrega para su transporte y, en su caso, el valor de la misma. La carga que se entregue a granel será pesada por el "Porteador" en el primer punto donde haya báscula apropiada o, en su defecto, aforada en metros cúbicos con la conformidad del "Remitente.
CUARTA.-  Para efectos del transporte, el "Remitente" deberá entregar al "Porteador" los documentos que las leyes y reglamentos exijan para llevar a cabo el servicio, en caso de no cumplirse con estos requisitos el "Porteador está obligado a rehusar el transporte de mercancías.
QUINTA,. Si por sospecha de falsedad en la declaracíon del contenido de un bulto el "Porteador" deseare proceder a su reconocmiento, podrá hacerlo ante testigos y con asistencia del "Remitente" o del consignatario. Si este último no concurriere, se solicitará la presencia de un inspector de la Secretaría de Comunicaciones y Transportes, y se levantará el acta correspondiente. El "Porteador" tendrá en todo caso la obligación de dejar los bultos en el esstado  en que se encontraban antes del conocimiento.
SEXTA- El "Porteador" deberá recoger y entregar la carga precisamente en los domicilios que señale el "Remitente", ajustándose a los términos y condiciones convenidos. El "Porteador" solo está obligado a llevar la carga al domicilio del consignatario para su entrega una sola vez. Si ésta no fuera recibida, se dejará aviso de que la mercancía queda a disposición del interesado en las bodegas que indique el "Porteador".
SEPTIMA.- Si la carga no fuere retirada dentro de los 30 días siguientes a aquél en que hubiere sido puesta a disposición del consignatario, el "Porteador" podría solicitar la venta en pública subasta con arreglo a lo que dispone el Código de Comercio
OCTAVA.- El "Porteador" y el "Remitente" negociarán libremente el precio del servicio, tomando en cuenta su tipo, característica de los embarques, volumen, regularidad, clase de carga y sistema de pago
NOVENA.- Si el "Remitente" desea que el "Porteador"asuma la responsabilidad por el valor de las mercancías o efecto que él declare hy que cubra toda clase de riesgos, inclusive los derivados de caso fortuito o de fuerza mayor, las partes deberán convenir un cargo adicional, equivalente al valor de la prima del seguro que se contrate, el cual se deberá expresar en la carta de porte.
DECIMA.- Cuando el importe de flete no incluya el cargo adicional, la responsabilidad del "Porteador" queda expresamente limitada a la cantidad equivalente a 15 días de salario mínimo vigente en el Distrito Federal por tonelada o cuando se trate de embarques cuyo peso sea mayor de 200kg. Pero menor de 1000kg; y a 4 días de salario mínimopor remewwsa cuando se trate de embarques con peso hasta 200kg.
DECIMA PRIMERA.- El precio del transporte deberá pagarse en origen, salvo convenio entre las partes de pago en destino. Cuando el transporte se hubiere concertado "Flete por Cobrar", la entrega de las mercancías o efectos se hará contra el pago del felte y el "Porteador" tendrá derecho a retenerlos mientras no se le cubrqa el precio convenido.
DECIMA SEGUNDA.- Si al momento de la entrega resultare algún faltante o avería, el consignatario deberá hacerla constar en ese acto en la carta de porte y formular su reclamación por escrito al "Porteador", dentro de las 24 horas siguientes
DECIMA TERCERA.- El "Porteador" queda eximido de la obligación de recibir mercanciás o efectos para su transporte, en los siguientes casos:
a) Cuando se trate de carga que por su naturaleza, peso, volumen, embalaje, defectuoso o cualquier otra circusntancia no pueda transportarse sin destruirse o sin causar daño a los demás artículos o el material rodante, salvo que la empresa de que se trate tenga el equipo adecuado.
b) Las mercancías cuyo transporte haya sido prohibido por disposiciones legales o reglamentarias. Cuando tales disposiciones no prohíban precisamente el transporte de determinadas mercancías, pero sí ordenen la presentación de ciertos documentos para que puedan ser transportadas, el "Remitente" estará obligado a entregar al "Porteador" los documentos correspondientes.
DECIMA CUARTA.- Los casos no previstos en las presentes condiciones y las quejas derivadas de su aplicación se someterán por la vía administrativa a la Secretaría de Comunicaciones y Transportes
DECIMA QUINTA.- Para el caso de que el "Remitente" contrate carro por entero, este aceptará la responsabilidad solidaria para que el "Porteador" mediante la figura de la corresponsabilidad QUE CONTEMPLA EL ARTICULO 10 DEL REGLAMENTO SOBRE EL PESO, DIMESIONES Y CAPACIDAD DE LOS VEHICULOS DE AUTOTRANSPORTE  que transitan en los caminos y puentes de jurisdicción federal, por lo que el "Remitente" queda oblicago a verificar que la carga y el vehículo que la transporta, cumplan con el peso y dimensiones máximas extablecidas en la Norma NOM-012-SCT-2-2008
Para el caso de incumplimiento e inobservancia a las dispociones que regulan el peso y dimensiones, por parte del "Remitente", este será corresponsable de las infracciones y multas de la Secretaría de Comunicaciones y Transportes
DEBO(EMOS) Y PAGARE (MOS) INCONDICIONALMENTE A LA ORDEN DE TRANSPORTES BELCHEZ, S.A. DE C.V. Y/O NELSON ARTURO BELCHEZ GONZALEZ EN LA CIUDAD DE VERACRUZ, VER, EL ________________ DE _________________ DEL_______________________ LA CANTIDAD DE _______________________________________________. LA FALTA DEL PAGO PUNTUAL DE ESTE PAGARE CAUSARA INTERESES MORATORIOS AL         % DESDE LA FECHA DE SU ACEPTACION A LA DE SU COBRO.
</td>
</tr>
<tr>
<td>
<center>
______________________________________________<br/>
Nombre y Firma de quien Recibe
</center>
</td>
</tr>
</table>

</body>

</html>
