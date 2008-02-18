# Add additional fields to the standard content types


import zope.interface

class IGFBContent(zope.interface.Interface):
    """GFBContent
    """

from Products.Archetypes.utils import DisplayList

from Products.ATCountryWidget.Widget import CountryWidget, MultiCountryWidget

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.VocabularyPickerWidget.VocabularyPickerWidget import VocabularyPickerWidget

from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName

# dummy
DUMMY = False
dummy_vocab = ['this', 'is', 'a', 'dummy', 'vocabulary']


class ExtensionFieldMixin:
    def _Vocabulary(self, content_instance, vocab_name):
        if DUMMY:
            return atapi.DisplayList([(x, x) for x in dummy_vocab])
        else:
            pv = getToolByName(content_instance, 'portal_vocabularies')
            VOCAB = getattr(pv, vocab_name, None)
            if VOCAB:
                return VOCAB.getDisplayList(VOCAB)
            else:
                return DisplayList()

    def translationMutator(self, instance):
        return self.getMutator(instance)


class NACEField(ExtensionField, ExtensionFieldMixin, atapi.LinesField):

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'NACE')



class CountryField(ExtensionField, ExtensionFieldMixin, atapi.LinesField):
    
    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'Country')




import zope.component
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender

class GFBTaggingSchemaExtender(object):
    zope.interface.implements(IOrderableSchemaExtender)
    zope.component.adapts(IGFBContent)
    
    # currently (linguaPlone 2.2 unreleased) it is not possible to have langaugeIndependent fields
    # at least not within the schema extender
    # translating an object will lead to 
    #      Module Products.LinguaPlone.browser.translate, line 61, in __call__
    #      Module Products.LinguaPlone.I18NBaseObject, line 145, in addTranslation
    #      AttributeError: translation_mutator


    _fields = [
            NACEField('nace',
                schemata='Sector',
                languageIndependent=True,
                multiValued=True,
                widget=VocabularyPickerWidget(
                    label="NACE Code",
                    description="Pick one or more values by clicking the Add button or using the Quicksearch field below.",
                    vocabulary="NACE",
                    label_msgid='label_nace',
                    description_msgid='help_nace',
                    i18n_domain='plone',
                ),
                translation_mutator="translationMutator",
            ),
            CountryField('country',
                schemata='Other',
                enforceVocabulary=False,
                languageIndependent=True,
                multiValued=True,
                widget=MultiCountryWidget(
                    label="Countries",
                    description='Select one or more countries appropriate for this content',
                    description_msgid='help_country',
                    provideNullValue=1,
                    nullValueTitle="Select...",
                    label_msgid='label_country',
                    i18n_domain='osha',
                ),                
                translation_mutator="translationMutator",
            ),
           
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields

    def getOrder(self, original):
        return original


#NOTE: These methods are called quite frequently, so it pays to optimise
#them.

zope.component.provideAdapter(GFBTaggingSchemaExtender,
                              name=u"gfb.metadata")



# RiskAssessmentLink
class IGFBContentRAL(zope.interface.Interface):
    """ IGFBContentRAL
    """

from Products.RiskAssessmentLink.content.RiskAssessmentLink import RiskAssessmentLink
zope.interface.classImplements(RiskAssessmentLink, IGFBContentRAL)

class GFBTaggingSchemaExtenderRAL(GFBTaggingSchemaExtender):
    
    zope.component.adapts(IGFBContentRAL)

    def getOrder(self, original):
        other = original.get('Other') or list()
        if hasattr(other, 'country'):
            other.remove('country')
        other.insert(3, 'country')
        original['Other'] = other

        sector = original.get('Sector') or list()
        if hasattr(sector, 'nace'):
            sector.remove('nace')
        sector.insert(0, 'nace')
        original['Sector'] = sector

        return original

zope.component.provideAdapter(GFBTaggingSchemaExtenderRAL,
                              name=u"gfb.metadata.ral")


# Provider
class IGFBContentProvider(zope.interface.Interface):
    """ IGFBContentProvider
    """

from Products.RemoteProvider.content.Provider import Provider
zope.interface.classImplements(Provider, IGFBContentProvider)

class GFBTaggingSchemaExtenderProvider(GFBTaggingSchemaExtender):
    
    zope.component.adapts(IGFBContentProvider)
    
    _fields = list()
    
    def getOrder(self, original):
        return original


zope.component.provideAdapter(GFBTaggingSchemaExtenderProvider,
                              name=u"gfb.metadata.provider")