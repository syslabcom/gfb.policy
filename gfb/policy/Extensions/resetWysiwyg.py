# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


def resetWysiwyg(self):
    pm = getToolByName(self, 'portal_membership')
    f = pm.getMembersFolder()
    for id in f.objectIds('ATFolder'):
        member = pm.getMemberById(id)
        if member:
            member.setMemberProperties({'wysiwyg_editor': 'CKeditor'})
            print "Set Editor for Member: %s" % member.getUserId()
