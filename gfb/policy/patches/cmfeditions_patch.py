from Acquisition import aq_base
from Products.CMFEditions.ArchivistTool import ArchivistTool
from Products.CMFEditions.CopyModifyMergeRepositoryTool import CopyModifyMergeRepositoryTool
from Products.CMFCore.utils import getToolByName
from Products.CMFUid.interfaces import IUniqueIdAnnotation
from StringIO import StringIO
from cPickle import Pickler, Unpickler


def _cloneByPickle(self, obj):
    """Returns a deep copy of a ZODB object, loading ghosts as needed.
    """
    modifier = getToolByName(self, 'portal_modifier')
    callbacks = modifier.getOnCloneModifiers(obj)
    if callbacks is not None:
        pers_id, pers_load, inside_orefs, outside_orefs = callbacks[0:4]
    else:
        inside_orefs, outside_orefs = (), ()

    stream = StringIO()
    p = Pickler(stream, 1)
    if callbacks is not None:
        p.persistent_id = pers_id
    cmf_uid = getattr(obj, 'cmf_uid', None)
    if IUniqueIdAnnotation.providedBy(cmf_uid):
        setattr(obj, 'cmf_uid', cmf_uid())
    # import pdb; pdb.set_trace( )
    try:
        p.dump(aq_base(obj))
    except TypeError:
        # just try again, this then seems to work
        # WTF?
        p.dump(aq_base(obj))
    approxSize = stream.tell()
    stream.seek(0)
    u = Unpickler(stream)
    if callbacks is not None:
        u.persistent_load = pers_load
    return approxSize, u.load(), inside_orefs, outside_orefs

ArchivistTool._cloneByPickle = _cloneByPickle


def _recursiveSave(self, obj, app_metadata, sys_metadata, autoapply):
    # prepare the save of the originating working copy
    portal_archivist = getToolByName(self, 'portal_archivist')
    prep = portal_archivist.prepare(obj, app_metadata, sys_metadata)

    # set the originator of the save operation for the referenced
    # objects
    if sys_metadata['originator'] is None:
        clone = prep.clone.object
        sys_metadata['originator'] = "%s.%s.%s" % (prep.history_id,
                                                   clone.version_id,
                                                   getattr(clone, 'location_id', ''))

    # What comes now is the current hardcoded policy:
    #
    # - recursively save inside references, then set a version aware
    #   reference
    # - on outside references only set a version aware reference
    #   (if under version control)
    inside_refs = map(lambda original_refs, clone_refs:
                      (original_refs, clone_refs.getAttribute()),
                      prep.original.inside_refs, prep.clone.inside_refs)
    for orig_ref, clone_ref in inside_refs:
        self._recursiveSave(orig_ref, app_metadata, sys_metadata,
                            autoapply)
        clone_ref.setReference(orig_ref, remove_info=True)

    outside_refs = map(lambda oref, cref: (oref, cref.getAttribute()),
                       prep.original.outside_refs, prep.clone.outside_refs)
    for orig_ref, clone_ref in outside_refs:
        clone_ref.setReference(orig_ref, remove_info=True)

    portal_archivist.save(prep, autoregister=autoapply)

    # just to ensure that the working copy has the correct
    # ``version_id``
    prep.copyVersionIdFromClone()

CopyModifyMergeRepositoryTool._recursiveSave = _recursiveSave
