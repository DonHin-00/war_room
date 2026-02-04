import sys
import os
import time
import json
import traceback
import logging
import inspect
from functools import wraps

class TraceLogger:
    """
    Advanced error tracer that captures stack traces and local variables.
    Writes structured logs to a JSONL file.
    """
    def __init__(self, filepath="errors.jsonl"):
        self.filepath = filepath
        self.setup_logging()

    def setup_logging(self):
        # Ensure directory exists
        log_dir = os.path.dirname(self.filepath)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError:
                pass

    def log_exception(self, exc, context_msg=""):
        """Logs an exception with full context."""
        timestamp = time.time()
        exc_type, exc_value, exc_traceback = sys.exc_info()

        # Get stack frames
        frames = []
        tb = exc_traceback
        while tb:
            frame = tb.tb_frame
            frames.append({
                "filename": frame.f_code.co_filename,
                "function": frame.f_code.co_name,
                "lineno": tb.tb_lineno,
                "locals": {k: str(v) for k, v in frame.f_locals.items() if not k.startswith("__")}
            })
            tb = tb.tb_next

        entry = {
            "timestamp": timestamp,
            "type": str(exc_type.__name__),
            "message": str(exc_value),
            "context": context_msg,
            "traceback": traceback.format_exc(),
            "frames": frames
        }

        try:
            with open(self.filepath, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            # Fallback to standard logging if file write fails
            logging.error(f"Failed to write to error log: {e}")
            logging.error(traceback.format_exc())

# Global instance
_tracer = TraceLogger()

def trace_errors(func):
    """Decorator to automatically log exceptions in the wrapped function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            _tracer.log_exception(e, context_msg=f"Error in {func.__name__}")
            raise # Re-raise to ensure the app handles/crashes as intended, or swallow?
            # For this simulation, we often swallow in main loops, but let's re-raise
            # so the outer try/except blocks (if any) can decide, OR
            # if it's a top-level agent loop, we might want to swallow to keep it alive.
            # Ideally, the agent loop handles it.
    return wrapper
