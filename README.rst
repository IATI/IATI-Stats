IATI Stats
==========

.. image:: https://travis-ci.org/IATI/IATI-Stats.svg?branch=master
    :target: https://travis-ci.org/IATI/IATI-Stats
.. image:: https://requires.io/github/IATI/IATI-Stats/requirements.svg?branch=master
    :target: https://requires.io/github/IATI/IATI-Stats/requirements/?branch=master
    :alt: Requirements Status
.. image:: https://coveralls.io/repos/IATI/IATI-Stats/badge.png?branch=master
    :target: https://coveralls.io/r/IATI/IATI-Stats?branch=master
.. image:: https://img.shields.io/badge/license-GPLv3-blue.svg
    :target: https://github.com/IATI/IATI-Stats/blob/master/GPL.md

Introduction
------------

IATI-Stats is a python application for generating JSON stats files from IATI data. An example of this outputted JSON can be found at http://dashboard.iatistandard.org/stats/

These stats are used to build the `IATI Dashboard <http://dashboard.iatistandard.org/>`_, and also to produce some of the stats for the Transparency Indicator and the IATI Annual report.

.. contents::

Requirements
------------

-  Git
-  Python 2.7
-  python-virtualenv
-  pip
-  Bash
-  gcc
-  Development files for libxml and libxslt e.g. ``libxml2-dev``,
   ``libxslt-dev`` (alternatively, you can install the python  dependencies in
   requirements.txt using your package manager, and skip the pip install step
   below)

On Ubuntu:

.. code-block:: bash

    sudo apt-get install git python-dev python-virtualenv python-pip
    sudo apt-get install libxml2-dev libxslt-dev


Getting some data to run stats on
---------------------------------

This stats code expects a `data/` directory containing subdirectories for each publisher, where each subdirectory contains that publisher's XML files. All the data on the registry can be downloaded in this structure using the `IATI-Registry-Refresher <https://github.com/IATI/IATI-Registry-Refresher/>`__.

The IATI Tech Team maintains an archive with a snapshot of this data taken every night, from which aggregate stats are produced for the dashboard, using the code in this repository. For political and security reasons this snapshot archive is not publicly available, but is available on request to others wishing to use it for aggregate calculations. Please email code [at] iatistandard [dot] org

Getting started
---------------

.. code-block:: bash

    # Get the code
    git clone https://github.com/IATI/IATI-Stats.git
    cd IATI-Stats

    # Put some IATI data in the 'data' directory
    # (see previous section)

    # Create a virtual environment (recommended)
    virtualenv pyenv
    source pyenv/bin/activate
    # Install python depencies
    pip install -r requirements.txt

    # Fetch helper data
    cd helpers
    git clone https://github.com/IATI/IATI-Rulesets.git
    ln -s IATI-Rulesets/rulesets .
    ./get_codelist_mapping.sh
    ./get_codelists.sh
    ./get_schemas.sh
    wget "http://dashboard.iatistandard.org/stats/ckan.json"
    wget "https://raw.githubusercontent.com/IATI/IATI-Dashboard/live/registry_id_relationships.csv"
    cd ..

    # Calculate some stats 
    python calculate_stats.py loop [--folder publisher-registry-id]
    python calculate_stats.py aggregate
    python calculate_stats.py invert
    # You will now have some JSON stats in the out/ directory

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

Stats definitions are located in a python module, by default ``stats.dashboard`` (``stats/dashboard.py``). This can be changed with the ``--stats-module`` flag. This module must contain the following classes:

-  ``PublisherStats``
-  ``ActivityStats``
-  ``ActivityFileStats``
-  ``OrganisationStats``
-  ``OrganisationFileStats``

See `./stats/countonly.py <https://github.com/IATI/IATI-Stats/blob/master/stats/countonly.py>`__ for the structure of a simple stats module.

Each function within these classes is considered to be a stats function,
unless it begins with an underscore (``_``). In the appropriate context,
an object is created from the class, and each stats functions is called.

The functions will also be called with ``self.blank = True``, and should
return an empty version of their normal output, for aggregation
purposes. The ``returns_numberdict`` and ``returns_number`` decorators are
provided for this purpose.

To calculate a new stat, add a function to the appropriate class in
``stats/dashboard.py`` (or a different stats module).


Running for every commit in the data directory
----------------------------------------------

If the data directory is a git repository (e.g. as a result of running `IATI-Registry-Refresher's git.sh <https://github.com/IATI/IATI-Registry-Refresher#creating-a-git-data-snapshot>`__), you can run the code: 

.. code-block:: bash

    # WARNING: This takes a long time (hours) and produces a lot of data (GBs)
    mkdir gitout
    ALL_COMMITS=1 ./git.sh

Environment variables for git.sh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The behaviour of `git.sh` can be modified using environment variables. `git_dashboard.sh` contains the two different runs of `git.sh` that are now used to generate data for the dashboard, each run with different environment variables.

The availible environment variables are:

GITOUT_DIR
    This is the output directory for git.sh (note that it uses the out directory for each commit, and then moves that to the appropriate place). Defaults to "gitout".
ALL_COMMITS
    By default git.sh only computes stats for the most recent commit. To override this, set this environment variable to any non-empty value.
GITOUT_SKIP_INCOMMITSDIR
    If this evironment variable has a non-empty value, a commit will be skipped if a directory already exists in $GITOUT_DIR/commits
COMMIT_SKIP_FILE
    The name of a file that will be grepped for the commit hash. If the hash exists in the file, the commit will be skipped. Defaults to "$GITOUT_DIR/gitaggregate/activities.json".

License
-------

::

    Copyright (C) 2013-2015 Ben Webb <bjwebb67@googlemail.com>

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

