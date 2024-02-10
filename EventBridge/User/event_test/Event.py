# coding: utf-8
import pprint
import re  # noqa: F401

import six
from enum import Enum
from event_test.Type import Type  # noqa: F401,E501

class Event(object):


    _types = {
        'type': 'Type',
        'dateCreated': 'int',
        'description': 'str',
        'endDate': 'float',
        'id': 'str',
        'isOneDay': 'bool',
        'name': 'str',
        'releases': 'list[object]',
        'startDate': 'float',
        'version': 'float'
    }

    _attribute_map = {
        'type': 'type',
        'dateCreated': 'dateCreated',
        'description': 'description',
        'endDate': 'endDate',
        'id': 'id',
        'isOneDay': 'isOneDay',
        'name': 'name',
        'releases': 'releases',
        'startDate': 'startDate',
        'version': 'version'
    }

    def __init__(self, type=None, dateCreated=None, description=None, endDate=None, id=None, isOneDay=None, name=None, releases=None, startDate=None, version=None):  # noqa: E501
        self._type = None
        self._dateCreated = None
        self._description = None
        self._endDate = None
        self._id = None
        self._isOneDay = None
        self._name = None
        self._releases = None
        self._startDate = None
        self._version = None
        self.discriminator = None
        self.type = type
        self.dateCreated = dateCreated
        self.description = description
        self.endDate = endDate
        self.id = id
        self.isOneDay = isOneDay
        self.name = name
        self.releases = releases
        self.startDate = startDate
        self.version = version


    @property
    def type(self):

        return self._type

    @type.setter
    def type(self, type):


        self._type = type


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
    def endDate(self):

        return self._endDate

    @endDate.setter
    def endDate(self, endDate):


        self._endDate = endDate


    @property
    def id(self):

        return self._id

    @id.setter
    def id(self, id):


        self._id = id


    @property
    def isOneDay(self):

        return self._isOneDay

    @isOneDay.setter
    def isOneDay(self, isOneDay):


        self._isOneDay = isOneDay


    @property
    def name(self):

        return self._name

    @name.setter
    def name(self, name):


        self._name = name


    @property
    def releases(self):

        return self._releases

    @releases.setter
    def releases(self, releases):


        self._releases = releases


    @property
    def startDate(self):

        return self._startDate

    @startDate.setter
    def startDate(self, startDate):


        self._startDate = startDate


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
        if issubclass(Event, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Event):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

