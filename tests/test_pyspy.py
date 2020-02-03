import sys
from queue import Queue

from pyspy import pyspy


class BaseTest:
    pass


class TestWiretapFunction(BaseTest):
    def test_logbook_contains_entry_after_calling_wiretapped_function(self):
        class FakeTestingModule:
            @staticmethod
            def my_fun():
                return

        sys.modules["FakeTestingModule"] = FakeTestingModule

        logbook = Queue()
        pyspy.wiretap_function(sys.modules["FakeTestingModule"], "my_fun", logbook)
        assert logbook.empty()
        FakeTestingModule.my_fun()
        assert not logbook.empty()
