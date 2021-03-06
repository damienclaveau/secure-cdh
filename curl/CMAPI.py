import pycurl
import json
from StringIO import StringIO
import importlib

class CMAPI:
    def __init__(self, host, username, password):
        self.DEFAULT_HTTP_PORT = 7180
        self.DEFAULT_HTTPS_PORT = 7183
        self.SERVICE_HIVE = "Hive"
        self.SERVICE_IMPALA = "Impala"
        self.SERVICE_SOLR = "Solr"
        self.SERVICE_HUE = "Hue"
        self.SERVICES = [self.SERVICE_HIVE, self.SERVICE_IMPALA, self.SERVICE_SOLR, self.SERVICE_HUE]

        urls = str(host).split(':')
        if len(urls) == 3:
            self.host = host
        elif len(urls) == 2:
            if urls[0] == 'https':
                self.host = host + ':' + str(self.DEFAULT_HTTPS_PORT)
            else:
                self.host = host + ':' + str(self.DEFAULT_HTTP_PORT)
        elif len(urls) == 1:
            self.host = host + ':' + str(self.DEFAULT_HTTP_PORT)
        else:
            raise Exception("Invalid host: %s passed" % (host))

        self.username = username
        self.password = password
        self.service_name = None
        self.api_url = None
        self.cluster_name = None
        self.service_names = {}
        self.service_type = None
        self.version = 'v12'
        self.init()

    def init(self):
        self.version = self.get_version()
        self.api_url = "{0}/api/{1}".format(
            self.host,
            self.version
        )

        self.cluster_name = self.get_cluster_name()
        self.get_service_names()

    def get_config_url(self, service_name):
        return "{0}/clusters/{1}/services/{2}/config".format(
                self.api_url,
                self.cluster_name,
                service_name
            )

    def curl_get(self, url):
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
        c.setopt(pycurl.USERPWD, "%s:%s" % (self.username, self.password))
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        c.close()

        return buffer.getvalue()

    def curl_put(self, url, data):
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json', 'Accept: application/json'])
        c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
        c.setopt(pycurl.USERPWD, "%s:%s" % (self.username, self.password))
        c.setopt(pycurl.CUSTOMREQUEST, "PUT")
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        c.close()

        return buffer.getvalue()

    def get_services(self):
        url = "{0}/clusters/{1}/services".format(
            self.api_url,
            self.cluster_name
        )
        return self.curl_get(url)

    def get_version(self):
        url = "{0}/api/version".format(self.host)
        return self.curl_get(url)

    def get_version_number(self):
        return self.version[1:]

    def get_cluster_name(self):
        url = "{0}/clusters".format(self.api_url)
        data = json.loads(self.curl_get(url))

        return data["items"][0]["name"]

    def get_service_names(self):
        data = json.loads(self.get_services())
        for d in data["items"]:
            self.service_names[d["type"]] = d["name"]

    def get_service_name(self, type):
        if self.service_names[type] is not None:
            return self.service_names[type]

    def enable_sentry(self):
        for service in self.SERVICES:
            if service.upper() in self.service_names:
                className = service + "CMAPIClient"

                module = importlib.import_module('api.'+className)
                class_ = getattr(module, className)
                client = class_(self)

                client.enable_sentry()
