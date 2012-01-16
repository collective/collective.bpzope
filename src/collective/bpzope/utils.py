"""
This was originally written by Stefan Eletzhofer. It has since been
adapted for use with bpython here.

German Free Software License (D-FSL)

This Program may be used by anyone in accordance with the terms of the
German Free Software License
The License may be obtained under <http://www.d-fsl.org>.
"""
from types import StringType
import sys
import os
import textwrap

_marker = []


def shasattr(obj, attr, acquire=False):
    """See Archetypes/utils.py
    """
    if not acquire:
        obj = obj.aq_base
    return getattr(obj, attr, _marker) is not _marker


class ZopeDebug(object):

    def __init__(self):
        """Get Zope configured and start it up. We also set up the
        fake request and do a setSite to initialize the component
        architecture on the portal.
        """
        self.instancehome = os.environ.get("INSTANCE_HOME")
        configfile = os.environ.get("CONFIG_FILE")
        if configfile is None and self.instancehome is not None:
            configfile = os.path.join(self.instancehome, "etc", "zope.conf")
        if configfile is None:
            raise RuntimeError("CONFIG_FILE env not set")
        print "CONFIG_FILE=", configfile
        print "INSTANCE_HOME=", self.instancehome

        self.configfile = configfile
        try:
            from Zope2 import configure
        except ImportError:
            from Zope import configure
        configure(configfile)

        try:
            import Zope2
            app = Zope2.app()
        except ImportError:
            import Zope
            app = Zope.app()

        from Testing.makerequest import makerequest
        self.app = makerequest(app)

        try:
            self._make_permissive()
            print "Permissive security installed"
        except:
            print "Permissive security NOT installed"

        self._pwd = self.portal or self.app
        try:
            from zope.component import getSiteManager
            from zope.component import getGlobalSiteManager
            from zope.app.component.hooks import setSite
            if self.portal is not None:
                setSite(self.portal)
                gsm = getGlobalSiteManager()
                sm = getSiteManager()
                if sm is gsm:
                    print "ERROR SETTING SITE!"
        except:
            # XXX: Why is this a bare exception?
            pass

    @property
    def utils(self):
        class Utils(object):
            commit = self.commit
            sync = self.sync
            object_info = self.object_info
            ls = self.ls
            pwd = self.pwd
            cd = self.cd
            su = self.su
            catalog_info = self.catalog_info

            @property
            def cwd(self):
                return self.pwd()

        return Utils()

    @property
    def namespace(self):
        return dict(utils=self.utils, app=self.app, portal=self.portal)

    @property
    def portal(self):
        portals = self.app.objectValues("Plone Site")
        if len(portals):
            return portals[0]
        else:
            return None

    def pwd(self):
        return self._pwd

    def _make_permissive(self):
        """
        Make a permissive security manager with all rights. Hell,
        we're developers, aren't we? Security is for wimps. :)
        """
        from Products.CMFCore.tests.base.security import (
            PermissiveSecurityPolicy)
        import AccessControl
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SecurityManager import setSecurityPolicy

        _policy = PermissiveSecurityPolicy()
        self.oldpolicy = setSecurityPolicy(_policy)
        newSecurityManager(None, AccessControl.User.system)

    def su(self, username=None):
        """Change to named user. Return to permissive security
        policy if no username is given.
        """
        if username is None:
            self._make_permissive()
            print "PermissiveSecurityPolicy put back in place"
            return

        user = (
            self.portal.acl_users.getUser(username) or
            self.app.acl_users.getUser(username)
        )
        if not user:
            print "Can't find %s in %s" % (username, self.portal.acl_users)
            return

        from AccessControl.ZopeSecurityPolicy import ZopeSecurityPolicy
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SecurityManagement import getSecurityManager
        from AccessControl.SecurityManager import setSecurityPolicy

        _policy = ZopeSecurityPolicy()
        self.oldpolicy = setSecurityPolicy(_policy)
        wrapped_user = user.__of__(self.portal.acl_users)
        newSecurityManager(None, wrapped_user)
        print 'User changed.'
        return getSecurityManager().getUser()

    def catalog_info(self, obj=None, catalog='portal_catalog', query=None,
                       sort_on='created', sort_order='reverse'):
        """Inspect portal_catalog. Pass an object or object id for a
        default query on that object, or pass an explicit query.
        """
        if obj and query:
            print "Ignoring %s, using query." % obj

        catalog = self.portal.get(catalog)
        if not catalog:
            return 'No catalog'

        indexes = catalog._catalog.indexes
        if not query:
            if type(obj) is StringType:
                cwd = self.pwd()
                obj = cwd.unrestrictedTraverse(obj)
            # If the default in the signature is mutable, its value will
            # persist across invocations.
            query = {}
            if indexes.get('path'):
                from string import join
                path = join(obj.getPhysicalPath(), '/')
                query.update({'path': path})
            if indexes.get('getID'):
                query.update({'getID': obj.id, })
            if indexes.get('UID') and shasattr(obj, 'UID'):
                query.update({'UID': obj.UID(), })
        if indexes.get(sort_on):
            query.update({'sort_on': sort_on, 'sort_order': sort_order})
        if not query:
            return 'Empty query'
        results = catalog(**query)

        result_info = []
        for r in results:
            rid = r.getRID()
            if rid:
                result_info.append(
                        {'path': catalog.getpath(rid),
                        'metadata': catalog.getMetadataForRID(rid),
                        'indexes': catalog.getIndexDataForRID(rid), }
                        )
            else:
                result_info.append({'missing': rid})

        if len(result_info) == 1:
            return result_info[0]
        return result_info

    def commit(self):
        """Commit the current transaction
        """
        try:
            import transaction
            transaction.get().commit()
        except ImportError:
            get_transaction().commit()

    def sync(self):
        """Sync the current state from the ZODB
        """
        self.app._p_jar.sync()

    def object_info(self, obj=None):
        """Return a dictionary with information about the given object.
        If no object is passed in, give info about the current working
        directory.
        """
        if type(obj) is StringType:
            cwd = self.pwd()
            obj = cwd.unrestrictedTraverse(obj)
        if obj is None:
            obj = self.pwd()
        Title = ""
        title = getattr(obj, 'Title', None)
        if title:
            Title = title()
        return {'id': obj.getId(),
                'Title': Title,
                'portal_type': getattr(obj, 'portal_type', obj.meta_type),
                'folderish': obj.isPrincipiaFolderish,
                }

    def cd(self, path):
        """Change current dir to a specific folder.

        cd('..')
        cd('/Plone/news')
        cd(portal.news)
        """
        if type(path) is not StringType:
            path = '/'.join(path.getPhysicalPath())
        cwd = self.pwd()
        x = cwd.unrestrictedTraverse(path)
        if x is None:
            raise KeyError("Can't cd to %s" % path)

        print "%s -> %s" % (self.pwd().getId(), x.getId())
        self._pwd = x

    def ls(self, obj=None):
        """List the objects in the given object. If no object
        is given, list the contents of the current working directory.

        ls()
        ls('/Plone/news')
        ls(portal.news)
        """
        if type(obj) is StringType:
            cwd = self.pwd()
            obj = cwd.unrestrictedTraverse(obj)
        if obj is None:
            obj = self.pwd()
        if obj.isPrincipiaFolderish:
            return [self.objectInfo(o) for id, o in obj.objectItems()]
        else:
            return self.objectInfo(obj)


def main():
    """This is run via bpython with the -i option
    """
    SOFTWARE_HOME = os.environ.get("SOFTWARE_HOME")
    if SOFTWARE_HOME:
        sys.path.append(SOFTWARE_HOME)
        print "SOFTWARE_HOME=%s\n" % SOFTWARE_HOME
    else:
        print "No $SOFTWARE_HOME set, assume Zope >= 2.12 (Plone 4 has this)."

    zope_debug = ZopeDebug()

    available_utils = ", ".join([
        x for x in
        dir(zope_debug.utils)
        if not x.startswith("_")]
    )
    print textwrap.dedent("""
        ZOPE mode bpython shell.

          Bound names:
           app
           portal
           utils.{%s}

        If you call utils.su() with no arguments, the PermissiveSecurityPolicy
        will be put back in place.

        """ % available_utils)
    if SOFTWARE_HOME:
        print "Uses the $SOFTWARE_HOME and $CONFIG_FILE environment variables."
    else:
        print "Uses the $CONFIG_FILE environment variable."

    # now set up the variables for bpython to use
    global app
    global portal
    global utils
    app = zope_debug.app
    portal = zope_debug.portal
    utils = zope_debug.utils


main()
