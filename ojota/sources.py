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
    """Base class for all the data sources."""
    def __init__(self, data_path=None):
        """Constructor for the Source class.

        Arguments:
        data_path -- the path where the data is located.
        """
        self.data_path = data_path

    def _get_file_path(self, cls):
        """Builds the path where the data will be located.

        Arguments:
            cls -- the class with the data.
        """
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
        """Fetch the elements for a given class.

        Arguments:
            cls - the class with the data.
        """
        data_path = self._get_file_path(cls)
        return self.read_elements(cls, data_path)

    def fetch_element(self, cls, pk):
        """Fetch the elements for a given element of a class.

        Arguments:
            cls - the class with the data.
            pk - the primary key of the given element.
        """
        data_path = self._get_file_path(cls)
        return self.read_element(cls, data_path, pk)

    def save(self, cls, data):
        """Fetch the elements for a given element of a class.

        Arguments:
            cls - the class with the data.
            pk - the primary key of the given element.
        """
        file_path = self._get_file_path(cls)
        return self.write_elements(file_path, data)

    def read_elements(self, cls, filepath):
        raise NotImplementedError

    def read_element(self, cls, url, pk):
        raise NotImplementedError

    def write_elements(self, filepath, data):
        raise NotImplementedError


class JSONSource(Source):
    """Source class for the data stored with JSON format"""
    def read_elements(self, cls, filepath):
        """Reads the elements form a JSON file. Returns a dictionary containing
        the read data.

        Arguments:
            filepath -- the path for the json file.
        """
        data = json.load(open('%s.json' % filepath, 'r'))
        try:
            elements = dict((element_data[cls.pk_field], element_data)
                            for element_data in data)
        except KeyError:
            raise AttributeError("Primary key was not found. Check that you have configured the class correctly. In case yopu have check your data source")

        return elements

    def write_elements(self, filepath, data):
        data_set = open('%s.json' % filepath, 'w')
        json_data = json.dumps(data, indent=4)
        data_set.write(json_data)
        data_set.close()


class YAMLSource(Source):
    """Source class for the data stored with YAML format.

    requires the PyYaml package to run.
    """
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
    """Source class for the data stored with JSON format taken through a Web
    Service.

    requires the "request" package to run.
    """
    WSTIMEOUT = 5

    def __init__(self, data_path=None, method="get", get_all_cmd="/all",
                  get_cmd="/data", user=None, password=None, cert=None,
                  custom_call=None):
        """Constructor for the WebServiceSource class.

        Arguments:
            data_path -- the path where the data is located.
            method -- the http method that will be used witht the web service.
            Defauts to "get".
            get_all_cmd -- the WS command to fetch all the data. Defaults to "/all".
            get_cmd -- the WS command to fetch one element. Defaults to "/data"
            user -- the user name for the authentication. If not provided
            the request will not use authentication.
            password -- the password for the authentication. If not provided the
            request will not use authentication.
        """
        Source.__init__(self, data_path=data_path)

        if request_imported:
            self.get_cmd = get_cmd
            self.get_all_cmd = get_all_cmd
            self.custom_call = custom_call if custom_call is not None else ""
            self.cert = cert
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
        """Reads the elements form a WS request. Returns a dictionary containing
        the read data.

        Arguments:
            cls -- the data class.
            url -- the path for the WS.
        """
        _url = url + self.get_all_cmd
        verify = self.cert is not None
        response = self.method(_url, timeout=self.WSTIMEOUT, auth=self.auth,
                               cert=self.cert, verify=verify)
        data = response.json
        elements = dict((element_data[cls.pk_field], element_data)
                        for element_data in data)
        return elements

    def read_element(self, cls, url, pk):
        """Reads one element elements form a JSON file. Returns a dictionary
        containing the read data.

        Arguments:
            cls -- the data class.
            url -- the path for the WS.
            pk -- the primary key.
        """
        _url = "%s/%s%s" % (url, pk, self.get_cmd)
        verify = self.cert is not None
        response = self.method(_url, timeout=self.WSTIMEOUT, auth=self.auth,
                               cert=self.cert, verify=verify)
        data = response.json
        element = {data[cls.pk_field]: data}
        return element