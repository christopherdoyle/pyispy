from queue import Queue

import pyspy
from . import BaseTest


class TestWiretapEntryPoint(BaseTest):
    def test_wiretap_basic_class__logs_correct_report(self):
        class MyClass:
            def f(self, other):
                return other

        my_object = MyClass()
        function_names = ["f"]
        logbook = Queue()
        pyspy.wiretap(my_object, function_names, logbook)

        my_object.f(5)

        report = logbook.get_nowait()

        assert report.function_name == "f"
