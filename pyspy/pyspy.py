import datetime
from dataclasses import dataclass
from queue import Queue
from types import ModuleType
from typing import Callable, Dict, Tuple


@dataclass
class SpyReport:
    call_time: datetime.datetime
    function_name: str
    function_args: Tuple
    function_kwargs: Dict


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
    function_name = function_handle.__name__

    def report(timestamp, *a, **kw):
        spy_report = SpyReport(
            call_time=timestamp,
            function_name=function_name,
            function_args=a,
            function_kwargs=kw,
        )
        logbook.put(spy_report)

    def wrapped_function(*a, **kw):
        report(datetime.datetime.now(), *a, **kw)
        return function_handle(*a, **kw)

    return wrapped_function


def wiretap_function(module: ModuleType, function_name: str, logbook: Queue) -> None:
    function_handle = find_function_in_module(module, function_name)
    wrapped_function = get_wiretapped_function(function_handle, logbook)
    setattr(module, function_name, wrapped_function)
