# secure-cdh

## Prerequisite

1. The following python packages are required to run the script included in the project:

```
pip install pycurl
pip install cm_api
pip install importlib
```

2. This also assumes that you have already install working KDC as well as Kerberos client
on all machines in the cluster. If not, please visit: https://github.com/daisukebe/krb-bootstrap
which includes script to set it up for you.

## How to run

### Get help

```
python enable-kerberos.py -h
python enable-sentry.py -h
```

### Enable Kerberos first


```
python enable-kerberos.py --cluster_name <cluster_name> <cm-host> <cm-user> <cm-pass> <kdc-host>
```

### Enable Sentry (requires Kerberos to be enabled first, need to add checking later on)

```
python enable-sentry.py --cluster_name <cluster_name> <cm-host> <cm-user> <cm-pass>
```
