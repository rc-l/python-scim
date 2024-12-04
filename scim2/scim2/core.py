from .base import Attribute, ResourceBase, ComplexBase
from .datatypes import *
from .helpers import inheritors

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

    class ScimInfo:
        # Note on naming this class, did not pick Metadata, or Schema or variants
        # thereof since these are already keys in the SCIM schema representation
        """Metadata for the SCIM object"""

        # Left name undefined on purpose, should be overridden by subclasses
        endpoint = classproperty(lambda cls: "/" + cls.name + "s")
        schema = classproperty(lambda cls: f'urn:ietf:params:scim:schemas:extension:2.0:{cls.name}')
        id = classproperty(lambda cls: cls.name)
        description = ""

    def dict(self):
        """Convert the object to a dictionary"""
        super_dict = super().dict()
        super_dict['schemas'] = self.list_schemas()
        super_dict['meta']["resourceType"] = self.ScimInfo.name
        super_dict['meta']["location"] = "{basepath}" + self.ScimInfo.endpoint + "/" + super_dict['id']
        return super_dict
    
    @classmethod
    def list_schemas(cls):
        """List the schemas for the ResourceType
        
        This list includes the schemas that this resource extends through inheritence
        """
        schemas = [cls.ScimInfo.schema]
        for base in cls.__bases__:
            # Get the schema from other resource schema classes but not from BaseSchema
            if issubclass(base, BaseSchema) and base != BaseSchema:
                schemas.extend(base.list_schemas())
        # Remove duplicates
        schemas = list(set(schemas))
        return schemas

    @classmethod
    def get_schema(cls):
        """Get the schema representation for the class
        The resource object only needs to get the attributes. Other properties are already
        known by parent.
        
        RFC7643 section 7
        """
        attributes = []
        # Do shallow collection of attributes since schema should only include attributes of the current class
        for k, v in cls._class_schema_attrs(shallow=True).items():
            attrschema = v.get_schema()
            if not "name" in attrschema:
                attrschema["name"] = k
            attributes.append(attrschema)

        schema = {
            "id": cls.ScimInfo.schema,
            "name": cls.ScimInfo.name,
            "description": cls.ScimInfo.description,
            "attributes": attributes,
            "meta": {
                "resourceType": "Schema",
                "location": "{basepath}/Schemas/" + cls.ScimInfo.schema
            }
        }
        return schema
    
    @classmethod
    def resource_type_representation(cls):
        """Generate a resource type representation.

        According to RFC7643 section 6 and in support of RFC7644 section 4."""
        output = dict()
        output['schemas'] = ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"]
        output['meta'] = {}
        output['meta']['resourceType'] = "ResourceType"
        output['meta']['location'] = "{basepath}/ResourceTypes/" + cls.ScimInfo.name
        output['endpoint'] = cls.ScimInfo.endpoint
        output['schema'] = cls.ScimInfo.schema
        output['name'] = cls.ScimInfo.name
        output['id'] = cls.ScimInfo.id

        # Description optional
        try:
            output['description'] = cls.ScimInfo.description
        except AttributeError:
            output['description'] = ""

        # Schema extensions
        # All the schemas that extend this schema
        subclasses = inheritors(cls)
        output['schemaExtensions'] = [
            {
                "schema": s.ScimInfo.schema,
                "required": False
            } 
            for s in subclasses if hasattr(s, 'ScimInfo')
        ]

        return output

class User(BaseSchema):

    class ScimInfo(BaseSchema.ScimInfo):
        name = "User"
        description = "User Account"
        schema = "urn:ietf:params:scim:schemas:core:2.0:User"

    userName = Attribute(String, required=True)

class EnterpriseUser(User):

    class ScimInfo(User.ScimInfo):
        name = "EnterpriseUser"
        description = "Enterprise User Account"
        schema = "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"

