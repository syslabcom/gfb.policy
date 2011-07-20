from Products.Archetypes.interfaces.base import IBaseContent
from plone.indexer.decorator import indexer


@indexer(IBaseContent)
def getRiskfactors(obj):
    return obj.restrictedTraverse('@@getVocabularyPath')('riskfactors')

@indexer(IBaseContent)
def nace(obj):
    return obj.restrictedTraverse('@@getVocabularyPath')('nace')
