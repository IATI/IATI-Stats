IATI Stats
==========

.. image:: https://github.com/codeforIATI/IATI-Stats/actions/workflows/ci.yml/badge.svg?branch=main
    :target: https://github.com/codeforIATI/IATI-Stats/actions/workflows/ci.yml
.. image:: https://coveralls.io/repos/github/codeforIATI/IATI-Stats/badge.svg?branch=main
    :target: https://coveralls.io/github/codeforIATI/IATI-Stats?branch=main
.. image:: https://img.shields.io/badge/license-GPLv3-blue.svg
    :target: https://github.com/codeforIATI/IATI-Stats/blob/main/LICENSE.md

Introduction
------------

IATI-Stats is a python application for generating JSON stats files from IATI data. An example of the outputted JSON can be found at https://github.com/codeforIATI/IATI-Stats-public

These stats are used to build `Code for IATI Analytics <https://analytics.codeforiati.org/>`_.

Requirements
------------

-  Git
-  Python 3.x
-  pip
-  Bash
-  gcc
-  Development files for libxml, libxslt and libz e.g. ``libxml2-dev``,
   ``libxslt-dev``, ``lib32z1-dev`` (alternatively, you can install the python  dependencies in
   requirements.txt using your package manager, and skip the pip install step
   below)

For example, on Ubuntu these requirements can be installed by running:

.. code-block:: bash

    sudo apt-get install git python-dev python-virtualenv python-pip
    sudo apt-get install libxml2-dev libxslt-dev


Getting some data to run stats on
---------------------------------

This stats code expects a ``data/`` directory, containing a subdirectory for each publisher. Each publisher subdirectory contains that publisher's raw XML files.  All the data on the registry can be downloaded in this structure using Code for IATI’s `IATI Data Dump <https://iati-data-dump.codeforiati.org/>`__.

Getting started
---------------

Take a look at `this Github Action <https://github.com/codeforIATI/IATI-Stats/blob/main/.github/workflows/build.yml>`__ to see how this code is used.

You can run ``python calculate_stats.py --help`` for a full list of command line options.

Outputted JSON
~~~~~~~~~~~~~~

``loop`` produces json for each file, in the ``out`` directory. This
contains the stats calculated for each individual Activity and
Organisation, as well as by file.

``aggregate`` produces json aggregated at the publisher level, in
the ``aggregated`` directory. It also produces ``aggregated.json``,
which is the same, but for the entire dataset.

``invert`` produces ``inverted.json``, which has a list of publishers
for each stat.

Structure of stats functions
----------------------------

Stats definitions are located in a python module, by default ``stats.analytics`` (``stats/analytics.py``). This can be changed with the ``--stats-module`` flag. This module must contain the following classes:

-  ``PublisherStats``
-  ``ActivityStats``
-  ``ActivityFileStats``
-  ``OrganisationStats``
-  ``OrganisationFileStats``

See `./stats/countonly.py <https://github.com/codeforIATI/IATI-Stats/blob/main/stats/countonly.py>`__ for the structure of a simple stats module.

Each function within these classes is considered to be a stats function,
unless it begins with an underscore (``_``). In the appropriate context,
an object is created from the class, and each stats functions is called.

The functions will also be called with ``self.blank = True``, and should
return an empty version of their normal output, for aggregation
purposes. The ``returns_numberdict`` and ``returns_number`` decorators are
provided for this purpose.

To calculate a new stat, add a function to the appropriate class in
``stats/analytics.py`` (or a different stats module).

License
-------

::

    Copyright (C) 2013-2015 Ben Webb <bjwebb67@googlemail.com>
    Copyright (C) 2021 Andy Lulham <a.lulham@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Included Data
-------------

(these are not released under the same license as the software)

-  ``helpers/old/exchange_rates.csv`` derived from `Exchange
   rates.xls <http://www.oecd.org/dac/stats/Exchange%20rates.xls>`__
