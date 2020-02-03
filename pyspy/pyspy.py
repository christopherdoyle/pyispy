from typing import Callable, Dict
from types import ModuleType

from queue import Queue


def find_function_in_module(module: ModuleType, function_name: str) -> Callable:
    try:
        function_handle = getattr(module, function_name)
        if not hasattr(function_handle, "__call__"):
            raise LookupError(
                f"Resolved object {function_name} in module {module} is not a function."
            )
        else:
            return function_handle
    except AttributeError:
        raise LookupError(f"Cannot find function {function_name} in module {module}")


def get_wiretapped_function(function_handle: Callable, logbook: Queue) -> Callable:
    def wrapped_function():
        logbook.put(f"{function_handle.__name__}")
        return function_handle()

    return wrapped_function


def wiretap_function(module: ModuleType, function_name: str, logbook: Queue) -> None:
    function_handle = find_function_in_module(module, function_name)
    wrapped_function = get_wiretapped_function(function_handle, logbook)
    setattr(module, function_name, wrapped_function)
