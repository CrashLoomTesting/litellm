import sys
import types
import asyncio

# Stub out parts of the litellm package that are heavy or optional so tests can import the target module
litellm_mod = types.ModuleType("litellm")
litellm_mod.DualCache = object

_logging = types.ModuleType("litellm._logging")
class _VerboseLogger:
    def exception(self, *a, **k):
        return None
    def debug(self, *a, **k):
        return None
    def warning(self, *a, **k):
        return None
_logging.verbose_proxy_logger = _VerboseLogger()

integrations = types.ModuleType("litellm.integrations")
custom_logger_mod = types.ModuleType("litellm.integrations.custom_logger")
class CustomLogger:
    pass
custom_logger_mod.CustomLogger = CustomLogger
integrations.custom_logger = custom_logger_mod

proxy_mod = types.ModuleType("litellm.proxy")
proxy_types_mod = types.ModuleType("litellm.proxy._types")
class UserAPIKeyAuth:
    def __init__(self):
        self.api_key = None
        self.parent_otel_span = None
proxy_types_mod.UserAPIKeyAuth = UserAPIKeyAuth
proxy_mod._types = proxy_types_mod

litellm_core_utils = types.ModuleType("litellm.litellm_core_utils")
core_helpers_mod = types.ModuleType("litellm.litellm_core_utils.core_helpers")
core_helpers_mod._get_parent_otel_span_from_kwargs = lambda kwargs: None
litellm_core_utils.core_helpers = core_helpers_mod

types_mod = types.ModuleType("litellm.types")
# caching submodule
caching_mod = types.ModuleType("litellm.types.caching")
class RedisPipelineIncrementOperation(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
caching_mod.RedisPipelineIncrementOperation = RedisPipelineIncrementOperation
types_mod.caching = caching_mod

# Put into sys.modules
sys.modules["litellm"] = litellm_mod
sys.modules["litellm._logging"] = _logging
sys.modules["litellm.integrations.custom_logger"] = custom_logger_mod
sys.modules["litellm.proxy._types"] = proxy_types_mod
sys.modules["litellm.litellm_core_utils.core_helpers"] = core_helpers_mod
sys.modules["litellm.types.caching"] = caching_mod
sys.modules["litellm.integrations"] = integrations
sys.modules["litellm.proxy"] = proxy_mod
sys.modules["litellm.litellm_core_utils"] = litellm_core_utils
sys.modules["litellm.types"] = types_mod

# Now import the module under test
import importlib.util
import os

# Load the target module directly from file to avoid package import complications
module_path = os.path.join(os.path.dirname(__file__), "..", "litellm", "proxy", "hooks", "parallel_request_limiter_v3.py")
module_path = os.path.normpath(module_path)
spec = importlib.util.spec_from_file_location("litellm.proxy.hooks.parallel_request_limiter_v3", module_path)
parallel = importlib.util.module_from_spec(spec)
# Create minimal stubs for litellm package and submodules used by the target module
import sys, types
litellm_mod = types.ModuleType("litellm")
litellm_mod.DualCache = object
# logging
_logging = types.ModuleType("litellm._logging")
class _VerboseLogger:
    def exception(self, *a, **k):
        return None
    def debug(self, *a, **k):
        return None
    def warning(self, *a, **k):
        return None
_logging.verbose_proxy_logger = _VerboseLogger()
# integrations.custom_logger
integrations_pkg = types.ModuleType("litellm.integrations")
custom_logger_mod = types.ModuleType("litellm.integrations.custom_logger")
class CustomLogger:
    pass
custom_logger_mod.CustomLogger = CustomLogger
# proxy._types
proxy_types_mod = types.ModuleType("litellm.proxy._types")
class UserAPIKeyAuth:
    def __init__(self):
        self.api_key = None
        self.parent_otel_span = None
proxy_types_mod.UserAPIKeyAuth = UserAPIKeyAuth
# litellm.litellm_core_utils.core_helpers
litellm_core_utils = types.ModuleType("litellm.litellm_core_utils")
core_helpers_mod = types.ModuleType("litellm.litellm_core_utils.core_helpers")
core_helpers_mod._get_parent_otel_span_from_kwargs = lambda kwargs: None
# types.caching
types_mod = types.ModuleType("litellm.types")
caching_mod = types.ModuleType("litellm.types.caching")
class RedisPipelineIncrementOperation(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
caching_mod.RedisPipelineIncrementOperation = RedisPipelineIncrementOperation

# register in sys.modules
sys.modules["litellm"] = litellm_mod
sys.modules["litellm._logging"] = _logging
sys.modules["litellm.integrations"] = integrations_pkg
sys.modules["litellm.integrations.custom_logger"] = custom_logger_mod
sys.modules["litellm.proxy._types"] = proxy_types_mod
sys.modules["litellm.litellm_core_utils"] = litellm_core_utils
sys.modules["litellm.litellm_core_utils.core_helpers"] = core_helpers_mod
sys.modules["litellm.types"] = types_mod
sys.modules["litellm.types.caching"] = caching_mod

# execute module
spec.loader.exec_module(parallel)


class DummyDualCache:
    async def async_increment_cache_pipeline(self, increment_list, litellm_parent_otel_span=None):
        # no-op for test
        return None


class DummyInternalUsageCache:
    def __init__(self):
        self.dual_cache = DummyDualCache()


def test_async_log_failure_event_handles_none_metadata():
    handler = parallel._PROXY_MaxParallelRequestsHandler_v3(internal_usage_cache=DummyInternalUsageCache())

    async def run():
        # Should not raise even if metadata is None
        await handler.async_log_failure_event(kwargs={"litellm_params": {"metadata": None}}, response_obj=None, start_time=0, end_time=0)

    asyncio.run(run())
