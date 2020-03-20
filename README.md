# SAP NW RFC SDK Installation

```Linux```

Create the SAP NW RFC SDK home directory, e.g. ```/usr/local/sap/```

Unpack the SAP NW RFC SDK archive to it, e.g. ```/usr/local/sap/nwrfcsdk/lib``` shall exist.

Set the ```SAPNWRFC_HOME``` env variable: ```SAPNWRFC_HOME=/usr/local/sap/nwrfcsdk```

Include the lib directory in the library search path:

As root, create a file ```/etc/ld.so.conf.d/nwrfcsdk.conf``` and enter the following values:

```
# include nwrfcsdk
/usr/local/sap/nwrfcsdk/lib
```
As ```root```, run the command ```ldconfig```. To check if libraries are installed:

$ ldconfig -p | grep sap # should show something like:
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

# Python Connector Installation

```Linux```

* Install Python 3

* Install pip3 if not already included: https://pip.pypa.io/en/stable/installing/

* Install the Python connector from the latest release

`wget https://github.com/SAP/PyRFC/releases/download/2.0.0/pyrfc-2.0.0-cp38-cp38-linux_x86_64.whl`

`pip3 install pyrfc-1.9.94-cp37-cp37m-linux_x86_64.whl`

Please look up the correct wheel name, depending on your platform and Python version.

Run python and type from pyrfc import *. If this finishes silently, without oputput, the installation was successful.
# Development Setup
- Create a Virtual Env, if desired
    - `python3 -m venv venv`
    - `source venv/bin/activate`
- `pip3 install --editable .`

