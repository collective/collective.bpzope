Introduction
============

The collective.bpzope package provides the initialization file to start
`bpython`_ as a Zope interactive debugging shell. It is intended to be
used with `zc.buildout`_ to generate the script.

The code for the script was ported over from the
`Zope IPython profile`_, and the idea was inspired by a
`blog post by Rigel Di Scala`_.

.. contents::

Buildout Configuration
======================

The script is generated using `zc.recipe.egg`_, this allows for some
initialization code to be run before invoking ``bpzope``. The following
will demonstrate how to set this up for use with and Plone 4.

Use with Plone 3 is not supported since there is no Python 2.4
compatible version of bpython that can read in a file with ``-i``.

To effectively use the ``bpzope`` interactive shell, you are encouraged
to use a ZEO server. This will allow you to run the site, and the
interpreter at the same time. See `plone.recipe.zeoserver`_.

Here is the configuration needed to set up the Zope aware bpython shell
for Plone 4::

    [buildout]
    parts =
        instance
        bpzope
    extends = http://dist.plone.org/release/4.1.3/versions.cfg
    
    [instance]
    recipe = plone.recipe.zope2instance
    user = admin:admin
    eggs =
        Plone
        Pillow
    
    [bpzope]
    recipe = zc.recipe.egg
    eggs =
        collective.bpzope
        ${instance:eggs}
    initialization =
        import os
        import pkg_resources
        os.environ["INSTANCE_HOME"] = "${instance:location}"
        zope_utils = pkg_resources.resource_filename('collective.bpzope', 'utils.py')
        sys.argv[1:1] = ("-i %s" % zope_utils).split()

The bpzope interpreter
======================

After running buildout, there will be a ``bpzope`` script generated::

    $ bin/buildout
    $ bin/bpzope

This will be a debug prompt like ``bin/instance debug``. The variable
``app`` will be bound to the Zope instance::

    >>> app
    <Application at >

The variable ``portal`` will be bound to the first Plone site that is
found::

    >>> portal
    <PloneSite at /Plone>

Utils
-----

There are an assortment of utilities that can be found with the
``utils`` variable.

The current user can be switched::

    >>> utils.su('admin')
    User changed.
    <PropertiedUser 'admin'>

Then can be switched back to the default user by calling it with no
argument::

    >>> utils.su()
    PermissiveSecurityPolicy put back in place

If there are changes to the current transaction, they can be
committed::

    >>> utils.commit()

The current session can be put into sync with changes that have been
made to the database::

    >>> utils.sync()


Change the working directory to a new one. Pass in a string or an
object::

    >>> utils.cd(portal.foo.bar)
    >>> utils.cd('foo/bar')
    >>> utils.cd('..')

There is a property of the utils object that prints out the current
working directory::

    >>> utils.cwd
    <PloneSite at /Plone>
    >>> utils.cd('foo/bar')
    >>> utils.cwd
    <ATFolder at /Plone/foo/bar>

Get the catalog information about a certain object::

    >>> utils.catalog_info(portal.foo)
    {'path': '/Plone/foo', ...}

See a listing of objects for a given object. Pass in an object or a
string. If no argument is given, list the current working directory::

    >>> utils.ls()
    [{'folderish': 1, 'portal_type': 'Folder', 'id': 'foo', 'Title': 'Foo Folder'}, ...]
    >>> utils.ls(portal.foo)
    [{'folderish': 1, 'portal_type': 'Folder', 'id': 'bar', 'Title': 'Bar Folder'}]
    >>> utils.ls('foo')
    [{'folderish': 1, 'portal_type': 'Folder', 'id': 'bar', 'Title': 'Bar folder'}]

Lastly, get information about a particular object::

    >>> utils.object_info()
    {'folderish': 1, 'portal_type': 'Plone Site', 'id': 'Plone', 'Title': 'Plone site'}
    >>> utils.object_info(portal.foo)
    {'folderish': 1, 'portal_type': 'Folder', 'id': 'foo', 'Title': 'Foo Folder'}
    >>> utils.object_info('foo')
    {'folderish': 1, 'portal_type': 'Folder', 'id': 'foo', 'Title': 'Foo Folder'}


.. _bpython: http://bpython-interpreter.org/
.. _zc.buildout: http://pypi.python.org/pypi/zc.buildout
.. _Zope IPython profile: http://svn.plone.org/svn/collective/dotipython/trunk/ipy_profile_zope.py
.. _blog post by Rigel Di Scala: http://blog.ipnext.it/?p=285
.. _zc.recipe.egg: http://pypi.python.org/pypi/zc.recipe.egg
.. _plone.recipe.zeoserver: http://pypi.python.org/pypi/plone.recipe.zeoserver


