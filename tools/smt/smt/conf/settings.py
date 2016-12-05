# -*- coding: utf-8 -*-

import os

AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None

PROJECT_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')


def rel(*x):
    return os.path.abspath(os.path.join(PROJECT_ROOT, *x))


SETUP_DIR = rel('../../../setup')
KEY_DIR = rel('../../../keys')


# Staging
STA_PUPPET_GIT_BRANCH = 'sta'
STA_PUPPET_GIT_REPO = 'git@github.com:CareerVillage/slack-moderation.git'
STA_PUPPET_BASE_DOMAIN = 'staging.slack-moderation'
STA_PUPPET_AWS_ACCESS_KEY_ID = None
STA_PUPPET_AWS_SECRET_ACCESS_KEY = None
STA_PUPPET_SENTRY_DSN = None
STA_PUPPET_NEWRELIC_LICENSE = None
STA_PUPPET_SECRET_KEY = None

# Production
PRO_PUPPET_GIT_BRANCH = 'master'
PRO_PUPPET_GIT_REPO = 'git@github.com:CareerVillage/slack-moderation.git'
PRO_PUPPET_BASE_DOMAIN = 'slack-moderation'
PRO_PUPPET_AWS_ACCESS_KEY_ID = None
PRO_PUPPET_AWS_SECRET_ACCESS_KEY = None
PRO_PUPPET_SENTRY_DSN = None
PRO_PUPPET_NEWRELIC_LICENSE = None
PRO_PUPPET_SECRET_KEY = None

try:
    from secrets import *
except ImportError:
    print 'Error importing secrets module on smt.conf.settings'

try:
    from user import *
except ImportError:
    print 'Error importing user module on smt.conf.settings'
