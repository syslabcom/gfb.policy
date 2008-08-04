import patches

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('gfb.policy.utils').declarePublic('logit')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
