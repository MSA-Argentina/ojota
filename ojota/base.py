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
from collections import MutableSequence
from json import dumps
from threading import current_thread

import ojota.sources

from ojota.sources import JSONSource
from ojota.cache import Cache
import six


def current_data_code(data_code):
    """Sets the current data path."""
    Ojota._data_codes[current_thread()] = data_code


def get_current_data_code():
    data_code = Ojota._data_codes.get(current_thread(), "")
    return data_code


def set_data_source(data_path):
    ojota.sources._DATA_SOURCE = data_path


def preload(*args):
    for arg in args:
        if hasattr(arg, "preload"):
            arg.preload()


class Relation(object):
    """Adds a relation to another object."""
    def __init__(self, attr_fk, to_class, related_name=None):
        """Constructor for the relation class
        Arguments:
            attr_fk -- a String with the foreign key attribute name
            to_class -- the class that the relation makes reference to
            related_name -- the name of the attribute for the backward relation
                             Default None
        """
        self.attr_fk = attr_fk
        self.to_class = to_class
        self.related_name = related_name

    def get_property(self):
        """Returns the property in which the relation will be referenced."""
        def _inner(method_self):
            """Inner function to return the property for the relation."""
            fk = getattr(method_self, self.attr_fk)
            return self.to_class.one(fk)

        ret = property(_inner)
        return ret

    def set_reversed_property(self, from_class):
        """Returns the property in which the backwards relation will be
        referenced."""
        def _inner(method_self):
            """Inner function to return the property for the backwards
            relation."""
            pk = method_self.primary_key
            params = {self.attr_fk: pk}
            return from_class.many(**params)

        if self.related_name:
            prop = property(_inner)
            setattr(self.to_class, self.related_name, prop)
            self.to_class.backwards_relations.append(self.related_name)


class Callback(object):
    def __init__(self, field_name, function):
        self.field_name = field_name
        self.function = function

    def get_property(self):
        """Returns the property in which the relation will be referenced."""
        def _inner(method_self):
            """Inner function to return the property for the relation."""
            fk = getattr(method_self, self.field_name)
            return self.function(fk)

        ret = property(_inner)
        return ret


class WSRelation(Relation):
    """Adds a relation to another object."""
    def __init__(self, attr_fk, to_class, related_name=None, ws_call=None,
                 plural_name=None):
        """Constructor for the relation class
        Arguments:
            attr_fk -- a String with the foreign key attribute name
            to_class -- the class that the relation makes reference to
            related_name -- the name of the attribute for the backward relation
                             Default None
            ws_call -- the name of the webservice command
            plural_name -- basename of ws_call, only needed if plural_name
                           should be changed.
        """
        self.attr_fk = attr_fk
        self.to_class = to_class
        self.related_name = related_name
        self.ws_call = ws_call
        self.plural_name = plural_name

    def get_property(self):
        """Returns the property in which the relation will be referenced."""
        def _ws_inner(method_self):
            """Inner function to return the property for the relation."""
            _klass = self.to_class()
            self.__plural_name = _klass.__class__.plural_name
            self.__get_all_cmd = _klass.data_source.get_all_cmd
            if self.plural_name is not None:
                plural_name = self.plural_name
            else:
                plural_name = method_self.plural_name
            if not self.ws_call:
                _klass.data_source.get_all_cmd = self.ws_call
                ret = _klass.one(getattr(method_self, self.attr_fk))
            else:
                _klass.__class__.plural_name = "/".join(
                    (plural_name, getattr(method_self, self.attr_fk)))
                _klass.data_source.get_all_cmd = self.ws_call
                ret = _klass.many()
            _klass.__class__.plural_name = self.__plural_name
            _klass.data_source.get_all_cmd = self.__get_all_cmd
            return ret

        def _inner(method_self):
            """Inner function to return the property for the relation."""
            fk = getattr(method_self, self.attr_fk)
            return self.to_class.one(fk)

        if self.ws_call is not None:
            ret = property(_ws_inner)
        else:
            ret = property(_inner)
        return ret


class OjotaSet(MutableSequence):
    def __init__(self, ojota_class, data):
        super(OjotaSet, self).__init__()
        self._list = list(data)
        self.ojota_class = ojota_class

    def __len__(self):
        return len(self._list)

    def __getitem__(self, indexes):
        if isinstance(indexes, slice):
            list_ = self._list[indexes.start:indexes.stop:indexes.step]
            ret = OjotaSet(self.ojota_class, list_)
        else:
            ret = self.ojota_class(**self._list[indexes])

        return ret

    def __delitem__(self, ii):
        del self._list[ii]

    def __setitem__(self, ii, val):
        raise NotImplementedError

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "OjotaSet containing %s %s" % (len(self._list),
                                              self.ojota_class.plural_name)

    def insert(self, ii, val):
        self._list.insert(ii, val)

    def append(self, val):
        list_idx = len(self._list)
        self.insert(list_idx, val)

    def many(self, **kwargs):
        elems = self.ojota_class._filter(self._list, kwargs)
        return OjotaSet(self.ojota_class, elems)

    def one(self, **kwargs):
        return self.ojota_class.one(**kwargs)


class MetaOjota(type):
    """Metaclass for Ojota"""
    def __init__(self, *args, **kwargs):
        self.relations = {}
        self.backwards_relations = []
        for attr, value in list(self.__dict__.items()):
            if isinstance(value, Relation):
                value.set_reversed_property(self)
                setattr(self, attr, value.get_property())
                self.relations[value.attr_fk] = (value.to_class, attr, value)
            elif isinstance(value, Callback):
                setattr(self, attr, value.get_property())

        return super(MetaOjota, self).__init__(*args, **kwargs)


class Ojota(six.with_metaclass(MetaOjota, object)):
    """Base class to create instances of serialized data in the source files.
    """
    _data_codes = {}
    plural_name = None
    data_in_root = True
    pk_field = "pk"
    required_fields = None
    cache = Cache()
    data_source = JSONSource()
    default_order = None
    queryset_type = OjotaSet
    prefilter = None
    cache_name = None

    @property
    def primary_key(self):
        """Returns the primary key value."""
        return getattr(self, self.pk_field)

    @classmethod
    def get_plural_name(cls):
        if cls.plural_name is None:
            plural_name = "%ss" % cls.__name__
        else:
            plural_name = cls.plural_name

        return plural_name

    def __init__(self, _pk=None, **kwargs):
        """Constructor."""
        self.fields = []
        if self.required_fields is None:
            self.required_fields = []
        else:
            self.required_fields = list(self.required_fields)
        if self.pk_field not in self.required_fields:
            self.required_fields.append(self.pk_field)

        for key in self.required_fields:
            if key not in kwargs:
                raise AttributeError("The field '%s' is required" % key)
        for key, val in list(kwargs.items()):
            self.fields.append(key)
            setattr(self, key, val)

    @classmethod
    def get_current_data_code(cls):
        return get_current_data_code()

    @classmethod
    def get_cache_name(cls):
        if cls.cache_name is not None:
            cache_name = '_cache_' + cls.cache_name
        else:
            cache_name = '_cache_' + cls.get_plural_name()
        if not cls.data_in_root and get_current_data_code():
            cache_name += '_' + get_current_data_code()
        return cache_name

    @classmethod
    def _read_all_from_datasource(cls):
        """Reads the data from the datasource, makes a dictionary with the key
        specified in the key parameter. Allows to filter by subdirectories when
        the data is not on the root according to the data path."""
        cache_name = cls.get_cache_name()

        if cache_name not in cls.cache:
            elements = cls.data_source.fetch_elements(cls)
            if cls.prefilter is not None:
                elements_ = cls._filter(list(elements.values()), cls.prefilter)
                elements = {}
                for elem in elements_:
                    elements[elem[cls.pk_field]] = elem

            cls.cache.set(name=cache_name, elems=elements)
        else:
            elements = cls.cache.get(cache_name)
        return elements

    @classmethod
    def _read_item_from_datasource(cls, pk):
        """Reads the data form the datasource if support index search."""
        cache_name = cls.get_cache_name()

        element = cls.data_source.fetch_element(cls, pk)
        if cache_name in cls.cache:
            cache = cls.cache.get(cache_name)
            cache.update(element)
            cls.cache.set(name=cache_name, elems=cache)
        else:
            cache = element
        return cache[pk]

    @classmethod
    def _objetize(cls, data):
        """Return the data into an element."""
        return cls.queryset_type(cls, data)

    @classmethod
    def _test_expression(cls, expression, value, element_data):
        """Finds out if a value in a given field matches an expression.

        Arguments:
        expression -- a string with the comparison expression. If the
        expression is a field name it will be compared with equal. In case that
        the field has "__" and an operation appended the it is compared with
        the appended expression. The availiable expressions allowed are: "=",
        "exact", "iexact", "contains", "icontains", "in", "gt", "gte", "lt",
        "lte", "startswith", "istartswith", "endswith", "iendswith", "range"
        and "ne"
        """
        expression_parts = expression.split('__')
        if len(expression_parts) == 1:
            field = expression
            operation = '='
        else:
            field, operation = expression_parts

        r = True
        try:
            if operation in ('=', 'exact'):
                r = element_data[field] == value
            elif operation == 'iexact':
                r = str(element_data[field]).lower() == str(value).lower()
            elif operation == 'contains':
                r = value in element_data[field]
            elif operation == 'icontains':
                r = str(value).lower() in str(element_data[field]).lower()
            elif operation == 'in':
                r = element_data[field] in value
            elif operation == 'gt':
                r = element_data[field] > value
            elif operation == 'gte':
                r = element_data[field] >= value
            elif operation == 'lt':
                r = element_data[field] < value
            elif operation == 'lte':
                r = element_data[field] <= value
            elif operation == 'startswith':
                r = str(element_data[field]).startswith(str(value))
            elif operation == 'istartswith':
                r = str(element_data[field]).lower().startswith(
                    str(value).lower())
            elif operation == 'endswith':
                r = str(element_data[field]).endswith(str(value))
            elif operation == 'iendswith':
                r = str(element_data[field]).lower().endswith(
                    str(value).lower())
            elif operation == 'range':
                r = value[0] <= element_data[field] <= value[1]
            elif operation == 'ne':
                r = element_data[field] != value
            else:
                raise AttributeError(
                    "The operation %s does not exist" % operation)
        except KeyError:
            r = False
        # TODO date operations
        # TODO regex operations
        return r

    @classmethod
    def _filter(cls, data, filters):
        """Applies filter to data.

        Arguments:
            data -- an iterable containing the data
            filters -- a dictionary with the filters
        """
        filtrados = []
        for element_data in data:
            add = True
            for expression, value in list(filters.items()):
                if not cls._test_expression(expression, value, element_data):
                    add = False
                    break
            if add:
                filtrados.append(element_data)

        return filtrados

    @classmethod
    def _sort(cls, data_list, order_fields):
        """Sort a list by a given field or field froups.

        Arguments:
            data_list -- a list with the data
            order_fields -- a string with the order fields
        """
        order_fields = [x.strip() for x in order_fields.split(',')]

        for order_field in reversed(order_fields):
            if order_field.startswith('-'):
                reverse = True
                order_field = order_field[1:]
            else:
                reverse = False

            def _key_func(item):
                elem_data = item.get(order_field, "")
                if elem_data is None:
                    elem_data = ""
                return elem_data

            data_list = sorted(data_list, key=_key_func, reverse=reverse)
        return data_list

    @classmethod
    def all(cls):
        return cls.many()

    @classmethod
    def many(cls, **kwargs):
        """Returns all the elements that match the conditions."""
        elements = list(cls._read_all_from_datasource().values())
        order_fields = cls.default_order
        if 'sorted' in kwargs:
            order_fields = kwargs['sorted']
            del kwargs['sorted']

        if kwargs:
            elements = cls._filter(elements, kwargs)

        if order_fields:
            elements = cls._sort(elements, order_fields)

        list_ = cls._objetize(elements)
        return list_

    @classmethod
    def one(cls, pk=None, **kwargs):
        """Returns the first element that matches the conditions."""
        element = None
        if pk is not None:
            kwargs[cls.pk_field] = pk
        if list(kwargs.keys()) == [cls.pk_field]:
            pk = kwargs[cls.pk_field]
            if hasattr(cls.data_source, 'get_cmd'):
                elem = cls._read_item_from_datasource(pk)
                element = cls._objetize([elem])[0]
            else:
                all_elems = cls._read_all_from_datasource()
                if pk in all_elems:
                    element = cls(**all_elems[pk])
        else:
            result = cls.many(**kwargs)
            if result:
                if len(result) > 1:
                    raise IndexError("one is returning more than one element")
                else:
                    element = result[0]

        return element

    @classmethod
    def first(cls, *args, **kwargs):
        elements = cls.many(*args, **kwargs)
        if elements is not None and len(elements):
            return elements[0]

    def __eq__(self, other):
        """Compare the equality of two elements."""
        same_pk = self.primary_key == other.primary_key
        same_class = self.__class__ is other.__class__
        return same_pk and same_class

    def __repr__(self):
        """String representation of the elements."""
        return '%s<%s>' % (self.__class__.__name__, self.primary_key)

    def to_dict(self):
        return dict([(field, getattr(self, field)) for field in self.fields])

    def to_json(self):
        return dumps(self.to_dict())

    def update(self, **kwargs):
        """Updates the given values."""
        for arg, value in list(kwargs.items()):
            if arg != self.pk_field:
                if arg not in self.fields:
                    self.fields.append(arg)
                setattr(self, arg, value)
        self.dump_values()

    def dump_values(self, new_data=None, delete=False):
        """Saves the data into a file."""
        elements = self.__class__.many()
        json_data = []
        for element in elements:
            if element == self:
                if not delete:
                    data = self.to_dict()
                else:
                    data = None
            else:
                data = element.to_dict()
            if data is not None:
                json_data.append(data)

        if new_data is not None:
            json_data.append(new_data)

        self.data_source.save(self.__class__, json_data)
        cache_name = self.__class__.get_cache_name()
        self.cache.clear(cache_name)

    def delete(self):
        self.dump_values(delete=True)

    def save(self):
        """Save function for an object."""
        ojota_fields = ("fields", "required_fields", "relations",
                        "backwards_relations")
        data = self.__dict__

        if all([field in list(data.keys()) for field in self.required_fields]):
            new_data = {}
            for attr_name, attr_value in list(data.items()):
                if attr_name not in ojota_fields:
                    self.fields.append(attr_name)
                    new_data[attr_name] = attr_value
            if self.__class__.one(self.primary_key) is None:
                self.dump_values(new_data)
            else:
                self.update(**new_data)

    @classmethod
    def preload(cls):
        cls.many()


class OjotaHierarchy(Ojota):

    @property
    def segments(self):
        return self.primary_key.split(".")

    @property
    def root(self):
        return self.segments[0]

    @property
    def last_segment(self):
        return self.segments[-1]

    @property
    def parent(self):
        if len(self.segments) > 1:
            return self.one('.'.join(self.segments[:-1]))
        else:
            return None

    def is_parent(self, other):
       parent_id = '.'.join(self.segments[:-1])
       return parent_id == other.primary_key

    def is_ancestor(self, other):
        if self.primary_key.startswith(other.primary_key):
            return True
        else:
            return False

    def is_sibling(self, other):
        return self.segments[:-1] == other.segments[:-1]

    def siblings(self):
        args = {"%s__startswith" % self.pk_field: self.parent.primary_key}
        elements = self.many(**args)
        list_ = []
        for element in elements:
            if element.is_parent(self.parent):
                list_.append(element)

        return list_

    def children(self):
        args = {"%s__startswith" % self.pk_field: self.primary_key}
        elements = self.many(**args)
        list_ = []
        for element in elements:
            if element.is_parent(self):
                list_.append(element)

        return list_
