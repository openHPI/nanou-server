from .common import *  # noqa


SECRET_KEY = 'uxv*l4)co)wm1*7o@if@r3p@+-=u6&)@78d#-4+93&03vg*!ze'

DEBUG = True


# Create a local_settings.py to override settings with sensible values
# that shall not be checked in to the repository

try:
    from .local_settings import *  # noqa
except ImportError:
    pass
