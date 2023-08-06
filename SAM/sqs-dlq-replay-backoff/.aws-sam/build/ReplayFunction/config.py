"""Environment configuration values used by lambda functions."""

import os

LOG_LEVEL = 'INFO'
SQS_MAIN_URL = os.getenv('SQS_MAIN_URL')
MAX_ATTEMPS = 1
BACKOFF_RATE = 1
MESSAGE_RETENTION_PERIOD = int(os.getenv('MESSAGE_RETENTION_PERIOD'))
