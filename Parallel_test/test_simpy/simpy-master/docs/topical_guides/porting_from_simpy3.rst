.. _porting_from_simpy3:

=========================
Porting from SimPy 3 to 4
=========================

SimPy 4 drops support for Python 2.7 and requires Python 3.6+. SimPy 4 also
breaks compatibility with SimPy 3 in a few minor ways.


Python 3.6+
===========

When porting a SimPy application to SimPy 4, the first step is to ensure that
the application works with SimPy 3 on Python >= 3.6. Once the application works
with Python 3.6, most of the work in porting to SimPy 4 is complete.

For more information on porting from Python 2 to 3, see `this guide
<https://docs.python.org/3/howto/pyporting.html>`_ from the Python docs.


Environment Subclasses
======================

The ``BaseEnvironment`` class has been removed in SimPy 4. The
:class:`~simpy.core.Environment` class is now the most base environment class.
Any code that inherited from ``BaseEnvironment`` should be modified to inherit
from :class:`~simpy.core.Environment` instead.

For example, the following SimPy 3 code:

.. code-block:: python

   class MyEnvironment(simpy.BaseEnvironment):
       ...

would be rewritten as follows for SimPy 4:

.. code-block:: python

   class MyEnvironment(simpy.Environment):
       ...


Returning from Process Generators
=================================

In Python 2 it is a syntax error for a generator (i.e. a function using the
``yield`` keyword) to return a value using the ``return`` keyword. SimPy 3,
supports a process generator returning a value via the
``Environment.exit(value)`` method, which simply raises a ``StopProcess``
exception. This mechanism was required for Python 2, but also works with
Python 3.

In Python 3, it is legal to use ``return`` to return a value from a generator.
Returning from a :class:`~simpy.events.Process` generator is also supported in
SimPy 3 for applications using Python 3 exclusively.

In SimPy 4, the ``Environment.exit()`` method and the ``StopProcess`` exception
are eliminated. Applications with generators that need to either return early
or return a value *must* use the ``return`` Python keyword.

.. note::

   No change is required for generators that do not return a value or that do
   not have control flow that requires returning early. This is the most common
   case for process generators used with SimPy.

Once a SimPy 3 application is ported to run with Python 3, it may then replace
any uses of ``Environment.exit(value)`` and ``raise StopProcess(value)`` with
``return value``. Once all occurences are changed, the application will be ready
to run with SimPy 4.

Example: Return from Generator
------------------------------

In the following example, ``Environment.exit()`` is used to return the first the
first "needle" from a store of items. When using SimPy 3 with Python 2, this is
the only way to return a value from a process generator.

.. code-block:: python

   def find_first_needle(env, store):
       while True:
           item = yield store.get()
           if is_needle(item):
               env.exit(item)  # Python2 generators cannot use return

   def proc(env, store):
       needle = yield env.process(find_first_needle(env, store))

In SimPy 4 or whith SimPy 3 and Python 3, ``find_first_needle()`` can be
rewritten as:

.. code-block:: python

   def find_first_needle(env, store):
       while True:
           item = yield store.get()
           if is_needle(item):
               return item  # A Python3 generator can return


Sticking with SimPy 3
=====================

For applications that are not yet ready to upgrade to SimPy 4 and Python 3, or
that may never upgrade, the SimPy dependency must be pinned to version 3.x.

When installing SimPy with ``pip``, use the following to force the latest SimPy
3.x to be installed:

.. code-block:: shell

   pip install 'simpy<4'

A similar version specification can be used in `requirements files
<https://pip.pypa.io/en/stable/user_guide/#requirements-files>`_:

.. code-block:: text

   simpy<4

Or in the ``install_requires`` list in a ``setup.py`` file:

.. code-block:: python

   setup(
       ...,
       install_requires=['simpy<4'],
       ...,
   )
