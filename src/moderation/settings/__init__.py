try:
    from .base import *
except ImportError:
    import traceback

    print(traceback.format_exc())
    print("Unable load all configuration files")
