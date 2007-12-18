from Products.CMFCore.utils import getToolByName
import logging, os
from zope.component import getUtility
from simplon.plone.ldap.engine.schema import LDAPProperty
from simplon.plone.ldap.engine.interfaces import ILDAPConfiguration


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
    quickinst.installProduct('ATVocabularyManager')
    quickinst.installProduct('RiskAssessmentLink') 
    quickinst.installProduct('ProxyIndex')
    quickinst.installProduct('VocabularyPickerWidget')
    quickinst.installProduct('Clouseau')
    quickinst.installProduct('DataGridField')
    quickinst.installProduct('gfb.theme')

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

    addCatalogMetadata(site, ['Category'])

    props = [
        dict(id='localityName', value='', type='string', plone_name='Locality', multi_valued=False),
        dict(id='stateOrProvinceName', value='', type='string', plone_name='Country', multi_valued=False),
        dict(id='postalAddress', value='', type='string', plone_name='Address', multi_valued=False),
        dict(id='telephoneNumber', value='', type='string', plone_name='Telephone', multi_valued=False),
        dict(id='facsimileTelephoneNumber', value='', type='string', plone_name='Fax', multi_valued=False)
        ]
    addMemberdataProperties(site, props)
    


def addMemberdataProperties(site, props):
    logger = logging.getLogger("MemberdataProperties")
    logger.info("Adding Memberdata Properties")

    pm = getToolByName(site, 'portal_memberdata')
    config=getUtility(ILDAPConfiguration)
    availableldapprops = [x.ldap_name for x in config.schema.values()]
    for prop in props:
        if not pm.hasProperty(prop['id']):
            pm._setProperty(prop['id'], prop['value'], prop['type'])     
        if prop['id'] not in availableldapprops:
            logger.info("adding %s" % prop['id'])
            config.schema.addItem(LDAPProperty(
                                       ldap_name=prop['id'],
                                       plone_name=prop['plone_name'], 
                                       description=prop['id'],
                                       multi_valued=prop['multi_valued']))
        else:
            logger.info("not adding %s" % prop['id'])
            logger.info(availableldapprops)


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
            
            
    # import the simple vocablaries from zexp
    if 'RiskAssessmentContents' not in pvm.objectIds():
        RAC = os.path.join(basedir, 'data', 'RiskAssessmentContents.zexp')
        pvm._importObjectFromFile(RAC, verify=False)

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


def addCatalogMetadata(site, metadata):
    logger = logging.getLogger("CatalogMetadata")
    logger.info("Adding Catalog Metadata")

    cat = getToolByName(site, 'portal_catalog')
    for md in metadata:
        if md not in cat.schema():
            cat.manage_addColumn(md)
            