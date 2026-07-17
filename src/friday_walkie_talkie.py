"""Compatibility launcher for Friday walkie-talkie mode.

Importing this module returns friday.core so existing tests and monkeypatches keep the same
module-global behavior as the old single-file implementation.
"""
import sys

from friday import core as _core

if __name__ == "__main__":
    try:
        _core.main()
    except KeyboardInterrupt:
        _core.shutdown_cleanup()
else:
    sys.modules[__name__] = _core
