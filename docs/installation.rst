Installation
============

Supported Platforms
-------------------
Python 2.6, 2.7, 3.3, and 3.4 are supported.  Both CPython (the standard Python
implementation) and `PyPy <http://pypy.org>`_ are supported and tested
against.

Linux, OSX, and Windows are supported.

Installation through pip
------------------------
`pip <https://pypi.python.org/pypi/pip>`_ is the suggested tool for installing
packages.  It will handle installing all python dependencies for the driver at
the same time as the driver itself.  To install the driver::

    pip install cassandra-driver

You can use ``pip install --pre cassandra-driver`` if you need to install a beta version.

OSX Installation Error
^^^^^^^^^^^^^^^^^^^^^^
If you're installing on OSX and have XCode 5.1 installed, you may see an error like this::

    clang: error: unknown argument: '-mno-fused-madd' [-Wunused-command-line-argument-hard-error-in-future]

To fix this, re-run the installation with an extra compilation flag::

    ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install cassandra-driver

Manual Installation
-------------------
You can always install the driver directly from a source checkout or tarball.
When installing manually, ensure the python dependencies are already
installed. You can find the list of dependencies in
`requirements.txt <https://github.com/datastax/python-driver/blob/master/requirements.txt>`_.

Once the dependencies are installed, simply run::

    python setup.py install

Verifying your Installation
---------------------------
To check if the installation was successful, you can run::

    python -c 'import cassandra; print cassandra.__version__'

It should print something like "2.0.0".

(*Optional*) Compression Support
--------------------------------
Compression can optionally be used for communication between the driver and
Cassandra.  There are currently two supported compression algorithms:
snappy (in Cassandra 1.2+) and LZ4 (only in Cassandra 2.0+).  If either is
available for the driver and Cassandra also supports it, it will
be used automatically.

For lz4 support::

    pip install lz4

For snappy support::

    pip install python-snappy

(If using a Debian Linux derivative such as Ubuntu, it may be easier to
just run ``apt-get install python-snappy``.)

(*Optional*) Metrics Support
----------------------------
The driver has built-in support for capturing :attr:`.Cluster.metrics` about
the queries you run.  However, the ``scales`` library is required to
support this::

    pip install scales

(*Optional*) Sorted Sets
------------------------
Cassandra can store entire collections within a column.  One of those
collection types is a set.  Cassandra's sets are actually ordered
sets.  By default, the driver will use unordered sets to represent
these collections.  If you would like to maintain the ordering,
install the ``blist`` library::

    pip install blist

(*Optional*) Non-python Dependencies
------------------------------------
The driver has several **optional** features that have non-Python dependencies.

C Extensions
^^^^^^^^^^^^
By default, two C extensions are compiled: one that adds support
for token-aware routing with the ``Murmur3Partitioner``, and one that
allows you to use `libev <http://software.schmorp.de/pkg/libev.html>`_
for the event loop, which improves performance.

When installing manually through setup.py, you can disable both with
the ``--no-extensions`` option, or selectively disable one or the other
with ``--no-murmur3`` and ``--no-libev``.

To compile the extenions, ensure that GCC and the Python headers are available.

On Ubuntu and Debian, this can be accomplished by running::

    $ sudo apt-get install gcc python-dev

On RedHat and RedHat-based systems like CentOS and Fedora::

    $ sudo yum install gcc python-devel

On OS X, homebrew installations of Python should provide the necessary headers.

libev support
^^^^^^^^^^^^^
The driver currently uses Python's ``asyncore`` module for its default
event loop.  For better performance, ``libev`` is also supported through
a C extension.

If you're on Linux, you should be able to install libev
through a package manager.  For example, on Debian/Ubuntu::

    $ sudo apt-get install libev4 libev-dev

On RHEL/CentOS/Fedora::

    $ sudo yum install libev libev-devel

If you're on Mac OS X, you should be able to install libev
through `Homebrew <http://brew.sh/>`_. For example, on Mac OS X::

    $ brew install libev

If successful, you should be able to build and install the extension
(just using ``setup.py build`` or ``setup.py install``) and then use
the libev event loop by doing the following:

.. code-block:: python

    >>> from cassandra.io.libevreactor import LibevConnection
    >>> from cassandra.cluster import Cluster

    >>> cluster = Cluster()
    >>> cluster.connection_class = LibevConnection
    >>> session = cluster.connect()

(*Optional*) Configuring SSL
-----------------------------
Andrew Mussey has published a thorough guide on
`Using SSL with the DataStax Python driver <http://blog.amussey.com/post/64036730812/cassandra-2-0-client-server-ssl-with-datastax-python>`_.
