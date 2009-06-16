from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

# These are traditional products (in the Products namespace). They'd normally
# be loaded automatically, but in tests we have to load them explicitly. This
# should happen at module level to make sure they are available early enough.

from Products.PloneTestCase import layer

SiteLayer = layer.PloneSite

class GFBPolicyLayer(SiteLayer):
    @classmethod
    def setUp(cls):
        ptc.setupPloneSite(products=['gfb.policy'])
        ztc.installProduct('ATVocabularyManager')
        ztc.installProduct('LinguaPlone')
        ztc.installProduct('TextIndexNG3')
        ztc.installProduct('ProxyIndex')
        ztc.installProduct('ATCountryWidget')
        SiteLayer.setUp()


class GFBPolicyTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """
    layer = GFBPolicyLayer
