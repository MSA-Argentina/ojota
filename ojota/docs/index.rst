.. Ojota documentation master file, created by
   sphinx-quickstart on Wed Jul 25 21:11:58 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Ojota's documentation!
=================================

Ojota is a ORM and flat file database engine.

Ojota is Free Software! you can check the code at http://bitbucket.org/msa_team/ojota

Supported data formats
=======================
 * JSON
 * YAML
 * JSON through web service

Installation
============
With easy_install

.. code-block:: bash

    sudo easy_install ojota

With pip

.. code-block:: bash

    sudo pip install ojota

From source

.. code-block:: bash

    hg clone ssh://hg@bitbucket.org/msa_team/ojota
    sudo python setup.py install

Table of contents
=================
.. toctree::
   :maxdepth: 2

    Read the module documentation <module>
    Some examples<examples>

Optional dependencies
=====================
 * pyyaml - To fecth the data from a file with YAML format
 * request - To fetch JSON form web sevice
 * flask -- To run the example web service.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

