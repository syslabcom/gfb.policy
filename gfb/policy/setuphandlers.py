from Products.CMFCore.utils import getToolByName
import logging, os
from zope.component import getMultiAdapter, getUtility
from simplon.plone.ldap.engine.schema import LDAPProperty
from simplon.plone.ldap.engine.interfaces import ILDAPConfiguration
from plone.portlets.constants import CONTEXT_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY
from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.app.portlets.portlets import navigation, news, classic, events, search
from plone.portlet.static import static as staticportlet
from gfb.policy.config import PROVIDER_ROLE, INSTALL_LDAP
from Products.RiskAssessmentLink.config import ADD_CONTENT_PERMISSIONS as RAL_PERMISSIONS
from Products.CMFCore.permissions import AddPortalContent, ReviewPortalContent


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
    # This needs to run before Riskassessment Link, otherwise a broken vocab will be imported
    # archgenxml2b6 currently only can import vdex and not vdexfiles
    importVocabularies(site)

    quickinst.installProduct('RiskAssessmentLink')
    quickinst.installProduct('ProxyIndex')
    quickinst.installProduct('VocabularyPickerWidget')
    quickinst.installProduct('Clouseau')
    quickinst.installProduct('DataGridField')
    quickinst.installProduct('gfb.theme')
    quickinst.installProduct('simplon.plone.ldap')
    quickinst.installProduct('TextIndexNG3')
    quickinst.installProduct('collective.portlet.tal')
    quickinst.installProduct('plone.portlet.collection')
    quickinst.installProduct('plone.portlet.static')
    quickinst.installProduct('collective.portlet.feedmixer')
    quickinst.installProduct('syslabcom.filter')


    index_data = [
            { 'idx_id' : 'nace'
            , 'meta_id' : 'nace'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
        ]

    addProxyIndexes(site, index_data)


    addExtraIndexes(site)


    addCatalogMetadata(site, ['getProvider_category'])

    props = [
#        dict(id='localityName', value='', type='string', plone_name='Locality', multi_valued=False),
#        dict(id='stateOrProvinceName', value='', type='string', plone_name='Country', multi_valued=False),
#        dict(id='postalAddress', value='', type='string', plone_name='Address', multi_valued=False),
#        dict(id='telephoneNumber', value='', type='string', plone_name='Telephone', multi_valued=False),
#        dict(id='facsimileTelephoneNumber', value='', type='string', plone_name='Fax', multi_valued=False)
        ]
    addMemberdataProperties(site, props)
    configurePortal(site)
    setupContent(site)
    #setupSecurity(site)
    configureCountryTool(site)

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
    logger = logging.getLogger("gfb policy VocabularyImporter")
    logger.info("Importing Vocabularies for gfb")
    vocabs = os.listdir(vocabdir)
    pvm = self.portal_vocabularies
    for vocabname in vocabs:
        vocabpath = os.path.join(vocabdir, vocabname)
        logger.info("Trying %s" % vocabpath)
        if vocabname.endswith('.vdex'):
            fh = open(vocabpath, "r")
            data = fh.read()
            fh.close()
            vocabname = vocabname[:-5]
            if vocabname in pvm.objectIds():
                logger.info("Vocabulary already in place")
                continue
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
        else:
            logger.info("No vocabfile found")

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

def addExtraIndexes(self):
    logger = logging.getLogger("ExtraIndexes")
    logger.info("Adding Extra Indexes")

    cat = getToolByName(self, 'portal_catalog')
    available = cat.indexes()
    
    if 'getTargetLanguage' not in available:
        logger.info('Adding KeywordIndex getTarget_language')
        cat.manage_addProduct['PluginIndexes'].manage_addKeywordIndex(id='getTargetLanguage', extra={'indexed_attrs': 'getTargetLanguage'})

    if 'getCountry' not in available:
        logger.info('Adding KeywordIndex Country')
        cat.manage_addProduct['PluginIndexes'].manage_addKeywordIndex(id='getCountry', extra={'indexed_attrs': 'getCountry'})   

def addCatalogMetadata(site, metadata):
    logger = logging.getLogger("CatalogMetadata")
    logger.info("Adding Catalog Metadata")

    cat = getToolByName(site, 'portal_catalog')
    for md in metadata:
        if md not in cat.schema():
            cat.manage_addColumn(md)

#################################
# PORTLET MANAGEMENT & CONTENT

def _blockPortlets(context, manager, CAT, status):
    portletManager = getUtility(IPortletManager, name=manager)
    assignable = getMultiAdapter((context, portletManager,), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CAT, status)


def portletAssignmentPortal(context):
    """ assign portlets as they should be set on the portal root """
    path = "/"
    left = assignment_mapping_from_key(context, 'plone.leftcolumn', CONTEXT_CATEGORY, path)
    right = assignment_mapping_from_key(context, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
    for x in list(left.keys()):
        del left[x]
    for x in list(right.keys()):
        del right[x]
    left['navtree'] = navigation.Assignment()
    left['events'] = events.Assignment()
    right['news'] = news.Assignment()

def portletAssignmentDB(context):
    """ assign portlets as they should be set on the database folder """
    path = '/'.join(context.getPhysicalPath())
    left = assignment_mapping_from_key(context, 'plone.leftcolumn', CONTEXT_CATEGORY, path)
    right = assignment_mapping_from_key(context, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
    for x in list(right.keys()):
        del right[x]
    _blockPortlets(context, 'plone.leftcolumn', CONTEXT_CATEGORY, True)
    _blockPortlets(context, 'plone.rightcolumn', CONTEXT_CATEGORY, True)

def portletAssignmentRAL(context):
    right = context.restrictedTraverse('++contenttypeportlets++plone.rightcolumn+RiskAssessmentLink')
    if 'ral_details' not in right.keys():
        right['ral_details'] = classic.Assignment(template='portlet_riskassessmentlink_details', macro='portlet')

def configurePortal(site):
    """ Config steps that cannot be done by generic setup yet """
    pmembership = getToolByName(site, 'portal_membership')
    pmembership.memberareaCreationFlag = True

    # Members have the right to publish their own content
    # So we set the Review portal content permission on the Owner role on the Members folder
    Members = site.Members
    Members.manage_permission(ReviewPortalContent, ['Owner'], acquire=1)

    # Add the help page
    if 'dashboard_help' not in site.objectIds():
        site.invokeFactory('Document', 'dashboard_help')
        dh = getattr(site, 'dashboard_help')
        dh.setTitle('Hilfe')
        dh.setDescription('Hilfe zum Umgang mit der GFB Site')
        pw = getToolByName(site, 'portal_workflow')
        pw.doActionFor(dh, 'publish')

def setupContent(site):
    """ Adds the db folder and registers the filter view as default as well as the portlets """
    # enable addition of large folders
    getattr(site.portal_types, 'Large Plone Folder').global_allow = True
    if 'db' not in site.objectIds():
        _ = site.invokeFactory('Large Plone Folder', 'db')
    db = getattr(site, 'db')
    db.setTitle('Datenbank')
    db.setLayout('riskassessmentlink_db_view')
    try:
        pwt = getToolByName(site, 'portal_workflow')
        pwt.doActionFor(db, 'publish')
    except: pass

    portletAssignmentPortal(site)
    portletAssignmentDB(db)
    portletAssignmentRAL(site)

#def setupSecurity(site):
#    """ Adds role and permission for the providers """
#    site._addRole(PROVIDER_ROLE)
#    db = getattr(site, 'db')
#    db.manage_role(PROVIDER_ROLE, permissions=[RAL_PERMISSIONS['RiskAssessmentLink'], AddPortalContent])



def configureCountryTool(site):
    """ Adds the relevant countries to the countrytool """
    ct = getToolByName(site, 'portal_countryutils')
    ct.manage_countries_reset()
    ct.manage_countries_addArea('Europa')
    ct.manage_countries_addCountryToArea('Europa', ['DK','FI','FR','IT','NL','PT','ES','GB','IS','IE','LI','LU','NO','SE','AT','DE','CH','MT','BE','CZ','HU','PL','RO','SK','HR','BG','BA','GR','SI','MK','EE','LV','LT'])
    ct.manage_countries_sortArea('Europa')
