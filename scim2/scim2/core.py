from .base import Attribute, ResourceBase, ComplexBase
from .datatypes import *

class MetaData(ComplexBase):
    """Metadata for a resource"""
    
    resourceType = Attribute(String, mutability="readOnly", caseExact=True)
    created = Attribute(DateTime)
    lastModified = Attribute(DateTime)
    location = Attribute(String)
    version = Attribute(String)


class BaseSchema(ResourceBase):
    """Base class for schema objects"""
    
    id = Attribute(String, required=True)
    externalId = Attribute(String)
    meta = Attribute(MetaData)


class User(BaseSchema):
    username = Attribute(String)
    emails = Attribute(String, multivalued=True)