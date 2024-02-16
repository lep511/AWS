# coding: utf-8
import pprint
import re  # noqa: F401

import six
from enum import Enum

class OrderNotification(object):


    _types = {
        'category': 'str',
        'location': 'str',
        'value': 'float'
    }

    _attribute_map = {
        'category': 'category',
        'location': 'location',
        'value': 'value'
    }

    def __init__(self, category=None, location=None, value=None):  # noqa: E501
        self._category = None
        self._location = None
        self._value = None
        self.discriminator = None
        self.category = category
        self.location = location
        self.value = value


    @property
    def category(self):

        return self._category

    @category.setter
    def category(self, category):


        self._category = category


    @property
    def location(self):

        return self._location

    @location.setter
    def location(self, location):


        self._location = location


    @property
    def value(self):

        return self._value

    @value.setter
    def value(self, value):


        self._value = value

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
        if issubclass(OrderNotification, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, OrderNotification):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

