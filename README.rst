**Early alfa version**!
The gap-restapi is reimplementation of Google's endpoints library which is
beautiful with all that tools like API Explorer, but are not of production
quality (at the time of writing this README).

The main benefits of gap-restapi over endpoints ...

- your application will more probably survive GAE update (as my did not in
  1.8.4 -> 1.8.5)
- gap-restapi is really simple and reliable
- stricttype used for validation does validates (no more "Internal Server
  Error" on invalid API call)
- stricttype.Message can be extended which allows better modeling of structured
  in/out data
- public API can have more error codes than just 400 or 503
- the handler is inherited from webapp2.RequestHandler and can be farther
  extended for your needs (ie. limit access to IP addresses).

Example
-------
(example is not ready yet, look in `tests <tests/test_restapi_web.py>`__ to see restapi in action)

.. code:: python

   # here will be an example of usage

Features
--------

What is still missing?
----------------------
- raise error if decorator misses required variables for get
