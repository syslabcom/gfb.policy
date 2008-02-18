from Products.CMFCore.utils import getToolByName

def notifyMemberAreaCreated(self, **args):
    pm = getToolByName(self, 'portal_membership')
    hf = pm.getHomeFolder()

    if hf is not None:
        if not hf.hasProperty('layout'):
            hf._setProperty('layout', '@@workingarea', 'string')
        else:
            hf._updateProperty('layout', '@@workingarea')
