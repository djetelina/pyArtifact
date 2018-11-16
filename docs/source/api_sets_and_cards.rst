Card objects
------------

.. currentmodule:: pyartifact.sets_and_cards

In order to easily work with cards (and abilities), pyartifact wraps them in easier to use
objects. The objects are made by inheriting multiple bases, where each base indicates the presence
of a certain attribute. For example all objects inheriting the :py:class:`Unit` class will have
attack, armor and hit_points attributes.

Card types
~~~~~~~~~~

Some cards from Valve's API are not included in this library, because they are more of a core mechanics,
these cards would have the type of Stronghold and Pathing.

Cards
^^^^^

.. autoclass:: Hero
.. autoclass:: Creep
.. autoclass:: Spell
.. autoclass:: Improvement
.. autoclass:: Item

Abilities
^^^^^^^^^

.. autoclass:: Ability
.. autoclass:: PassiveAbility

Card Base classes
~~~~~~~~~~~~~~~~~

Base
^^^^

.. autoclass:: CardBase


Colored card
^^^^^^^^^^^^

.. autoclass:: ColoredCard

Unit
^^^^

.. autoclass:: Unit

NotAbility
^^^^^^^^^^^

.. autoclass:: NotAbility

Castable
^^^^^^^^

.. autoclass:: Castable
