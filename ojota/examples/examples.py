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

from ojota import Ojota, Relation, set_data_source, Callback
from ojota.base import OjotaHierarchy
from ojota.cache import Memcache
from ojota.examples.example_ws import Country, Flag
from ojota.sources import YAMLSource, CSVSource, XLSSource

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
    team = Relation("team_id", Team, "persons")
    country = Relation("country_id", Country, "persons")
    age_str = Callback("age", lambda x:str(x))

    def __repr__(self):
        return self.name


class Customer(Ojota):
    plural_name = "Customers"
    pk_field = "id"
    required_fields = ("id", "name", "address", "age")
    data_source = CSVSource()


class OtherPeople(Ojota):
    plural_name = "OtherPeople"
    pk_field = "id"
    data_source = XLSSource()
    required_fields = ("id", "name", "last_name", "age")


class Place(OjotaHierarchy):
    plural_name = "Places"
    pk_field = "id"
    required_fields = ("id", "name")
    default_order = ("id")



if __name__ == "__main__":
    #p = Person(id=1, name="juan", last_name = "perez", age=30)
    #p.save()
    persons = Person.all()
    print persons
    #print [p for p in persons]
    #print [p for p in persons.many(age=35)]
    #print persons.one(age=35)
    #print persons[0:1]
    #print persons[0]
    #print persons[0:2]

    places = Place.all()
    print [p.parent for p in Place.all()]
    print places[1].is_sibling(places[4])
    print [p for p in places[1].children()]


