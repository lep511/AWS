# coding: utf-8
import pprint
import re  # noqa: F401

import six
from enum import Enum

class Host(object):


    _types = {
        'id': 'str',
        'isRetired': 'bool',
        'memo': 'str',
        'name': 'str',
        'roles': 'list[object]',
        'status': 'str',
        'url': 'str'
    }

    _attribute_map = {
        'id': 'id',
        'isRetired': 'isRetired',
        'memo': 'memo',
        'name': 'name',
        'roles': 'roles',
        'status': 'status',
        'url': 'url'
    }

    def __init__(self, id=None, isRetired=None, memo=None, name=None, roles=None, status=None, url=None):  # noqa: E501
        self._id = None
        self._isRetired = None
        self._memo = None
        self._name = None
        self._roles = None
        self._status = None
        self._url = None
        self.discriminator = None
        self.id = id
        self.isRetired = isRetired
        self.memo = memo
        self.name = name
        self.roles = roles
        self.status = status
        self.url = url


    @property
    def id(self):

        return self._id

    @id.setter
    def id(self, id):


        self._id = id


    @property
    def isRetired(self):

        return self._isRetired

    @isRetired.setter
    def isRetired(self, isRetired):


        self._isRetired = isRetired


    @property
    def memo(self):

        return self._memo

    @memo.setter
    def memo(self, memo):


        self._memo = memo


    @property
    def name(self):

        return self._name

    @name.setter
    def name(self, name):


        self._name = name


    @property
    def roles(self):

        return self._roles

    @roles.setter
    def roles(self, roles):


        self._roles = roles


    @property
    def status(self):

        return self._status

    @status.setter
    def status(self, status):


        self._status = status


    @property
    def url(self):

        return self._url

    @url.setter
    def url(self, url):


        self._url = url

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
        if issubclass(Host, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Host):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

