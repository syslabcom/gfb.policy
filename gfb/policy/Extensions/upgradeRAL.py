from Products.CMFCore.utils import getToolByName

def upgrade(self):
    """ set values in the replaced fields """
    pc = getToolByName(self, "portal_catalog")
    res = pc(portal_type="RiskAssessmentLink")
    for r in res:
        o = r.getObject()
        print "i got:", o.absolute_url()
        dateOfEditing = o.getDateOfEditing()
        o.setEffectiveDate(dateOfEditing)
        workplace = o.getWorkplace()
        wps = tuple([dict(Keywords=x['Workplace']) for x in workplace])
        o.setAdditionalKeywords(wps)
        o.reindexObject()

    return "finished"