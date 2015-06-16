# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName

# Note: this ExternalMethod is used in the Members folder
# It is called via a hook if a new member folder is created
# The script MUST be named notifyMemberAreaCreated


def notifyMemberAreaCreated(self, **args):
    pm = getToolByName(self, 'portal_membership')
    member = pm.getAuthenticatedMember()

    hf = pm.getHomeFolder()
    if not member.getProperty('is_expert_author', False):
        if hf is not None:
            if not hf.hasProperty('layout'):
                hf._setProperty('layout', '@@workingarea', 'string')
            else:
                hf._updateProperty('layout', '@@workingarea')

    member.setMemberProperties({'wysiwyg_editor': 'CKeditor'})
    if hf is not None:
        hf.manage_permission(
            permission_to_manage="Change local roles",
            roles=['Manager'], acquire=0)
