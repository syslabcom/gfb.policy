from Products.CMFCore.utils import getToolByName

    
def importVarious(context):
    """Miscellanous steps import handle
    """
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('gfb.policy_various.txt') is None:
        return

    site=context.getSite()
    quickinst = getToolByName(site, 'portal_quickinstaller')
    quickinst.installProduct('ATCountryWidget')
    quickinst.installProduct('AddRemoveWidget')
    quickinst.installProduct('CMFPlacefulWorkflow')
    quickinst.installProduct('Marshall')
    quickinst.installProduct('PloneHelpCenter')
    quickinst.installProduct('UserAndGroupSelectionWidget')
    quickinst.installProduct('plone.app.iterate')
    quickinst.installProduct('RiskAssessmentLink')

    
