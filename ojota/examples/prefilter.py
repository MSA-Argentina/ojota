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
from __future__ import print_function
import os

from ojota import set_data_source
from ojota.base import OjotaHierarchy

file_path = (os.path.dirname(os.path.abspath(__file__)))
set_data_source(os.path.join(file_path, "data"))


class Place(OjotaHierarchy):
    plural_name = "Places"
    pk_field = "id"
    required_fields = ("id", "name")
    default_order = ("id")


class City(Place):
    prefilter = {"type": "City"}
    cache_name = "City"


class Zone(Place):
    prefilter = {"type": "Zone"}
    cache_name = "Zone"


if __name__ == '__main__':
    print([city for city in Place.all()])
    print([city for city in City.all()])
    print([city for city in Zone.all()])
