from Products.RiskAssessmentLink.content.RiskAssessmentLink import RiskAssessmentLink_schema as schema
schema['provider'].widget.visible['edit'] = 'invisible'

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
