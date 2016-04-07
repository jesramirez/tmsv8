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
                    <h2><b>${ _("Driver's License to expire or expired before") } ${ formatLang(data['date'],date=True) }</b></h2>
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
                    <b>${ _('ID') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Name') }</b>
                    </th>                
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('License Expiration') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Days to expire (from today)') }</b>
                    </th>
                    <th style="text-align:center;background-color: lightgray;" class="cell_extended">
                    <b>${ _('Driver from Supplier') }</b>
                    </th>
                </tr>
            </thead>
            <tbody>
            %for employee in objects :            
                <tr>
                    <td style="text-align:center;" class="cell_extended">${employee.id or ''| entity}</td>
                    <td style="text-align:left;" class="cell_extended">${employee.name or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${employee.tms_driver_license_expiration or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${employee.tms_driver_license_days_to_expire or ''| entity}</td>
                    <td style="text-align:center;" class="cell_extended">${ ('X' if employee.tms_supplier_driver else '') or ''| entity}</td>
                </tr>
            %endfor
            </tbody>
        </table>
       <p style="page-break-after:always">
        </p>
       
</body>
</html>