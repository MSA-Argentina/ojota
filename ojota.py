import json
import os


PATH_DATOS_JSON = "datos_json"

def cod_datos_actual(cod_datos):
    """Setea el juego de datos actual."""
    SerializadoJson.COD_DATOS_ACTUAL = cod_datos


class SerializadoJson(object):
    """Clase con instancias listadas en un archivo json."""
    COD_DATOS_ACTUAL = ''
    plural_name = 'SerializadosJson' # redefinir al heredar
    json_en_raiz = True # redefinir al heredar
    pk_field = "pk"
    required_fields = None
    
    @property
    def primary_key(self):
        return getattr(self, self.pk_field)
    
    def __init__(self, _pk=None, **kwargs):
        if self.required_fields is not None:
            _requeridos = list(self.required_fields)
            _requeridos.append(self.pk_field)
            
            if not all([key in kwargs for key in _requeridos]):
                raise AttributeError

        for key, val in kwargs.iteritems():
            setattr(self, key, val)
            
    @classmethod
    def _leer_json(cls):
        """Lee las instancias desde json y arma un dict con la clave
           especificada en el parametro clave.
           Admite filtrar por mesa cuando los datos son de un json que esta en
           el subdirectorio de datos que una mesa usa."""
        nombre_cache = '_cache_' + cls.plural_name

        if not cls.json_en_raiz and SerializadoJson.COD_DATOS_ACTUAL:
            nombre_cache += '_' + SerializadoJson.COD_DATOS_ACTUAL

        if nombre_cache not in dir(cls):
            # se pluraliza el nombre de la clase para obtener el nombre del
            # archivo (ej: Persona -> Personas.json)
            if cls.json_en_raiz or not SerializadoJson.COD_DATOS_ACTUAL:
                path_json = os.path.join(PATH_DATOS_JSON,
                                         cls.plural_name + '.json')
            else:
                path_json = os.path.join(PATH_DATOS_JSON,
                                         SerializadoJson.COD_DATOS_ACTUAL,
                                         cls.plural_name + '.json')

            datos = json.load(open(path_json, 'r'))
            elementos = dict((datos_elemento[cls.pk_field], datos_elemento)
                             for datos_elemento in datos)
            setattr(cls, nombre_cache, elementos)
        return getattr(cls, nombre_cache)

    @classmethod
    def get(cls, pk=None, **kargs):
        """Obtiene el primer elemento que cumpla con las condiciones."""
        if pk:
            kargs[cls.pk_field] = pk
        if kargs.keys() == [cls.pk_field]:
            pk = kargs[cls.pk_field]
            todos = cls._leer_json()
            if pk in todos:
                return cls(**todos[pk])
            else:
                return None
        else:
            resultado = cls.all(**kargs)
            if resultado:
                return resultado[0]
            else:
                return None

    @classmethod
    def _objetize(cls, datos):
        return [cls(**datos_elemento)
                for datos_elemento in datos]

    @classmethod
    def _filter(cls, datos, filtros):
        filtrados = [datos_elemento
                     for datos_elemento in datos
                     if all(datos_elemento[campo] == valor
                            for campo, valor in filtros.items())]
        return filtrados

    @classmethod
    def _sort(cls, lista, campos_orden):
        campos_orden = [x.strip() for x in campos_orden.split(',')]

        for campo_orden in reversed(campos_orden):
            if campo_orden.startswith('-'):
                invertir = True
                campo_orden = campo_orden[1:]
            else:
                invertir = False

            lista = sorted(lista,
                           key=lambda e: getattr(e, campo_orden),
                           reverse=invertir)
        return lista

    @classmethod
    def all(cls, **kargs):
        """Obtiene la lista de elementos que cumplen las condiciones."""
        elementos = cls._leer_json().values()
        campos_orden = None
        if 'sorted' in kargs:
            campos_orden = kargs['sorted']
            del kargs['sorted']

        if kargs:
            elementos = cls._filter(elementos, kargs)

        lista = cls._objetize(elementos)

        if campos_orden:
            lista = cls._sort(lista, campos_orden)

        return lista

    def __eq__(self, other):
        same_pk = self.primary_key == other.primary_key
        same_class = self.__class__ is other.__class__ 
        return same_pk and same_class
        
    def __repr__(self):
        return '%s<%s>' % (self.__class__.__name__, self.primary_key)	


class Persona(SerializadoJson):
    """Lista que agrupa personas."""
    plural_name = 'Personas'
    pk_field = 'codigo'
    
    required_fields = ('nombre', 'apellido', 'edad', 'estatura', 'cod_equipo')
        
    
