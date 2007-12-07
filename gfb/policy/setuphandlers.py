from Products.CMFCore.utils import getToolByName
import logging, os

basedir = os.path.abspath(os.path.dirname(__file__))
vocabdir = os.path.join(basedir, 'data', 'vocabularies')

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
    quickinst.installProduct('ATVocabularyManager')

    importVocabularies(site)

    index_data = [
            { 'idx_id' : 'nace'
            , 'meta_id' : 'nace'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
          , { 'idx_id' : 'country'
            , 'meta_id' : 'country'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
        ]    

    addProxyIndexes(site, index_data)






def importVocabularies(self):
    logger = logging.getLogger("VocabularyImporter")
    logger.info("Importing Vocabularies")
    vocabs = os.listdir(vocabdir)
    pvm = self.portal_vocabularies
    for vocabname in vocabs:
        vocabpath = os.path.join(vocabdir, vocabname)
        if vocabname.endswith('.vdex'):
            fh = open(vocabpath, "r")
            data = fh.read()
            fh.close()
            vocabname = vocabname[:-5]
            if vocabname in pvm.objectIds(): continue
            pvm.invokeFactory('VdexFileVocabulary', vocabname)
            pvm[vocabname].importXMLBinding(data)
            logger.info("VDEX Import of %s" % vocabname)
    
        elif vocabname.endswith('.dump'):
            fh = open(vocabpath, "r")
            data = fh.read()
            fh.close()
            vocabname = vocabname[:-5]
            if vocabname in pvm.objectIds(): continue
            vocabstruct = cPickle.loads(data)
            createSimpleVocabs(pvm, vocabstruct)
            logger.info("Dump Import of %s" % vocabname)
            

def addProxyIndexes(self, index_data):
    logger = logging.getLogger("ProxyIndex")
    logger.info("Adding Proxy Indexes")

    VALUE_EXPR = "python:object.getField('%(meta_id)s').getAccessor(object)()"

    cat = getToolByName(self, 'portal_catalog')
    available = cat.indexes()
    for data in index_data:
        if data['idx_id'] in available:
            continue
        extra = data['extra']
        extra['value_expr'] = VALUE_EXPR %{'meta_id': data['meta_id']}
        extra['key1'] = "indexed_attrs"
        extra['value1'] = "proxy_value"
        logger.info("Adding Proxy Index %s" % data['idx_id'])
        cat.manage_addProduct['ProxyIndex'].manage_addProxyIndex(
            id=data['idx_id'],
            extra=extra)            
