# __init__.py

# This makes the Chronicler class and the default 'log' instance
# available directly from the package.
# So you can do: from chronicler import Chronicler, log
# Instead of: from chronicler.chronicler import Chronicler, log

from .chronicler import Chronicler, log