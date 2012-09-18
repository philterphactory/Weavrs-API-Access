import logging

from hashlib import md5

import urllib
import httplib2



try:
    from django.utils import simplejson as json
except ImportError:
    import simplejson as json


class WeavrsClient(object):
    """
    A client wrapper calling Weavrs API, includes Authorization header
    """

    API_PATH = 'api/2'
    server = None
    consumer_key = None

    def __init__(self, server, consumer_key):
        self.server = server
        self.consumer_key = consumer_key

    def find_user_by_email(self, email):
        return self.get("/find/user/", False, email=email)

    def get(self, path, cache=True, **params):
        url = "http://%s/%s%s" % (self.server, WeavrsClient.API_PATH, path)

        if params:
            # Don't add request param if value is None
            request_params = {}
            for key in params:
                if params[key]:
                    request_params[key] = params[key]
            encoded_query_path = urllib.urlencode(request_params, doseq=True)
            url = "%s?%s" % (url, encoded_query_path)

        http = httplib2.Http()
        print url
        resp, content = http.request(url, "GET", headers={'Authorization': self.consumer_key} )

        try:
            content = json.loads(content)
        except ValueError:
            logging.warn("Can't decode response: %s"%content)
            raise

        return content

    def post(self, path, **params):
        url = "http://%s/%s%s" % (self.server, WeavrsClient.API_PATH, path)

        if params:
            # Don't add request param if value is None
            request_params = {}
            for key in params:
                if params[key]:
                    request_params[key] = params[key]
            encoded_query_path = urllib.urlencode(request_params, doseq=True)
            url = "%s?%s" % (url, encoded_query_path)

        http = httplib2.Http()
        resp, content = http.request(url, "GET", headers={'Authorization': self.consumer_key} )

        try:
            content = json.loads(content)
        except ValueError:
            logging.warn("Can't decode response: %s"%content)
            raise

        return content

