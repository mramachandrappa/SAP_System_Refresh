#!/bin/sh
sudo mkdir /usr/local/sap/
unzip nwrfsdk/Linuxx86_64/nwrfc750P_5-70002752.zip -d /usr/local/sap/
SAPNWRFC_HOME=/usr/local/sap/nwrfcsdk
sudo pip3 install pyrfc-connectors/pyrfc-2.0.1-cp37-cp37m-linux_x86_64.whl
