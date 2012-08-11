"""
This file is part of Ojota.

    Ojota is free software: you can redistribute it and/or modify
    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Ojota is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU  Lesser General Public License
    along with Ojota.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import json

try:
    import yaml
    yaml_imported = True
except ImportError:
    yaml_imported = False

try:
    import requests
    request_imported = True
except ImportError:
    request_imported = False

from urllib2 import urlopen

_DATA_SOURCE = "data"

class Source(object):
    def __init__(self, data_path=None):
        self.data_path = data_path
    def _get_file_path(self, cls):
        if self.data_path is None:
            data_path = _DATA_SOURCE
        else:
            data_path = self.data_path
        if cls.data_in_root or not cls.CURRENT_DATA_CODE:
            filepath = os.path.join(data_path, cls.plural_name)
        else:
            filepath = os.path.join(data_path, cls.CURRENT_DATA_CODE,
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
        if yaml_imported:
            datos = yaml.load(open('%s.yaml' % filepath, 'r'))
            elements = {}
            for key, value in datos.items():
                elements[value[cls.pk_field]] = value
        else:
            raise Exception("In order to use YAML sources you should install the 'PyYAML' package")

        return elements


class WebServiceSource(Source):
    WSTIMEOUT = 5

    def __init__(self, data_path=None, method="get", get_all_cmd="/all",
                  get_cmd="/data", user=None, password=None):
        Source.__init__(self, data_path=data_path)

        if request_imported:
            self.get_cmd = get_cmd
            self.get_all_cmd = get_all_cmd
            try:
                self.method = getattr(requests, method)
            except AttributeError:
                self.method = requests.get
            if user is not None and password is not None:
                self.auth = (user, password)
            else:
                self.auth = None
        else:
            raise Exception("In order to use Web Service sources you should install the 'requests' package")

    def read_elements(self, cls, url):
        """Reads the elements form a JSON file. Returns a dictionary containing
        the read data.

        Arguments:
        filepath -- the path for the json file.
        """
        _url = url + self.get_all_cmd
        response = self.method(_url, timeout=self.WSTIMEOUT, auth=self.auth)
        data = response.json
        elements = dict((element_data[cls.pk_field], element_data)
                        for element_data in data)
        return elements

    def read_element(self, cls, url, pk):
        _url = "%s/%s%s" % (url, pk, self.get_cmd)
        data = urlopen(_url, timeout=self.WSTIMEOUT).read()
        data = json.loads(data)
        element = {data[cls.pk_field]: data}
        return element