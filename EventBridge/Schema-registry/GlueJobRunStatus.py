# coding: utf-8
import pprint
import re  # noqa: F401

import six
from enum import Enum
from schema.aws.glue.gluejobrunstatus.NotificationCondition import NotificationCondition  # noqa: F401,E501

class GlueJobRunStatus(object):


    _types = {
        'notificationCondition': 'NotificationCondition',
        'jobName': 'str',
        'severity': 'str',
        'state': 'str',
        'jobRunId': 'str',
        'message': 'str',
        'startedOn': 'datetime'
    }

    _attribute_map = {
        'notificationCondition': 'notificationCondition',
        'jobName': 'jobName',
        'severity': 'severity',
        'state': 'state',
        'jobRunId': 'jobRunId',
        'message': 'message',
        'startedOn': 'startedOn'
    }

    def __init__(self, notificationCondition=None, jobName=None, severity=None, state=None, jobRunId=None, message=None, startedOn=None):  # noqa: E501
        self._notificationCondition = None
        self._jobName = None
        self._severity = None
        self._state = None
        self._jobRunId = None
        self._message = None
        self._startedOn = None
        self.discriminator = None
        self.notificationCondition = notificationCondition
        self.jobName = jobName
        self.severity = severity
        self.state = state
        self.jobRunId = jobRunId
        self.message = message
        self.startedOn = startedOn


    @property
    def notificationCondition(self):

        return self._notificationCondition

    @notificationCondition.setter
    def notificationCondition(self, notificationCondition):


        self._notificationCondition = notificationCondition


    @property
    def jobName(self):

        return self._jobName

    @jobName.setter
    def jobName(self, jobName):


        self._jobName = jobName


    @property
    def severity(self):

        return self._severity

    @severity.setter
    def severity(self, severity):


        self._severity = severity


    @property
    def state(self):

        return self._state

    @state.setter
    def state(self, state):


        self._state = state


    @property
    def jobRunId(self):

        return self._jobRunId

    @jobRunId.setter
    def jobRunId(self, jobRunId):


        self._jobRunId = jobRunId


    @property
    def message(self):

        return self._message

    @message.setter
    def message(self, message):


        self._message = message


    @property
    def startedOn(self):

        return self._startedOn

    @startedOn.setter
    def startedOn(self, startedOn):


        self._startedOn = startedOn

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
        if issubclass(GlueJobRunStatus, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, GlueJobRunStatus):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

