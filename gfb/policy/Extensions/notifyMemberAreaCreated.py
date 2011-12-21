# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName

# Note: this ExternalMethod is used in the Members folder
# It is called via a hook if a new member folder is created
# The script MUST be named notifyMemberAreaCreated

def notifyMemberAreaCreated(self, **args):
    pm = getToolByName(self, 'portal_membership')
    hf = pm.getHomeFolder()

    if hf is not None:
        if not hf.hasProperty('layout'):
            hf._setProperty('layout', '@@workingarea', 'string')
        else:
            hf._updateProperty('layout', '@@workingarea')

    member = pm.getAuthenticatedMember()
    member.setMemberProperties({'wysiwyg_editor': 'CKeditor'})
    hf.manage_permission(permission_to_manage="Change local roles", roles=['Manager'], acquire=0)
