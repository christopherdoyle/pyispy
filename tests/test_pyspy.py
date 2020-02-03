import sys
from queue import Queue
from typing import Callable, Sequence

import pytest

from pyspy import pyspy


@pytest.fixture
def fake_module_interface():
    class FakeTestingModule:
        @staticmethod
        def my_fun():
            pass

    def inject_functions(functions: Sequence[Callable] = None):
        for function in functions or ():
            setattr(FakeTestingModule, function.__name__, staticmethod(function))
        return FakeTestingModule

    name = FakeTestingModule.__name__
    assert name not in sys.modules
    sys.modules[name] = FakeTestingModule
    yield inject_functions
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
        self, fake_module_interface
    ):
        logbook = self.wiretap_and_run(fake_module_interface(), "my_fun")
        assert not logbook.empty()

    def test_logbook_contains_correct_type(self, fake_module_interface):
        logbook = self.wiretap_and_run(fake_module_interface(), "my_fun")
        entry = logbook.get_nowait()
        assert isinstance(entry, pyspy.SpyReport)

    def test_wiretapped_function__returns_correct_return_value(
        self, fake_module_interface
    ):
        def my_fun():
            return 5

        module = fake_module_interface([my_fun])
        logbook = Queue()
        pyspy.wiretap_function(module, "my_fun", logbook)
        result = module.my_fun()
        assert result == 5

    def test_report_contains_args(self, fake_module_interface):
        def my_fun(name, height, reach):
            return

        module = fake_module_interface([my_fun])
        logbook = Queue()
        pyspy.wiretap_function(module, "my_fun", logbook)
        args = ("Reyes", 78, 205)
        module.my_fun(*args)
        report = logbook.get_nowait()
        assert report.function_args == args

    def test_report_contains_kwargs(self, fake_module_interface):
        def my_fun(flag=False):
            return

        module = fake_module_interface([my_fun])
        logbook = Queue()
        pyspy.wiretap_function(module, "my_fun", logbook)
        kwargs = {"flag": True}
        module.my_fun(**kwargs)
        report = logbook.get_nowait()
        assert report.function_kwargs == kwargs
