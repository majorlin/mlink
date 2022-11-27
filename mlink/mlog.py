#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) 2022 YTMicro
# ******************************************************************************
# File: mlog.py
# Created Date: 2022/11/26 - 20:10
# Author: Major Lin
# ******************************************************************************

import logging
from logging.config import dictConfig


def log_init():
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': '~/.mlink.log',
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'formatter': 'standard'
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'filters': {},
        'loggers': {
            'mlog': {
                'handlers': ['default', 'console'],
                'level': 'DEBUG',
                'propagate': False
            },
        },
    }
    dictConfig(logging_config)


log_init()
logger = logging.getLogger('mlog')
