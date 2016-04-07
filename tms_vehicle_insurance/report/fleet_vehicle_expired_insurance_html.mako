<html>
<head>
    <style type="text/css">
        ${css}
    </style>
    <title>Expired or To expire Driver Licenses.pdf</title>
    
</head>
   <body>
        <table  width="100%">
            <tr>
                <td style="text-align:center;">
                    <h2><b>${ _("Fleet Vehicle Insurance Policies to expire or expired before") } ${ formatLang(data['date'],date=True) }</b></h2>
                </td>
            </tr>
        </table>
        <table  width="20%" align="center" class="cell_extended">
            <tr>
                <td style="text-align:center;" class="cell_extended">${ _('Records:') } ${ data['count'] }</td>                
            </tr>
        </table>
        <br />
        <table width="100%" class="cell_extended">
            <thead>
                <tr>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Vehicle') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Model') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('License Plate') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Type') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Insurance Policy') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Insurance Policy Data') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Insurance Policy Expiration') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Days to expire (from today)') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Insurance Policy Supplier') }</b>
                    </th>                    
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Vehicle from Supplier') }</b>
                    </th>
                </tr>
            </thead>
            <tbody>
            %for vehicle in objects :            
                <tr>                    
                    <td style="text-align:left;" class="cell_extended">${vehicle.name or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${vehicle.model_id.name or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${vehicle.license_plate or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${ (_('Motorized Unit') if vehicle.fleet_type=='tractor' else _('Trailer') if vehicle.fleet_type=='trailer' else _('Dolly') if vehicle.fleet_type=='dolly' else _('Other') ) or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${vehicle.insurance_policy or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${vehicle.insurance_policy_data or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${vehicle.insurance_policy_expiration or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${vehicle.insurance_policy_days_to_expire or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${vehicle.insurance_supplier_id.name or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${ ('X' if vehicle.supplier_unit else '') or ''| entity}</td>
                </tr>
            %endfor
            </tbody>
        </table>
       <p style="page-break-after:always">
        </p>
       
</body>
</html>