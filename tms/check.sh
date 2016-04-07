#!/bin/bash
FECHA=$(date +%Y%m%d-%H%M)
bzr diff
bzr commit -m "Revision Codificacion $FECHA"
bzr merge lp:~tms-hesatec/oerp-tms/trunk
