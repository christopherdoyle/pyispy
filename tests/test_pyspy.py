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
    @staticmethod
    def wiretap_and_run(module, function_name) -> Queue:
        logbook = Queue()
        pyspy.wiretap_function(module, function_name, logbook)
        module.my_fun()
        return logbook

    def test_logbook_contains_entry_after_calling_wiretapped_function(
        self, fake_module
    ):
        logbook = self.wiretap_and_run(fake_module, "my_fun")
        assert not logbook.empty()

    def test_logbook_contains_correct_type(self, fake_module):
        logbook = self.wiretap_and_run(fake_module, "my_fun")
        entry = logbook.get_nowait()
        assert isinstance(entry, pyspy.SpyReport)

    def test_wiretapped_function__returns_correct_return_value(self, fake_module):
        def my_fun():
            return 5

        setattr(fake_module, "my_fun", staticmethod(my_fun))

        logbook = Queue()
        pyspy.wiretap_function(fake_module, "my_fun", logbook)
        result = fake_module.my_fun()
        assert result == 5
