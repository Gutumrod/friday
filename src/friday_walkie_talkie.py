"""Compatibility launcher for Friday walkie-talkie mode.

Importing this module returns friday.core so existing tests and monkeypatches keep the same
module-global behavior as the old single-file implementation.
"""
import sys

from friday import core as _core

if __name__ == "__main__":
    from friday.home_assistant_runtime import install_home_assistant_read_tools
    from friday.home_device_runtime import install_home_device_read_tools
    from friday.runtime_security import apply_runtime_security
    from friday.stt.runtime import install_stt_provider

    apply_runtime_security(_core)
    install_stt_provider(_core)
    ha_client = install_home_assistant_read_tools(_core)
    install_home_device_read_tools(_core, client=ha_client)
    try:
        _core.main()
    except KeyboardInterrupt:
        _core.shutdown_cleanup()
else:
    sys.modules[__name__] = _core
