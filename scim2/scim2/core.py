from .base import Attribute, ResourceBase, ComplexBase
from .datatypes import *

class classproperty:
    def __init__(self, func):
        self.fget = func
    def __get__(self, instance, owner):
        return self.fget(owner)

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

    @classproperty
    def _info_name(cls):
        """Name of the schema"""
        return cls.__name__
    
    @classproperty
    def _info_location(cls):
        """Location of the resource on the server"""
        # Leaving basepath a placeholder for later formatting
        return "{basepath}/" + cls.__name__

    def dict(self):
        """Convert the object to a dictionary"""
        super_dict = super().dict()
        super_dict['meta']["resourceType"] = self._info_name
        super_dict['meta']["location"] = self._info_location
        return super_dict


class User(BaseSchema):

    username = Attribute(String)
    emails = Attribute(String, multivalued=True)