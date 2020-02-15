"""Top-level package for PyISpy."""
from queue import Queue
from typing import List, Sequence, Union

from . import main

__author__ = """Christopher Doyle"""
__version__ = "0.1.0"


def wiretap(
    o: object, function_names: Union[str, Sequence[str]], logbook: Union[Queue, List],
) -> bool:
    if isinstance(function_names, str):
        function_names = [function_names]
    else:
        function_names = list(function_names)

    request = main.Request(o=o, function_names=function_names, logbook=logbook)
    response = main.process_request(request)
    return response.success


__all__ = ["wiretap"]
