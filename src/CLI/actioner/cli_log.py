################################################################################
#                                                                              #
#  Copyright 2019 Broadcom. The term Broadcom refers to Broadcom Inc. and/or   #
#  its subsidiaries.                                                           #
#                                                                              #
#  Licensed under the Apache License, Version 2.0 (the "License");             #
#  you may not use this file except in compliance with the License.            #
#  You may obtain a copy of the License at                                     #
#                                                                              #
#     http://www.apache.org/licenses/LICENSE-2.0                               #
#                                                                              #
#  Unless required by applicable law or agreed to in writing, software         #
#  distributed under the License is distributed on an "AS IS" BASIS,           #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
#  See the License for the specific language governing permissions and         #
#  limitations under the License.                                              #
#                                                                              #
################################################################################

import syslog
import inspect

syslog.openlog('sonic-cli')
__enable_debug = False
__enable_print = False


def log_debug(msg):
    if not isinstance(msg, basestring):
        msg = str(msg)

    if __enable_debug:
        syslog.syslog(syslog.LOG_DEBUG, msg)

    if __enable_print:
        caller_frame = inspect.stack()[1][0]
        frame_info = inspect.getframeinfo(caller_frame)
        for line in msg.split('\n'):
            print('[{}:{}] DEBUG:: {}'.format(frame_info.function, frame_info.lineno, line))


def log_info(msg):
    if not isinstance(msg, basestring):
        msg = str(msg)

    syslog.syslog(syslog.LOG_INFO, msg)

    if __enable_print:
        caller_frame = inspect.stack()[1][0]
        frame_info = inspect.getframeinfo(caller_frame)
        for line in msg.split('\n'):
            print('[{}:{}] INFO:: {}'.format(frame_info.function, frame_info.lineno, line))


def log_error(msg):
    if not isinstance(msg, basestring):
        msg = str(msg)

    syslog.syslog(syslog.LOG_ERR, msg)

    if __enable_print:
        caller_frame = inspect.stack()[1][0]
        frame_info = inspect.getframeinfo(caller_frame)
        for line in msg.split('\n'):
            print('[{}:{}] ERROR:: {}'.format(frame_info.function, frame_info.lineno, line))

