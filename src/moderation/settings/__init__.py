import os
import environ

try:
    print('Importing ....')
    from .base import *
    if os.environ.get('ENVIRONMENT', 'Development') == 'Production':
        from .production import *
    else:
        from .local import *
except ImportError:
    import traceback
    print(traceback.format_exc())
    print('Unable load all configuration files')
