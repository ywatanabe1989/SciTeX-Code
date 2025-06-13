import functools
import warnings


def deprecated(reason=None):
    """
    A decorator to mark functions as deprecated. It will result in a warning being emitted
    when the function is used.

    Args:
        reason (str): A human-readable string explaining why this function was deprecated.
    """

    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated: {reason}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return new_func

    return decorator
