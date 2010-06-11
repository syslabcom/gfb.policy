from Products.PloneHelpCenter.content.PHCContent import PHCContent
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFCore.utils import getToolByName

def getSubjectVocab(self):
    """Get subject (keywords) vocabulary"""
    catalog = getToolByName(self, 'portal_catalog')
    values = catalog.uniqueValuesFor('Subject')
    enc = getSiteEncoding(self)
    values = [unicode(x, enc) for x in values if type(x) != type(u'')]
    return values

PHCContent.getSubjectVocab = getSubjectVocab

