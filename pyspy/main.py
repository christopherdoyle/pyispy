from dataclasses import dataclass
from queue import Queue
from typing import List, Sequence, Union
import types

from . import hooks


@dataclass
class Request:
    o: object
    function_names: Sequence[str]
    logbook: Union[Queue, List]


@dataclass
class Response:
    success: bool


def is_class(o: object) -> bool:
    return isinstance(o, type)


def is_module(o: object) -> bool:
    return isinstance(o, types.ModuleType)


def process_request(request: Request) -> Response:
    if is_module(request.o):
        wf = hooks.wiretap_function
    elif is_class(request.o):
        wf = hooks.wiretap_class_method
    else:
        wf = hooks.wiretap_instance_method

    # TODO
    if not isinstance(request.logbook, Queue):
        raise NotImplementedError("TODO")

    for function_name in request.function_names:
        wf(request.o, function_name, request.logbook)

    return Response(success=True)
