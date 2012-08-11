import os
import json

try:
    import yaml
except ImportError:
    pass

from urllib2 import urlopen

_DATA_SOURCE = "data"

class Source(object):
    def _get_file_path(self, cls):
        if cls.data_in_root or not cls.CURRENT_DATA_CODE:
            filepath = os.path.join(_DATA_SOURCE, cls.plural_name)
        else:
            filepath = os.path.join(_DATA_SOURCE, cls.CURRENT_DATA_CODE,
                                    cls.plural_name)
        return filepath

    def fetch_elements(self, cls):
        data_path = self._get_file_path(cls)
        return self.read_elements(cls, data_path)

    def fetch_element(self, cls, pk):
        data_path = self._get_file_path(cls)
        return self.read_element(cls, data_path, pk)


class JSONSource(Source):
    def read_elements(self, cls, filepath):
        """Reads the elements form a JSON file. Returns a dictionary containing
        the read data.

        Arguments:
        filepath -- the path for the json file.
        """
        data = json.load(open('%s.json' % filepath, 'r'))
        elements = dict((element_data[cls.pk_field], element_data)
                        for element_data in data)

        return elements


class YAMLSource(Source):
    def read_elements(self, cls, filepath):
        """Reads the elements form a JSON file. Returns a dictionary containing
        the read data.

        Arguments:
        filepath -- the path for the json file.
        """
        datos = yaml.load(open('%s.yaml' % filepath, 'r'))
        elements = {}
        for key, value in datos.items():
            elements[value[cls.pk_field]] = value

        return elements


class WebServiceSource(Source):
    WSTIMEOUT = 5

    def __init__(self, method="get", get_all_cmd="/all", get_cmd="/data"):
        self.get_cmd = get_cmd
        self.get_all_cmd = get_all_cmd

    def read_elements(self, cls, url):
        """Reads the elements form a JSON file. Returns a dictionary containing
        the read data.

        Arguments:
        filepath -- the path for the json file.
        """
        _url = url + self.get_all_cmd
        print "REQUESTING", _url
        data = urlopen(_url, timeout=self.WSTIMEOUT).read()
        data = json.loads(data)
        elements = dict((element_data[cls.pk_field], element_data)
                        for element_data in data)
        return elements

    def read_element(self, cls, url, pk):
        _url = "%s/%s%s" % (url, pk, self.get_cmd)
        data = urlopen(_url, timeout=self.WSTIMEOUT).read()
        data = json.loads(data)
        element = {data[cls.pk_field]: data}
        return element