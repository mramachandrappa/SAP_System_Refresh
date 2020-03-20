# PyRFC - The Python RFC Connector

The pyrfc Python package provides Python bindings for SAP NetWeaver RFC Library, for a comfortable way of calling ABAP modules from Python and Python modules from ABAP, via SAP Remote Function Call (RFC) protocol.

# Set UP
### Step 1 : SAP NW RFC SDK Installation

Information on where to download the SAP NW RFC SDK [here](https://support.sap.com/en/product/connectors/nwrfcsdk.html)

`Linux`

* Create the SAP NW RFC SDK home directory, e.g. `/usr/local/sap/`

* Unpack the SAP NW RFC SDK archive to it, e.g. `/usr/local/sap/nwrfcsdk/lib` shall exist.

    `unzip nwrfsdk/Linuxx86_64/nwrfc750P_5-70002752.zip -d /usr/local/sap/`

* Set the `SAPNWRFC_HOME` env variable: `SAPNWRFC_HOME=/usr/local/sap/nwrfcsdk`

* Include the lib directory in the library search path:

   As root, create a file `/etc/ld.so.conf.d/nwrfcsdk.conf` and enter the following values:

    ```
    # include nwrfcsdk
    /usr/local/sap/nwrfcsdk/lib
    ```
As `root`, run the command `ldconfig`. To check if libraries are installed:

$ `ldconfig -p | grep sap` # should show something like:
  ```
  libsapucum.so (libc6,x86-64) => /usr/local/sap/nwrfcsdk/lib/libsapucum.so
  libsapnwrfc.so (libc6,x86-64) => /usr/local/sap/nwrfcsdk/lib/libsapnwrfc.so
  libicuuc.so.50 (libc6,x86-64) => /usr/local/sap/nwrfcsdk/lib/libicuuc.so.50
  libicui18n.so.50 (libc6,x86-64) => /usr/local/sap/nwrfcsdk/lib/libicui18n.so.50
  libicudecnumber.so (libc6,x86-64) => /usr/local/sap/nwrfcsdk/lib/libicudecnumber.so
  libicudata.so.50 (libc6,x86-64) => /usr/local/sap/nwrfcsdk/lib/libicudata.so.50
  libgssapi_krb5.so.2 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2
  libgssapi.so.3 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libgssapi.so.3
$
```

### Step 2 : Python Connector Installation

```Linux```

* Install Python 3

* Install pip3 if not already included: https://pip.pypa.io/en/stable/installing/

* Install the Python connector from the [latest release](https://github.com/SAP/PyRFC/releases/tag/2.0.4)

Please look up the correct wheel name, depending on your platform and Python version.

For current setup wheel is already downloaded, you can install it using,

`pip3 install pyrfc-connectors/pyrfc-2.0.1-cp37-cp37m-linux_x86_64.whl`

Run python and type `from pyrfc import *` If this finishes silently, without errors, the installation was successful.

# Development Setup
- Create a Virtual Env, if desired
    - `python3 -m venv venv`
    - `source venv/bin/activate`
- `pip3 install --editable .`

