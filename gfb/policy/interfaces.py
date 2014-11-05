from zope.interface import Interface


class IVocabularyUtility(Interface):
    """A utility that returns a vocabulary dict"""
    def getVocabularyDict():
        """return the dict"""


class INewsListing(Interface):
    pass
