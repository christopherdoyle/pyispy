import sys
import datetime
from queue import Queue
from typing import Callable, Sequence

import pytest

from pyispy import hooks
from . import BaseTest


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


class TestSpyReport(BaseTest):
    @property
    def spy_report1(self):
        return hooks.SpyReport(
            call_time=datetime.datetime(2020, 2, 20),
            function_name="Roger",
            function_args=(1, 2),
            function_kwargs={"a": [1]},
        )

    @property
    def spy_report2(self):
        return hooks.SpyReport(
            call_time=datetime.datetime(2020, 2, 20),
            function_name="Roger",
            function_args=(1, 2),
            function_kwargs={"a": [1]},
        )

    def test_eq__given_identical_report__is_equal(self):
        assert self.spy_report1 == self.spy_report2

    def test_eq__given_different_call_time__is_not_equal(self):
        spy_report2 = self.spy_report2
        spy_report2.call_time = spy_report2.call_time + datetime.timedelta(days=1)
        assert self.spy_report1 != spy_report2

    def test_eq__given_different_function_name__is_not_equal(self):
        spy_report2 = self.spy_report2
        spy_report2.function_name += " Daltrey"
        assert self.spy_report1 != spy_report2

    def test_eq__given_different_function_args__is_not_equal(self):
        spy_report2 = self.spy_report2
        spy_report2.function_args += (3, 4)
        assert self.spy_report1 != spy_report2

    def test_eq__given_different_function_kwargs__is_not_equal(self):
        spy_report2 = self.spy_report2
        spy_report2.function_kwargs["b"] = 10000
        assert self.spy_report1 != spy_report2

    def test_eq__to_function_name(self):
        assert self.spy_report1 == "Roger"
        assert self.spy_report1 != "Pete"

    def test_eq__given_dictionary_with_same_values__not_equal(self):
        assert self.spy_report1 != self.spy_report1.__dict__


class TestFakeModuleInterface(BaseTest):
    def test_inject_functions__no_functions__does_not_crash(
        self, fake_module_interface
    ):
        fake_module_interface()

    def test_inject_functions__with_function__is_attr(self, fake_module_interface):
        def this_is_a_function():
            pass

        module = fake_module_interface([this_is_a_function])
        assert hasattr(module, "this_is_a_function")

    def test_inject_functions__with_multiple_functions__are_attrs(
        self, fake_module_interface
    ):
        def function_one():
            pass

        def function_two():
            pass

        module = fake_module_interface([function_one, function_two])
        assert hasattr(module, "function_one")
        assert hasattr(module, "function_two")

    def test_injected_functions__take_args_and_kwargs_and_return(
        self, fake_module_interface
    ):
        def function(name, *a, flag=False, **kw):
            return [a, flag]

        module = fake_module_interface([function])

        result = module.function("Chris", 5, 1729, flag=True, height=4)

        assert result == [(5, 1729), True]


class TestWiretapFunction(BaseTest):
    @staticmethod
    def wiretap_and_run(module, function_name) -> Queue:
        logbook = Queue()
        hooks.wiretap_function(module, function_name, logbook)
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
        assert isinstance(entry, hooks.SpyReport)

    def test_wiretapped_function__returns_correct_return_value(
        self, fake_module_interface
    ):
        def my_fun():
            return 5

        module = fake_module_interface([my_fun])
        logbook = Queue()
        hooks.wiretap_function(module, "my_fun", logbook)
        result = module.my_fun()
        assert result == 5

    def test_report_contains_args(self, fake_module_interface):
        def my_fun(name, height, reach):
            return

        module = fake_module_interface([my_fun])
        logbook = Queue()
        hooks.wiretap_function(module, "my_fun", logbook)
        args = ("Reyes", 78, 205)
        module.my_fun(*args)
        report = logbook.get_nowait()
        assert report.function_args == args

    def test_report_contains_kwargs(self, fake_module_interface):
        def my_fun(flag=False):
            return

        module = fake_module_interface([my_fun])
        logbook = Queue()
        hooks.wiretap_function(module, "my_fun", logbook)
        kwargs = {"flag": True}
        module.my_fun(**kwargs)
        report = logbook.get_nowait()
        assert report.function_kwargs == kwargs


class TestWiretapClassMethod(BaseTest):
    """In particular we are testing the behavior with self and cls arguments to
    functions.

    TODO Test on inherited classes
    """

    @property
    def testing_class(self):
        class TestingClass:
            def normal_method(self, *a, **kw):
                return a, kw

            @staticmethod
            def static_method(*a, **kw):
                return a, kw

            @classmethod
            def class_method(cls, *a, **kw):
                return a, kw

        return TestingClass

    @pytest.mark.parametrize(
        "method_name", ("normal_method", "static_method", "class_method"),
    )
    def test_call_on_instance__no_wiretap(self, method_name):
        """Sanity check for behavior of static/class methods before testing
        said behavior with wiretapping.
        """
        class_obj = self.testing_class
        class_instance = class_obj()
        method_handle = getattr(class_instance, method_name)
        result = method_handle(1, 2, three=4)
        assert result == ((1, 2), {"three": 4})

    @pytest.mark.parametrize(
        "method_name", ("normal_method", "static_method", "class_method"),
    )
    def test_call_on_instance__instantiate_after_wiretap(self, method_name):
        class_obj = self.testing_class
        logbook = Queue()
        hooks.wiretap_class_method(class_obj, method_name, logbook)
        class_instance = class_obj()
        method_handle = getattr(class_instance, method_name)
        result = method_handle(1, 2, three=4)
        assert result == ((1, 2), {"three": 4})
        assert logbook.get_nowait().function_name == method_name

    @pytest.mark.parametrize(
        "method_name", ("normal_method", "static_method", "class_method"),
    )
    def test_call_on_instance__instantiate_before_wiretap(self, method_name):
        class_obj = self.testing_class
        logbook = Queue()
        class_instance = class_obj()
        hooks.wiretap_class_method(class_obj, method_name, logbook)
        method_handle = getattr(class_instance, method_name)
        result = method_handle(1, 2, three=4)
        assert result == ((1, 2), {"three": 4})
        assert logbook.get_nowait().function_name == method_name

    def test_call_on_class__normal_method__raises(self):
        """We are testing that the patched method still required a self"""
        class_obj = self.testing_class
        logbook = Queue()
        hooks.wiretap_class_method(class_obj, "normal_method", logbook)

        with pytest.raises(Exception):
            class_obj.normal_method()


class TestWiretapInstanceMethod(BaseTest):
    @property
    def testing_class(self):
        class TestingClass:
            def normal_method(self, *a, **kw):
                return a, kw

            @staticmethod
            def static_method(*a, **kw):
                return a, kw

            @classmethod
            def class_method(cls, *a, **kw):
                return a, kw

        return TestingClass

    @pytest.mark.parametrize(
        "method_name", ("normal_method", "static_method", "class_method"),
    )
    def test_call_on_instance(self, method_name):
        class_instance = self.testing_class()
        logbook = Queue()
        hooks.wiretap_instance_method(class_instance, method_name, logbook)
        method_handle = getattr(class_instance, method_name)
        result = method_handle(1, 2, three=4)
        assert result == ((1, 2), {"three": 4})
        assert logbook.get_nowait().function_name == method_name

    def test_classmethod_on_class__unaffected(self):
        """We set the wiretap on an instance and check the cls.class_method is
        not wiretapped.
        """
        class_obj = self.testing_class
        class_instance = class_obj()
        logbook = Queue()
        hooks.wiretap_instance_method(class_instance, "class_method", logbook)
        class_obj.class_method()
        assert logbook.empty

    def test_wiretapped_instance__does_not_affect_other_instance(self):
        # same class
        class_obj = self.testing_class
        # two instances
        class_instance_one = class_obj()
        class_instance_two = class_obj()

        logbook = Queue()
        hooks.wiretap_instance_method(class_instance_one, "normal_method", logbook)

        class_instance_two.normal_method()
        assert logbook.empty

    def test_wiretapped_instance__does_not_affect_new_instance(self):
        class_obj = self.testing_class
        class_instance_one = class_obj()

        logbook = Queue()
        hooks.wiretap_instance_method(class_instance_one, "normal_method", logbook)

        class_instance_two = class_obj()
        class_instance_two.normal_method()
        assert logbook.empty
