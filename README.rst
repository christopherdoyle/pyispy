=====
PySpy
=====


.. image:: https://img.shields.io/pypi/v/pyspy.svg
        :target: https://pypi.python.org/pypi/pyspy

.. image:: https://img.shields.io/travis/christopherdoyle/pyspy.svg
        :target: https://travis-ci.org/christopherdoyle/pyspy

.. image:: https://readthedocs.org/projects/pyspy/badge/?version=latest
        :target: https://pyspy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status







* Free software: MIT license
* Documentation: https://pyspy.readthedocs.io.


Testing helper utility for monitoring calls to functions and methods (spying).


Example
-------

```python
import my_module
import pyspy

def my_ClassA():
    reports = []
    pyspy.wiretap(my_module.ClassA, ["__init__", "exec"], reports)

    obj = my_module.ClassA()

    assert "__init__" in reports
```


TODO
----

* Refactor hooks as classes to contract input arguments (object, function name,
  logbook) to support polymorphic attitude in ``process_request``.
* Implement ``SpyReport == <function_name>``
* Implement/test wiretap on magic methods
    * Handle response to read-only functions (for example ``__add__`` in int type)


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
