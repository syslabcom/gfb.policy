from Acquisition import aq_inner
from plone.browserlayer.utils import registered_layers
from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.browser.menu import TranslateSubMenuItem
from Products.LinguaPlone.interfaces import ILinguaPloneProductLayer
from plone.app.contentmenu.menu import ActionsSubMenuItem
from plone.app.contentmenu.menu import DisplaySubMenuItem
from plone.app.contentmenu.menu import WorkflowMenu
from plone.memoize.view import memoize
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone.browser.ploneview import Plone
from zope.component import getMultiAdapter


def translation_menu_available(self):
    if self.disabled():
        return False  # pragma: no cover
    mtool = getToolByName(self.context, 'portal_membership')
    if not mtool.checkPermission('Modify portal content', self):
        return False
    return ILinguaPloneProductLayer in registered_layers()

TranslateSubMenuItem.available = translation_menu_available


orig_display_menu_available = DisplaySubMenuItem.available

def display_menu_available(self):
    mtool = getToolByName(self.context, 'portal_membership')
    if not mtool.checkPermission('Modify portal content', self):
        return False
    return orig_display_menu_available(self)

DisplaySubMenuItem.available = display_menu_available


orig_actions_menu_available = ActionsSubMenuItem.available

def actions_menu_available(self):
    mtool = getToolByName(self.context, 'portal_membership')
    if not mtool.checkPermission('Modify portal content', self):
        return False
    return orig_actions_menu_available(self)

ActionsSubMenuItem.available = actions_menu_available


orig_wf_getMenuItems = WorkflowMenu.getMenuItems

def wf_getMenuItems(self, context, request):
    """Return menu item entries in a TAL-friendly form."""
    mtool = getToolByName(context, 'portal_membership')
    if not mtool.checkPermission('Manage portal', context):
        return []
    return orig_wf_getMenuItems(self, context, request)

WorkflowMenu.getMenuItems = wf_getMenuItems


@memoize
def displayContentsTab(self):
    """Whether or not the contents tabs should be displayed
    """
    context = aq_inner(self.context)
    modification_permissions = (ModifyPortalContent,
                                AddPortalContent,
                                DeleteObjects,
                                ReviewPortalContent,
                                "CMFEditions: Checkout to location",)

    contents_object = context
    # If this object is the parent folder's default page, then the
    # folder_contents action is for the parent, we check permissions
    # there. Otherwise, if the object is not folderish, we don not display
    # the tab.
    if self.isDefaultPageInFolder():
        contents_object = self.getCurrentFolder()
    elif not self.isStructuralFolder():
        return 0

    # If this is not a structural folder, stop.
    plone_view = getMultiAdapter((contents_object, self.request),
                                 name='plone')
    if not plone_view.isStructuralFolder():
        return 0

    show = 0
    # We only want to show the 'contents' action under the following
    # conditions:
    # - If you have permission to list the contents of the relavant
    #   object, and you can DO SOMETHING in a folder_contents view. i.e.
    #   Copy or Move, or Modify portal content, Add portal content,
    #   or Delete objects.

    # Require 'List folder contents' on the current object
    if _checkPermission(ListFolderContents, contents_object):
        # If any modifications are allowed on object show the tab.
        for permission in modification_permissions:
            if _checkPermission(permission, contents_object):
                show = 1
                break

    return show

Plone.displayContentsTab = displayContentsTab
