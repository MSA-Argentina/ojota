from flask import Flask
from json import dumps

from ojota import Ojota
from ojota.base import set_data_source
from ojota.sources import WebServiceSource


set_data_source("http://localhost:8001")


class Country(Ojota):
    plural_name = "Countries"
    pk_field = "id"
    required_fields = ("id", "name")
    data_source = WebServiceSource()

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
