import json
import yaml
import os

PATH_DATOS = "datos"

def cod_datos_actual(cod_datos):
    """Setea el juego de datos actual."""
    Serializado.COD_DATOS_ACTUAL = cod_datos

class Relation(object):
    def __init__(self, attr_fk, to_class, related_name=None):
        self.attr_fk = attr_fk
        self.to_class = to_class
        self.related_name = related_name

    def get_property(self):
        def method(method_self):
            fk = getattr(method_self, self.attr_fk)
            return self.to_class.get(fk)
        return property(method)

    def set_reversed_property(self, from_class):
        def method(method_self):
            pk = method_self.primary_key
            params = {self.attr_fk: pk}
            return from_class.all(**params)

        if self.related_name:
            prop = property(method)
            setattr(self.to_class, self.related_name, prop)


class MetaSerializado(type):
    def __init__(self, *args, **kwargs):
        # no uso iteritems porque estoy modificando el __dict__
        for attr, value in self.__dict__.items():
            if isinstance(value, Relation):
                value.set_reversed_property(self)
                setattr(self, attr, value.get_property())
        return super(MetaSerializado, self).__init__(*args, **kwargs)


class Serializado(object):
    """Clase con instancias listadas en un archivo json."""
    __metaclass__ = MetaSerializado
    COD_DATOS_ACTUAL = ''
    plural_name = 'Serializado' # redefinir al heredar
    datos_en_raiz = True # redefinir al heredar
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
    def _leer_archivo(cls):
        """Lee las instancias desde json y arma un dict con la clave
           especificada en el parametro clave.
           Admite filtrar por mesa cuando los datos son de un json que esta en
           el subdirectorio de datos que una mesa usa."""
        nombre_cache = '_cache_' + cls.plural_name

        if not cls.datos_en_raiz and Serializado.COD_DATOS_ACTUAL:
            nombre_cache += '_' + Serializado.COD_DATOS_ACTUAL

        if nombre_cache not in dir(cls):
            # se pluraliza el nombre de la clase para obtener el nombre del
            # archivo (ej: Persona -> Personas.json)
            if cls.datos_en_raiz or not Serializado.COD_DATOS_ACTUAL:
                filepath = os.path.join(PATH_DATOS,
                                         cls.plural_name)
            else:
                filepath = os.path.join(PATH_DATOS,
                                         Serializado.COD_DATOS_ACTUAL,
                                         cls.plural_name)

            try:
                elementos = cls._leer_elementos_json(filepath)
            except IOError:
                try:
                    elementos = cls._leer_elementos_yaml(filepath)
                except IOError:
                    pass
            setattr(cls, nombre_cache, elementos)
        return getattr(cls, nombre_cache)

    @classmethod
    def _leer_elementos_json(cls, filepath):
        datos = json.load(open(filepath + '.json', 'r'))
        elementos = dict((datos_elemento[cls.pk_field], datos_elemento)
                        for datos_elemento in datos)

        return elementos

    @classmethod
    def _leer_elementos_yaml(cls, filepath):
        datos = yaml.load(open(filepath + '.yaml', 'r'))
        elementos = {}
        for key, value in datos.items():
            elementos[value[cls.pk_field]] = value

        return elementos

    @classmethod
    def get(cls, pk=None, **kargs):
        """Obtiene el primer elemento que cumpla con las condiciones."""
        if pk:
            kargs[cls.pk_field] = pk
        if kargs.keys() == [cls.pk_field]:
            pk = kargs[cls.pk_field]
            todos = cls._leer_archivo()
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
    def _test_expression(cls, expresion, valor, datos_elemento):
        partes_expresion = expresion.split('__')
        if len(partes_expresion) == 1:
            campo = expresion
            operacion = '='
        else:
            campo, operacion = partes_expresion

        r = True
        try:
            if operacion in ('=', 'exact'):
                r = datos_elemento[campo] == valor
            elif operacion == 'iexact':
                r = str(datos_elemento[campo]).lower() == str(valor).lower()
            elif operacion == 'contains':
                r = valor in datos_elemento[campo]
            elif operacion == 'icontains':
                r = str(valor).lower() in str(datos_elemento[campo]).lower()
            elif operacion == 'in':
                r = datos_elemento[campo] in valor
            elif operacion == 'gt':
                r = datos_elemento[campo] > valor
            elif operacion == 'gte':
                r = datos_elemento[campo] >= valor
            elif operacion == 'lt':
                r = datos_elemento[campo] < valor
            elif operacion == 'lte':
                r = datos_elemento[campo] <= valor
            elif operacion == 'startswith':
                r = str(datos_elemento[campo]).startswith(str(valor))
            elif operacion == 'istartswith':
                r = str(datos_elemento[campo]).lower().startswith(str(valor).lower())
            elif operacion == 'endswith':
                r = str(datos_elemento[campo]).endswith(str(valor))
            elif operacion == 'iendswith':
                r = str(datos_elemento[campo]).lower().endswith(str(valor).lower())
            elif operacion == 'range':
                r = valor[0] <= datos_elemento[campo] <= valor[1]
            elif operacion == 'ne':
                r = datos_elemento[campo] != valor
            else:
                raise AttributeError("La operacion %s no existe" % operacion)
        except KeyError:
            raise AttributeError("No existe el campo %s" % campo)
        # TODO date operations
        # TODO regex operations
        return r

    @classmethod
    def _filter(cls, datos, filtros):
        filtrados = []
        for datos_elemento in datos:
            agregar = True
            for expresion, valor in filtros.items():
                if not cls._test_expression(expresion, valor, datos_elemento):
                    agregar = False
                    break
            if agregar:
                filtrados.append(datos_elemento)

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
        elementos = cls._leer_archivo().values()
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

