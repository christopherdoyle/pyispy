=====
PyISpy
=====


.. image:: https://img.shields.io/pypi/v/pyispy.svg
        :target: https://pypi.python.org/pypi/pyispy

.. image:: https://img.shields.io/travis/christopherdoyle/pyispy.svg
        :target: https://travis-ci.org/christopherdoyle/pyispy

.. image:: https://readthedocs.org/projects/pyispy/badge/?version=latest
        :target: https://pyispy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status







* Free software: MIT license
* Documentation: https://pyispy.readthedocs.io.


Testing helper utility for monitoring calls to functions and methods (spying).


Example
-------

.. code-block:: python

    import my_module
    import pyispy

    def my_ClassA():
        reports = []
        pyispy.wiretap(my_module.ClassA, ["__init__", "exec"], reports)

        obj = my_module.ClassA()

        assert "__init__" in reports


TODO
----

* Refactor hooks as classes to contract input arguments (object, function name,
  logbook) to support polymorphic attitude in ``process_request``.
* Implement/test wiretap on magic methods
    * Handle response to read-only functions (for example ``__add__`` in int type)


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
