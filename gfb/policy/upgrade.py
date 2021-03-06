from Products.CMFCore.interfaces import IWorkflowDefinition
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.Worklists import Worklists
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


def reload_actions(self):
    self.runImportStepFromProfile('profile-gfb.policy:default', 'actions')


def set_folder_order(self):
    pc = getToolByName(self, 'portal_catalog')
    folders = pc.searchResults(portal_type="Folder")
    for folder_brain in folders:
        folder = folder_brain.getObject()
        if folder.getId() == 'Members':
            continue
        folder.orderObjects("creation_date", reverse=True)
        folder.setOrdering("prepend")
    logger = logging.getLogger("gfb.policy")
    logger.info("Set order for folder items")


def configure_versioning_and_diffing(self):
    self.runImportStepFromProfile('profile-gfb.policy:default', 'repositorytool')
    diff_tool = getToolByName(self, 'portal_diff')
    if "RichDocument" not in diff_tool.listDiffTypes():
        diff_tool.setDiffField("RichDocument", "any", "Compound Diff for AT types")


def add_worklists(self):
    wft = getToolByName(self, 'portal_workflow')
    for wf in wft.objectValues():
        if not IWorkflowDefinition.providedBy(wf):
            continue
        if not getattr(wf, 'worklists', None):
            wf._addObject(Worklists('worklists'))
