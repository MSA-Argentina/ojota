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
from __future__ import absolute_import
try:
    from flask import Flask
except:
    pass

from json import dumps

from ojota import Ojota, Relation
from ojota.sources import WebServiceSource


class Flag(Ojota):
    plural_name = "Flags"
    pk_field = "id"
    required_fields = ("id", "description")
    data_source = WebServiceSource("http://localhost:8001")

    def __repr__(self):
        return self.description


class Country(Ojota):
    plural_name = "Countries"
    pk_field = "id"
    required_fields = ("id", "name")
    data_source = WebServiceSource("http://localhost:8001")
    country = Relation("flag_id", Flag, "countries")

    def __repr__(self):
        return self.name


if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/Countries/all")
    @app.route("/Countries/<id_>/data")
    def all_countries(id_=None):
        data = [{"id": "0", "name": "Argentina", "flag_id": "0"},
                {"id": "1", "name": "Brazil", "flag_id": "1"}]
        if id_ is None:
            ret = dumps(data)
        else:
            ret = dumps(data[int(id_)])
        return ret

    @app.route("/Flags/all")
    @app.route("/Flags/<id_>/data")
    def all_flags(id_=None):
        data = [{"id": "0", "description": "Blue and White"},
                {"id": "1", "description": "Green, Yellow and Blue"}]
        if id_ is None:
            ret = dumps(data)
        else:
            ret = dumps(data[int(id_)])
        return ret
    app.debug = True
    app.run(port=8001)
