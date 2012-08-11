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
try:
    from flask import Flask
except:
    pass

from json import dumps

from ojota import Ojota
from ojota.sources import WebServiceSource


class Country(Ojota):
    plural_name = "Countries"
    pk_field = "id"
    required_fields = ("id", "name")
    data_source = WebServiceSource("http://localhost:8001")

    def __repr__(self):
        return self.name


if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/Countries/all")
    @app.route("/Countries/<id_>/data")
    def all_countries(id_=None):
        data = [{"id": "0", "name": "Argentina"},
                {"id": "1", "name": "Brazil"}]
        if id_ is None:
            ret = dumps(data)
        else:
            ret = dumps(data[int(id_)])
        return ret
    app.debug = True
    app.run(port=8001)
