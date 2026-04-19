Plan:
1. Safely guard access to kwargs['litellm_params']['metadata'] in async_log_failure_event by using .get and defaulting to {}.
2. Add a small unit test ensuring async_log_failure_event doesn't raise when metadata is None.
3. Run pytest to validate the change.
