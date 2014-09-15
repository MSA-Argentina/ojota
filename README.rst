.. Ojota documentation master file, created by
   sphinx-quickstart on Wed Jul 25 21:11:58 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Ojota's documentation!
=================================

Ojota is a ORM and flat file database engine.

Ojota is Free Software! you can check the code at https://github.com/MSA-Argentina/ojota 


How does it works?
==================

First we will define the data object

.. code-block:: python

    # The information is stored in a file called Persons.json
    class Person(Ojota):
        required_fields = ("name", "address", "age")
        cache  = Memcache()

    # The information is stored in a file called Teams.yaml
    class Team(Ojota):
        pk_field = "id"
        data_source = YAMLSource()
        required_fields = ("id", "name", "color")

        def __repr__(self):
            return self.name

Just with that we can query the ORM objects

.. code-block:: python

    # Some Example queries
    # "all" returns all the Person Objects
    Person.all()
    # "many will return filtered results
    Person.many(age=30, sorted="name")
    Person.many(age__lt=30, sorted="-name")
    Person.many(sorted="name")

    # "one" will get only one object
    Team.one(1) # you can just send the primary key
    Team.one(name="River Plate")

    # You can sub-query over the results
    persons = Person.all()
    elders = persons.many(age__gt=30)
    fat_elders = elders.many(weight__gt=50)
    female_elders = elders.many(gender="F")

That's it your information will be stored in plain text and you will have a
powerfull ORM to play with it

Supported data formats
=======================
 * JSON
 * DSON
 * YAML
 * CSV
 * JSON through web service
 * XLS

New Features for 2.0
=====================
 * QuerySets with recursive filtering
 * "Callbacks" support (you can add custom properties with a callback function)
 * Hierarchical Objects support

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

    git clone https://github.com/MSA-Argentina/ojota.git
    sudo python setup.py install

Optional dependencies
=====================
 * pyyaml - To fecth the data from a file with YAML format
 * dogeon - To fecth the data from a file with DSON format
 * request - To fetch JSON form web sevice
 * flask -- To run the example web service.

You might also want to to take a look at Ojota's sister project called Havaiana http://havaiana.rtfd.org  
