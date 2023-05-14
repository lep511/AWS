# coding: utf-8
import pprint
import re  # noqa: F401

import six
from enum import Enum

class ResourceInfo(object):


    _types = {
        'account_id': 'object',
        'region': 'object',
        'resource_id': 'str',
        'resource_type': 'str',
        'service': 'str'
    }

    _attribute_map = {
        'account_id': 'account-id',
        'region': 'region',
        'resource_id': 'resource-id',
        'resource_type': 'resource-type',
        'service': 'service'
    }

    def __init__(self, account_id=None, region=None, resource_id=None, resource_type=None, service=None):  # noqa: E501
        self._account_id = None
        self._region = None
        self._resource_id = None
        self._resource_type = None
        self._service = None
        self.discriminator = None
        self.account_id = account_id
        self.region = region
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.service = service


    @property
    def account_id(self):

        return self._account_id

    @account_id.setter
    def account_id(self, account_id):


        self._account_id = account_id


    @property
    def region(self):

        return self._region

    @region.setter
    def region(self, region):


        self._region = region


    @property
    def resource_id(self):

        return self._resource_id

    @resource_id.setter
    def resource_id(self, resource_id):


        self._resource_id = resource_id


    @property
    def resource_type(self):

        return self._resource_type

    @resource_type.setter
    def resource_type(self, resource_type):


        self._resource_type = resource_type


    @property
    def service(self):

        return self._service

    @service.setter
    def service(self, service):


        self._service = service

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
        if issubclass(ResourceInfo, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, ResourceInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

