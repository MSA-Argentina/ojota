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

from ojota import Serializado, Relation


class Equipo(Serializado):
    """Lista que agrupa personas."""
    plural_name = 'Equipos'
    pk_field = 'codigo'

    required_fields = ('codigo',)


class Persona(Serializado):
    """Lista que agrupa personas."""
    plural_name = 'Personas'
    pk_field = 'codigo'

    #required_fields = ('nombre', 'apellido', 'edad', 'estatura', 'cod_equipo')
    equipo = Relation('cod_equipo', Equipo, related_name='personas')


class Animal(Serializado):
    """Lista que agrupa animales."""
    plural_name = 'Animales'
    pk_field = 'codigo'