from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
import logging


def fixGenericSetup(self):
    logger = logging.getLogger("fixGenericSetup")
    logger.info("Fixing Generic Setup")

    gs = getToolByName(self, 'portal_setup')
    view = self.restrictedTraverse('@@manage_importsteps')
    invalid_steps = view.invalidSteps()
    ids = [x['id'] for x in invalid_steps]
    gs.manage_deleteImportSteps(ids)
    logger.info("Removed %d invalid import steps" % len(invalid_steps))
    
    view = self.restrictedTraverse('@@manage_exportsteps')
    invalid_steps = view.invalidSteps()
    ids = [x['id'] for x in invalid_steps]
    gs.manage_deleteExportSteps(ids)
    logger.info("Removed %d invalid export steps" % len(invalid_steps))


def configureLanguageTool(self):
    plt = getToolByName(self, 'portal_languages')
    settings = {'use_path_negotiation': 1,
        'use_cookie_negotiation': 1,
        'display_flags': 1,
        'force_language_urls': 0,
        'start_neutral': 0,
        'set_cookie_everywhere': 0,
        'use_subdomain_negotiation': 0,
        'use_content_negotiation': 0,
        'use_request_negotiation': 1,
        'authenticated_users_only': 0,
        'use_combined_language_codes': 0,
        'allow_content_language_fallback': 1,
        'use_cctld_negotiation': 0}
    for k, v in settings.items():
        setattr(plt, k, v)


def migrateGlossary(self):
    """Migrate the PloneHelpCentre Definitions to
    PloneGlossary Glossary definitions"""
    pc = getToolByName(self, 'portal_catalog')
    definitions = pc.searchResults(Type="Definition")
    portal = getSite()
    glossary = portal.de.service.glossar.glossary
    for definition in definitions:
        glossary.invokeFactory(
            type_name="PloneGlossaryDefinition",
            id=definition.id,
        )
        new_definition = glossary[definition.id]
        new_definition.setTitle(definition.Title)
        new_definition.setDefinition(definition.Description)
