from Products.CMFCore.utils import getToolByName
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
    