from Products.CMFCore.utils import getToolByName

from Products.RiskAssessmentLink.content.RiskAssessmentLink import RiskAssessmentLink, RiskAssessmentLink_schema as schema
schema['provider'].widget.visible['edit'] = 'invisible'

from AccessControl import ClassSecurityInfo
security = ClassSecurityInfo()


security.declarePublic('at_post_edit_script')
def at_post_edit_script(self):
    """
    """

    def getMyProvider(self):
        pm = getToolByName(self, 'portal_membership')
        hf = pm.getHomeFolder()
        name = pm.getAuthenticatedMember().getUserName()
        res = self.portal_catalog(portal_type='Provider', Creator=name)
        return len(res) > 0 and res[0].getObject() or None

    provider = getMyProvider(self)
    if provider:
        self.setProvider(provider.UID())

RiskAssessmentLink.at_post_edit_script = at_post_edit_script
RiskAssessmentLink.at_post_create_script = RiskAssessmentLink
