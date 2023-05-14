# coding: utf-8
import pprint
import re  # noqa: F401

import six
from enum import Enum
from schema.karte.chatevent.Alert import Alert  # noqa: F401,E501
from schema.karte.chatevent.Host import Host  # noqa: F401,E501
from schema.karte.chatevent.ResourceInfo import ResourceInfo  # noqa: F401,E501

class KARTEApiV2Hook(object):


    _types = {
        'alert': 'Alert',
        'host': 'Host',
        'resourceInfo': 'ResourceInfo',
        'event': 'str',
        'memo': 'str',
        'orgName': 'str',
        'user': 'object'
    }

    _attribute_map = {
        'alert': 'alert',
        'host': 'host',
        'resourceInfo': 'resourceInfo',
        'event': 'event',
        'memo': 'memo',
        'orgName': 'orgName',
        'user': 'user'
    }

    def __init__(self, alert=None, host=None, resourceInfo=None, event=None, memo=None, orgName=None, user=None):  # noqa: E501
        self._alert = None
        self._host = None
        self._resourceInfo = None
        self._event = None
        self._memo = None
        self._orgName = None
        self._user = None
        self.discriminator = None
        self.alert = alert
        self.host = host
        self.resourceInfo = resourceInfo
        self.event = event
        self.memo = memo
        self.orgName = orgName
        self.user = user


    @property
    def alert(self):

        return self._alert

    @alert.setter
    def alert(self, alert):


        self._alert = alert


    @property
    def host(self):

        return self._host

    @host.setter
    def host(self, host):


        self._host = host


    @property
    def resourceInfo(self):

        return self._resourceInfo

    @resourceInfo.setter
    def resourceInfo(self, resourceInfo):


        self._resourceInfo = resourceInfo


    @property
    def event(self):

        return self._event

    @event.setter
    def event(self, event):


        self._event = event


    @property
    def memo(self):

        return self._memo

    @memo.setter
    def memo(self, memo):


        self._memo = memo


    @property
    def orgName(self):

        return self._orgName

    @orgName.setter
    def orgName(self, orgName):


        self._orgName = orgName


    @property
    def user(self):

        return self._user

    @user.setter
    def user(self, user):


        self._user = user

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
        if issubclass(KARTEApiV2Hook, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, KARTEApiV2Hook):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

