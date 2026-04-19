import asyncio
import sys
import types
import importlib
from pathlib import Path

# Create lightweight stubs for the litellm package to avoid importing heavy dependencies
litellm_mod = types.ModuleType("litellm")
# Minimal DualCache placeholder
class DualCache:
    pass
litellm_mod.DualCache = DualCache

# _logging.verbose_proxy_logger stub
_logging_mod = types.ModuleType("litellm._logging")
class Logger:
    def exception(self, *a, **k):
        pass
    def debug(self, *a, **k):
        pass
    def warning(self, *a, **k):
        pass
verbose_logger = Logger()
_logging_mod.verbose_proxy_logger = verbose_logger

# integrations.custom_logger.CustomLogger stub
integrations_mod = types.ModuleType("litellm.integrations.custom_logger")
class CustomLogger:
    pass
integrations_mod.CustomLogger = CustomLogger

# proxy._types.UserAPIKeyAuth stub
proxy_types_mod = types.ModuleType("litellm.proxy._types")
class UserAPIKeyAuth:
    api_key = None
proxy_types_mod.UserAPIKeyAuth = UserAPIKeyAuth

# Insert into sys.modules so imports succeed
sys.modules["litellm"] = litellm_mod
sys.modules["litellm._logging"] = _logging_mod
sys.modules["litellm.integrations.custom_logger"] = integrations_mod
sys.modules["litellm.proxy._types"] = proxy_types_mod

# Import the module under test after stubbing
module_path = "litellm.proxy.hooks.parallel_request_limiter_v3"
parallel_mod = importlib.import_module(module_path)

# Now get the class
_PROXY_MaxParallelRequestsHandler_v3 = parallel_mod._PROXY_MaxParallelRequestsHandler_v3

class DummyDualCache:
    def __init__(self):
        self.calls = []

    async def async_increment_cache_pipeline(self, increment_list, litellm_parent_otel_span=None):
        self.calls.append((increment_list, litellm_parent_otel_span))


class DummyInternalUsageCache:
    def __init__(self):
        self.dual_cache = DummyDualCache()


def test_async_log_failure_event_handles_none_metadata():
    internal = DummyInternalUsageCache()
    handler = _PROXY_MaxParallelRequestsHandler_v3(internal)

    # Should not raise even if metadata is None
    kwargs = {"litellm_params": {"metadata": None}}

    asyncio.run(handler.async_log_failure_event(kwargs, response_obj=None, start_time=0, end_time=0))

    # No increments should have been scheduled
    assert internal.dual_cache.calls == []
