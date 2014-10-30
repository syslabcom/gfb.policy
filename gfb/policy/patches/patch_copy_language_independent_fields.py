from Products.Archetypes.utils import shasattr
from Products.LinguaPlone.utils import LanguageIndependentFields
from Products.Archetypes.mimetype_utils import getDefaultContentType


# Reason for this patch
# Fixes bug from ticket #10843
# When lang-independent fields are copied over, the usual call of
# setDefaults() of Products.Archetypes.Schema.__init__.BasicSchema is
# missing.
# Since we have the brain-dead situation of a language-independent
# text field in RiskAssessmentLink, we need to make sure that when the
# mutator for the translation is called, at least the correct mimetype
# is passed in. Otherwise the transform of the value will incorrectly
# escape HTML characters, since it would not know it should render HTML


def copyField(self, field, translation):
    accessor = field.getEditAccessor(self.context)
    if not accessor:
        accessor = field.getAccessor(self.context)
    if accessor:
        data = accessor()
    else:
        data = field.get(self.context)
    mutator = field.getMutator(translation)
    # if field.__name__ == 'remarks':
    #     import pdb; pdb.set_trace( )
    if mutator is not None:
        # Protect against weird fields, like computed fields
        kw = {}
        if shasattr(field, 'default_content_type'):
            # specify a mimetype if the mutator takes a
            # mimetype argument
            # if the schema supplies a default, we honour that,
            # otherwise we use the site property
            default_content_type = field.default_content_type
            if default_content_type is None:
                default_content_type = getDefaultContentType(field)
            kw['mimetype'] = default_content_type

        mutator(data, **kw)
    else:
        field.set(translation, data)


LanguageIndependentFields.copyField = copyField
