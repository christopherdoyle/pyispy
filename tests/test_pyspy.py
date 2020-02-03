import sys
from queue import Queue

import pytest

from pyspy import pyspy


@pytest.fixture
def fake_module():
    class FakeTestingModule:
        @staticmethod
        def my_fun():
            pass

    name = FakeTestingModule.__name__
    assert name not in sys.modules
    sys.modules[name] = FakeTestingModule
    yield FakeTestingModule
    del sys.modules[name]


class BaseTest:
    pass


class TestWiretapFunction(BaseTest):
    def test_logbook_contains_entry_after_calling_wiretapped_function(
        self, fake_module
    ):
        logbook = Queue()
        pyspy.wiretap_function(fake_module, "my_fun", logbook)
        assert logbook.empty()
        fake_module.my_fun()
        assert not logbook.empty()
