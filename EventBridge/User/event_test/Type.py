# coding: utf-8
import pprint
import re  # noqa: F401

import six
from enum import Enum

class Type(object):


    _types = {
        'color': 'str',
        'dateCreated': 'float',
        'description': 'str',
        'ghostedDate': 'float',
        'id': 'str',
        'name': 'str',
        'order': 'float',
        'version': 'float'
    }

    _attribute_map = {
        'color': 'color',
        'dateCreated': 'dateCreated',
        'description': 'description',
        'ghostedDate': 'ghostedDate',
        'id': 'id',
        'name': 'name',
        'order': 'order',
        'version': 'version'
    }

    def __init__(self, color=None, dateCreated=None, description=None, ghostedDate=None, id=None, name=None, order=None, version=None):  # noqa: E501
        self._color = None
        self._dateCreated = None
        self._description = None
        self._ghostedDate = None
        self._id = None
        self._name = None
        self._order = None
        self._version = None
        self.discriminator = None
        self.color = color
        self.dateCreated = dateCreated
        self.description = description
        self.ghostedDate = ghostedDate
        self.id = id
        self.name = name
        self.order = order
        self.version = version


    @property
    def color(self):

        return self._color

    @color.setter
    def color(self, color):


        self._color = color


    @property
    def dateCreated(self):

        return self._dateCreated

    @dateCreated.setter
    def dateCreated(self, dateCreated):


        self._dateCreated = dateCreated


    @property
    def description(self):

        return self._description

    @description.setter
    def description(self, description):


        self._description = description


    @property
    def ghostedDate(self):

        return self._ghostedDate

    @ghostedDate.setter
    def ghostedDate(self, ghostedDate):


        self._ghostedDate = ghostedDate


    @property
    def id(self):

        return self._id

    @id.setter
    def id(self, id):


        self._id = id


    @property
    def name(self):

        return self._name

    @name.setter
    def name(self, name):


        self._name = name


    @property
    def order(self):

        return self._order

    @order.setter
    def order(self, order):


        self._order = order


    @property
    def version(self):

        return self._version

    @version.setter
    def version(self, version):


        self._version = version

    def to_dict(self):
        result = {}

        for attr, _ in six.iteritems(self._types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(Type, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Type):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

