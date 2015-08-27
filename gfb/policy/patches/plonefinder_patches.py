from Acquisition import aq_base
from Acquisition import aq_inner
from collective.plonefinder.browser.finder import Finder
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


def setScopeInfos(self, context, request, showbreadcrumbs):
    """
    set scope and all infos related to scope
    """
    browsedpath = request.get('browsedpath', self.browsedpath)
    portal = self.data['portal']
    # find browser root and rootpath if undefined
    if self.data['root'] is None:
        self.data['root'] = root = aq_inner(portal.restrictedTraverse(
            self.rootpath))
        if not self.rootpath:
            self.rootpath = '/'.join(root.getPhysicalPath())
    # find scope if undefined
    # by default scope = browsedpath or first parent folderish
    # or context if context is a folder
    scope = self.data['scope']
    if scope is None:
        if browsedpath:
            self.data['scope'] = scope = aq_inner(
                    portal.restrictedTraverse(browsedpath))
        else:
            # PATCH
            # In case this is a working copy, set the scope to the
            # original scope
            iterate_control = getMultiAdapter(
                (aq_inner(context), request), name='iterate_control')
            folder = (
                aq_inner(iterate_control.get_original(context)) or
                aq_inner(context))
            if not bool(getattr(
                        aq_base(folder), 'isPrincipiaFolderish', False)):
                folder = aq_inner(folder.aq_parent)
            self.data['scope'] = scope = folder

    self.scopetitle = scope.pretty_title_or_id()
    self.scopetype = scopetype = scope.portal_type
    self.scopeiconclass = ('contenttype-%s divicon' %
            scopetype.lower().replace(' ', '-'))

    # set browsedpath and browsed_url
    self.browsedpath = '/'.join(scope.getPhysicalPath())
    self.browsed_url = scope.absolute_url()
    if scope is not self.data['root']:
        parentscope = aq_inner(scope.aq_parent)
        self.parentpath = '/'.join(parentscope.getPhysicalPath())

    # set breadcrumbs
    # TODO : use self.data['catalog']
    portal_membership = getToolByName(context, "portal_membership")
    if showbreadcrumbs:
        crumbs = []
        item = scope
        itempath = self.browsedpath
        while itempath != self.rootpath:
            crumb = {}
            crumb['path'] = itempath
            crumb['title'] = item.title_or_id()
            crumb['show_link'] = portal_membership.checkPermission(
                    'View', item)
            crumbs.append(crumb)
            item = aq_inner(item.aq_parent)
            itempath = '/'.join(item.getPhysicalPath())
        crumbs.reverse()
        self.breadcrumbs = crumbs


Finder.setScopeInfos = setScopeInfos