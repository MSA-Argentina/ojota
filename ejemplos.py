from ojota import Serializado, relation

class Equipo(Serializado):
    """Lista que agrupa personas."""
    plural_name = 'Equipos'
    pk_field = 'codigo'

    required_fields = ('codigo',)


class Persona(Serializado):
    """Lista que agrupa personas."""
    plural_name = 'Personas'
    pk_field = 'codigo'

    required_fields = ('nombre', 'apellido', 'edad', 'estatura', 'cod_equipo')
    equipo = relation('cod_equipo', Equipo)


class Animal(Serializado):
    """Lista que agrupa animales."""
    plural_name = 'Animales'
    pk_field = 'codigo'