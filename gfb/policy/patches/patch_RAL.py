from Products.CMFCore.utils import getToolByName
from gfb.policy.config import AVAILABLE_LANGUAGES_RAL
from zope.i18n import translate
from Products.Archetypes.utils import DisplayList
from Products.RiskAssessmentLink.content.RiskAssessmentLink import RiskAssessmentLink


#from Products.RemoteProvider.content.Provider import Provider, Provider_schema
#unwantedFields = ('rights', 'subject', 'contributors', 'allowDiscussion', 'location',
#    'creators', 'effectiveDate', 'expirationDate', 'creation_date', 'modification_date', 'language', 'sme', 
#    'email', 'remoteLanguage', 'nace', 'country', 'provider')
#for name in unwantedFields:
#    if Provider_schema.get(name):
#        Provider_schema[name].widget.visible['edit'] = 'invisible'
#        Provider_schema[name].widget.visible['view'] = 'invisible'
#        Provider_schema.changeSchemataForField(name, 'default')
#
## make providerCategory required
#Provider_schema['providerCategory'].required = True


def getFilteredLanguages(self):
    """ return the languages filtered by the abbreviations given in the config file """
    plt = getToolByName(self, 'portal_languages')
    langs = plt.listAvailableLanguages()
    L = []
    for l in langs:
        if l[0] in AVAILABLE_LANGUAGES_RAL:
            L.append((l[0], translate(l[1]) ))
    L.sort()
    return DisplayList(L)

RiskAssessmentLink.getFilteredLanguages = getFilteredLanguages


