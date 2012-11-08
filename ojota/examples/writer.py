import os

from ojota import Ojota, Relation, set_data_source
from ojota.sources import YAMLSource
from ojota.examples.example_ws import Country, Flag
from ojota.cache import Memcache
from ojota.examples.examples import Team
from copy import copy

file_path = (os.path.dirname(os.path.abspath(__file__)))
set_data_source(os.path.join(file_path, "data"))


class Person(Ojota):
    plural_name = "Persons"
    pk_field = "id"
    required_fields = ("id", "name", "address", "age", "team_id")
    team = Relation("team_id", Team, "persons")
    country = Relation("country_id", Country, "persons")

    def __repr__(self):
        return self.name

if __name__ == "__main__":

    p = Person.get("9")
    p.name = "juan"
    p.address = "hola"
    p.age = 10
    p.team_id = "1"
    p.save()