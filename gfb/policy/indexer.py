from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.interfaces.base import IBaseFolder
from Products.CMFCore.utils import _mergedLocalRoles, getToolByName
from plone.indexer.decorator import indexer


@indexer(IBaseContent)
def getRiskfactors(obj):
    return obj.restrictedTraverse('@@getVocabularyPath')('riskfactors')


@indexer(IBaseContent)
def nace(obj):
    return obj.restrictedTraverse('@@getVocabularyPath')('nace')


@indexer(IBaseFolder)
def editors(obj):
    """ Return a list of users who are editors of this folder.
    Pretty much copied from CatalogTool.allowedRolesAndUsers().
    """
    allowed_roles = ['Editor']
    allowed = {}
    try:
        acl_users = getToolByName(obj, 'acl_users', None)
        if acl_users is not None:
            localroles = acl_users._getAllLocalRoles(obj)
    except AttributeError:
        localroles = _mergedLocalRoles(obj)
    for user, roles in localroles.items():
        for role in roles:
            if role in allowed_roles:
                allowed['user:' + user] = 1
    return list(allowed.keys())
