import datetime
import inspect
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


def is_static_method(cls, method_name):
    return isinstance(inspect.getattr_static(cls, method_name), staticmethod)


def is_class_method(cls, method_name):
    method_handle = getattr(cls, method_name)
    return inspect.ismethod(method_handle) and method_handle.__self__ is cls


def find_function_in_object(o: object, function_name: str) -> Callable:
    try:
        function_handle = getattr(o, function_name)
        if not hasattr(function_handle, "__call__"):
            raise LookupError(
                f"Resolved object {function_name} in object {o} is not a function."
            )
        else:
            return function_handle
    except AttributeError:
        raise LookupError(f"Cannot find function {function_name} in object {o}.")


def get_wiretapped_function(
    function_handle: Callable, logbook: Queue, classmethod: bool = False
) -> Callable:
    function_name = function_handle.__name__

    def report(timestamp, *a, **kw):
        spy_report = SpyReport(
            call_time=timestamp,
            function_name=function_name,
            function_args=a,
            function_kwargs=kw,
        )
        logbook.put(spy_report)

    if classmethod:

        def wrapped_function(cls, *a, **kw):
            report(datetime.datetime.now(), *a, **kw)
            return function_handle(*a, **kw)

    else:

        def wrapped_function(*a, **kw):
            report(datetime.datetime.now(), *a, **kw)
            return function_handle(*a, **kw)

    return wrapped_function


def wiretap_function(module: ModuleType, function_name: str, logbook: Queue) -> None:
    function_handle = find_function_in_object(module, function_name)
    wrapped_function = get_wiretapped_function(function_handle, logbook)
    setattr(module, function_name, wrapped_function)


def wiretap_class_method(class_obj, method_name: str, logbook: Queue) -> None:
    """Wiretaps the method in every instance of given class."""
    function_handle = find_function_in_object(class_obj, method_name)
    wrapped_function = get_wiretapped_function(
        function_handle, logbook, classmethod=is_class_method(class_obj, method_name)
    )

    if is_static_method(class_obj, method_name):
        wrapped_function = staticmethod(wrapped_function)
    elif is_class_method(class_obj, method_name):
        wrapped_function = classmethod(wrapped_function)

    setattr(class_obj, method_name, wrapped_function)


def wiretap_instance_method(o: object, method_name: str, logbook: Queue) -> None:
    function_handle = find_function_in_object(o, method_name)
    wrapped_function = get_wiretapped_function(function_handle, logbook)
    setattr(o, method_name, wrapped_function)
