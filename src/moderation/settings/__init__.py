try:
    print 'Importing ....'
    from base import *  # noqa
    from local import *  # noqa

except ImportError:
    import traceback
    print traceback.format_exc()
    print 'Unable to find moderation/settings/local.py'

try:
    from post_env_commons import *  # noqa

except ImportError:
    pass
