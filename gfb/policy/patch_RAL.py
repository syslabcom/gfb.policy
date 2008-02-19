from Products.CMFCore.utils import getToolByName
from config import AVAILABLE_LANGUAGES_RAL
from zope.i18n import translate
from Products.Archetypes.utils import DisplayList

from Products.RiskAssessmentLink.content.RiskAssessmentLink import RiskAssessmentLink, RiskAssessmentLink_schema as schema
schema['provider'].widget.visible['edit'] = 'invisible'
schema['provider'].widget.visible['view'] = 'invisible'
schema['remoteProvider'].widget.visible['edit'] = 'invisible'
schema['remoteProvider'].widget.visible['view'] = 'invisible'


from Products.RemoteProvider.content.Provider import Provider, Provider_schema
unwantedFields = ('rights', 'subject', 'contributors', 'allowDiscussion', 'location',
    'creators', 'effectiveDate', 'expirationDate', 'creation_date', 'modification_date', 'language', 'sme', 
    'email', 'remoteLanguage', 'nace', 'country', 'provider')
for name in unwantedFields:
    if Provider_schema.get(name):
        Provider_schema[name].widget.visible['edit'] = 'invisible'
        Provider_schema[name].widget.visible['view'] = 'invisible'
        Provider_schema.changeSchemataForField(name, 'default')


from AccessControl import ClassSecurityInfo
security = ClassSecurityInfo()


security.declarePublic('at_post_edit_script')
def at_post_edit_script(self):
    """
    """

    def getMyProvider(self):
        pm = getToolByName(self, 'portal_membership')
        hf = pm.getHomeFolder()
        name = pm.getAuthenticatedMember().getUserId() 
        f = pm.getMembersFolder()
        path = "/".join( f.getPhysicalPath() ) + '/' + name
        res = self.portal_catalog(portal_type='Provider', path=path)
        return len(res) > 0 and res[0].getObject() or None

    provider = getMyProvider(self)
    if provider:
        self.setRemoteProvider(provider.UID())
        self.reindexObject()



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

RiskAssessmentLink.at_post_edit_script = at_post_edit_script
RiskAssessmentLink.at_post_create_script = at_post_edit_script
RiskAssessmentLink.getFilteredLanguages = getFilteredLanguages


