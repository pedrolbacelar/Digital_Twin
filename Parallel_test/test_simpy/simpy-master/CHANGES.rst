Changelog for SimPy
===================

4.0.1 - 2020-04-15
------------------

- [FIX] Typing repair for Get and Put as ContextManagers


4.0.0 - 2020-04-06
------------------

- [BREAKING] Python 3.6 is the minimum supported version
- [BREAKING] ``BaseEnvironment`` is eliminated. Inherit ``Environment`` instead.
- [BREAKING] ``Environment.exit()`` is eliminated. Use ``return`` instead.
- [NEW] "Porting from SimPy 3 to 4" topical guide in docs
- [NEW] SimPy is now fully type annotated (PEP-483, PEP-484)
- [NEW] PEP-517/PEP-518 compatible build system


3.0.13 - 2020-04-05
-------------------

- [FIX] Repair several minor typos in documentation
- [FIX] Possible AttributeError in Process._resume()
- [CHANGE] Use setuptools_scm in distribution build


3.0.12 - 2020-03-12
-------------------

- [FIX] Fix URLs for GitLab.com and re-release


3.0.11 - 2018-07-13
-------------------

- [FIX] Repair Environment.exit() to support PEP-479 and Python 3.7.
- [FIX] Fix wrong usage_since calculation in preemptions
- [NEW] Add "Time and Scheduling" section to docs
- [CHANGE] Move Interrupt from events to exceptions
- [FIX] Various minor documentation improvements

3.0.10 – 2016-08-26
-------------------

- [FIX] Conditions no longer leak callbacks on events (thanks to Peter Grayson).

3.0.9 – 2016-06-12
------------------

- [NEW] PriorityStore resource and performance benchmarks were implemented by
  Peter Grayson.
- [FIX] Support for identifying nested preemptions was added by Cristian Klein.

3.0.8 – 2015-06-23
------------------

- [NEW] Added a monitoring guide to the documentation.
- [FIX] Improved packaging (thanks to Larissa Reis).
- [FIX] Fixed and improved various test cases.


3.0.7 – 2015-03-01
------------------

- [FIX] State of resources and requests were inconsistent before the request
  has been processed (`issue #62 <https://bitbucket.org/simpy/simpy/issue/
  62>`__).
- [FIX] Empty conditions were never triggered (regression in 3.0.6, `issue #63
  <https://bitbucket.org/simpy/simpy/issue/63>`__).
- [FIX] ``Environment.run()`` will fail if the until event does not get
  triggered (`issue #64 <https://bitbucket.org/simpy/simpy/issue/64>`__).
- [FIX] Callback modification during event processing is now prohibited (thanks
  to Andreas Beham).


3.0.6 - 2015-01-30
------------------

- [NEW] Guide to SimPy resources.
- [CHANGE] Improve performance of condition events.
- [CHANGE] Improve performance of filter store (thanks to Christoph Körner).
- [CHANGE] Exception tracebacks are now more compact.
- [FIX] ``AllOf`` conditions handle already processed events correctly (`issue
  #52 <https://bitbucket.org/simpy/simpy/issue/52>`__).
- [FIX] Add ``sync()`` to ``RealtimeEnvironment`` to reset its internal
  wall-clock reference time (`issue #42 <https://bitbucket.org/simpy/simpy/
  issue/42>`__).
- [FIX] Only send copies of exceptions into processes to prevent traceback
  modifications.
- [FIX] Documentation improvements.


3.0.5 – 2014-05-14
------------------

- [CHANGE] Move interruption and all of the safety checks into a new event
  (`pull request #30`__)
- [FIX] ``FilterStore.get()`` now behaves correctly (`issue #49`__).
- [FIX] Documentation improvements.

__ https://bitbucket.org/simpy/simpy/pull-request/30
__ https://bitbucket.org/simpy/simpy/issue/49


3.0.4 – 2014-04-07
------------------

- [NEW] Verified, that SimPy works on Python 3.4.
- [NEW] Guide to SimPy events
- [CHANGE] The result dictionary for condition events (``AllOF`` / ``&`` and
  ``AnyOf`` / ``|``) now is an *OrderedDict* sorted in the same way as the
  original events list.
- [CHANGE] Condition events now also except processed events.
- [FIX] ``Resource.request()`` directly after ``Resource.release()`` no longer
  successful. The process now has to wait as supposed to.
- [FIX] ``Event.fail()`` now accept all exceptions derived from
  ``BaseException`` instead of only ``Exception``.


3.0.3 – 2014-03-06
------------------

- [NEW] Guide to SimPy basics.
- [NEW] Guide to SimPy Environments.
- [FIX] Timing problems with real time simulation on Windows (issue #46).
- [FIX] Installation problems on Windows due to Unicode errors (issue #41).
- [FIX] Minor documentation issues.


3.0.2 – 2013-10-24
------------------

- [FIX] The default capacity for ``Container`` and ``FilterStore`` is now also
  ``inf``.


3.0.1 – 2013-10-24
------------------

- [FIX] Documentation and default parameters of ``Store`` didn't match. Its
  default capacity is now ``inf``.


3.0 – 2013-10-11
----------------

SimPy 3 has been completely rewritten from scratch. Our main goals were to
simplify the API and code base as well as making SimPy more flexible and
extensible. Some of the most important changes are:

- Stronger focus on events. Processes yield event instances and are suspended
  until the event is triggered. An example for an event is a *timeout*
  (formerly known as *hold*), but even processes are now events, too (you can
  wait until a process terminates).

- Events can be combined with ``&`` (and) and ``|`` (or) to create
  *condition events*.

- Process can now be defined by any generator function. You don't have to
  subclass ``Process`` anymore.

- No more global simulation state. Every simulation stores its state in an
  *environment* which is comparable to the old ``Simulation`` class.

- Improved resource system with newly added resource types.

- Removed plotting and GUI capabilities. `Pyside`__ and `matplotlib`__ are much
  better with this.

- Greatly improved test suite. Its cleaner, and the tests are shorter and more
  numerous.

- Completely overhauled documentation.

There is a `guide for porting from SimPy 2 to SimPy 3`__. If you want to stick
to SimPy 2 for a while, change your requirements to ``'SimPy>=2.3,<3'``.

All in all, SimPy has become a framework for asynchronous programming based on
coroutines. It brings more than ten years of experience and scientific know-how
in the field of event-discrete simulation to the world of asynchronous
programming and should thus be a solid foundation for everything based on an
event loop.

You can find information about older versions on the `history page`__

__ http://qt-project.org/wiki/PySide
__ http://matplotlib.org/
__ https://simpy.readthedocs.io/en/latest/topical_guides/porting_from_simpy2.html
__ https://simpy.readthedocs.io/en/latest/about/history.html
