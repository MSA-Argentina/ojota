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

from ojota import Ojota, Relation, set_data_source
from ojota.sources import YAMLSource
from ojota.examples.example_ws import Country
from ojota.cache import Memcache

file_path = (os.path.dirname(os.path.abspath(__file__)))
set_data_source(os.path.join(file_path, "data"))


class Team(Ojota):
    plural_name = "Teams"
    pk_field = "id"
    data_source = YAMLSource()
    required_fields = ("id", "name", "color")

    def __repr__(self):
        return self.name


class Person(Ojota):
    plural_name = "Persons"
    pk_field = "id"
    required_fields = ("id", "name", "address", "age", "team_id")
    team = Relation("team_id", Team)
    country = Relation("country_id", Country)
    cache  = Memcache()

    def __repr__(self):
        return self.name
