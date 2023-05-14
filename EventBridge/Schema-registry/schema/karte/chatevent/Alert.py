# coding: utf-8
import pprint
import re  # noqa: F401

import six
from enum import Enum

class Alert(object):


    _types = {
        'closedAt': 'object',
        'createdAt': 'int',
        'criticalThreshold': 'float',
        'duration': 'float',
        'id': 'str',
        'isOpen': 'bool',
        'metricLabel': 'str',
        'metricValue': 'float',
        'monitorName': 'str',
        'monitorOperator': 'str',
        'openedAt': 'float',
        'status': 'str',
        'trigger': 'str',
        'url': 'str',
        'warningThreshold': 'float'
    }

    _attribute_map = {
        'closedAt': 'closedAt',
        'createdAt': 'createdAt',
        'criticalThreshold': 'criticalThreshold',
        'duration': 'duration',
        'id': 'id',
        'isOpen': 'isOpen',
        'metricLabel': 'metricLabel',
        'metricValue': 'metricValue',
        'monitorName': 'monitorName',
        'monitorOperator': 'monitorOperator',
        'openedAt': 'openedAt',
        'status': 'status',
        'trigger': 'trigger',
        'url': 'url',
        'warningThreshold': 'warningThreshold'
    }

    def __init__(self, closedAt=None, createdAt=None, criticalThreshold=None, duration=None, id=None, isOpen=None, metricLabel=None, metricValue=None, monitorName=None, monitorOperator=None, openedAt=None, status=None, trigger=None, url=None, warningThreshold=None):  # noqa: E501
        self._closedAt = None
        self._createdAt = None
        self._criticalThreshold = None
        self._duration = None
        self._id = None
        self._isOpen = None
        self._metricLabel = None
        self._metricValue = None
        self._monitorName = None
        self._monitorOperator = None
        self._openedAt = None
        self._status = None
        self._trigger = None
        self._url = None
        self._warningThreshold = None
        self.discriminator = None
        self.closedAt = closedAt
        self.createdAt = createdAt
        self.criticalThreshold = criticalThreshold
        self.duration = duration
        self.id = id
        self.isOpen = isOpen
        self.metricLabel = metricLabel
        self.metricValue = metricValue
        self.monitorName = monitorName
        self.monitorOperator = monitorOperator
        self.openedAt = openedAt
        self.status = status
        self.trigger = trigger
        self.url = url
        self.warningThreshold = warningThreshold


    @property
    def closedAt(self):

        return self._closedAt

    @closedAt.setter
    def closedAt(self, closedAt):


        self._closedAt = closedAt


    @property
    def createdAt(self):

        return self._createdAt

    @createdAt.setter
    def createdAt(self, createdAt):


        self._createdAt = createdAt


    @property
    def criticalThreshold(self):

        return self._criticalThreshold

    @criticalThreshold.setter
    def criticalThreshold(self, criticalThreshold):


        self._criticalThreshold = criticalThreshold


    @property
    def duration(self):

        return self._duration

    @duration.setter
    def duration(self, duration):


        self._duration = duration


    @property
    def id(self):

        return self._id

    @id.setter
    def id(self, id):


        self._id = id


    @property
    def isOpen(self):

        return self._isOpen

    @isOpen.setter
    def isOpen(self, isOpen):


        self._isOpen = isOpen


    @property
    def metricLabel(self):

        return self._metricLabel

    @metricLabel.setter
    def metricLabel(self, metricLabel):


        self._metricLabel = metricLabel


    @property
    def metricValue(self):

        return self._metricValue

    @metricValue.setter
    def metricValue(self, metricValue):


        self._metricValue = metricValue


    @property
    def monitorName(self):

        return self._monitorName

    @monitorName.setter
    def monitorName(self, monitorName):


        self._monitorName = monitorName


    @property
    def monitorOperator(self):

        return self._monitorOperator

    @monitorOperator.setter
    def monitorOperator(self, monitorOperator):


        self._monitorOperator = monitorOperator


    @property
    def openedAt(self):

        return self._openedAt

    @openedAt.setter
    def openedAt(self, openedAt):


        self._openedAt = openedAt


    @property
    def status(self):

        return self._status

    @status.setter
    def status(self, status):


        self._status = status


    @property
    def trigger(self):

        return self._trigger

    @trigger.setter
    def trigger(self, trigger):


        self._trigger = trigger


    @property
    def url(self):

        return self._url

    @url.setter
    def url(self, url):


        self._url = url


    @property
    def warningThreshold(self):

        return self._warningThreshold

    @warningThreshold.setter
    def warningThreshold(self, warningThreshold):


        self._warningThreshold = warningThreshold

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
        if issubclass(Alert, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Alert):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

