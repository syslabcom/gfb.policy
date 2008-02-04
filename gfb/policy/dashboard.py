from zope.interface import implements
from zope.component import adapts, queryUtility

from zope.app.container.interfaces import INameChooser

from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from Products.PluggableAuthService.interfaces.authservice import IBasicUser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import USER_CATEGORY

from plone.app.portlets.interfaces import IDefaultDashboard
from plone.app.portlets import portlets
from gfb.theme.portlets import myral, myprovider

from plone.app.portlets.storage import UserPortletAssignmentMapping


# Adapter to configure users Dashboard


class DefaultDashboard(object):
    """Define an adapter from the user/principal type (by default, this is
    Products.PluggableAuthService.interfaces.authservice.IBasicUser) to
    this interface and implement __call__ to return a mapping of dashboard
    settings. When a new user is created, this adapter will be invoked to
    build a default dashboard.
    """

    implements(IDefaultDashboard)
    adapts(IPropertiedUser)

    def __init__(self, principal):
        self.principal = principal

    def __call__(self):
        return {
            'plone.dashboard1' : (myprovider.Assignment(),),
            'plone.dashboard2' : (myral.Assignment(),),
            'plone.dashboard3' : (),
            'plone.dashboard4' : (portlets.review.Assignment(),),
        }
