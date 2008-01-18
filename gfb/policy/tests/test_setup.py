import unittest
from gfb.policy.tests.base import GFBPolicyTestCase

from Products.CMFCore.utils import getToolByName

class TestSetup(GFBPolicyTestCase):

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

    def test_portal_title(self):
        self.assertEquals("GFB Portal", self.portal.getProperty('title'))
    
    #def test_portal_description(self):
    #    self.assertEquals("Welcome to the GFB portal", self.portal.getProperty('description'))
    #
    #def test_riskassessmentlink_installed(self):
    #    self.failUnless('RiskAssessmentLink' in self.types.objectIds())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
