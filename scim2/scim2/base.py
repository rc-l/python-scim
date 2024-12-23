from copy import deepcopy
import json

from .datatypes import DataTypeBase
from .datatypes import *
from .helpers import classproperty

class Attribute():
    """Base class for all attributes

    RFC 7643 section 2
    """
    def __init__(self, value_type, **kwargs):
        self.multivalued = kwargs.get("multivalued", False)
        self._type = value_type
        self.complex = issubclass(self._type, Base)
        self.reset()

        # Remaining attribute properties
        self.description = kwargs.get("description", "")
        self.required = kwargs.get("required", False)
        self.mutability = kwargs.get("mutability", "readWrite")
        assert self.mutability in ("readOnly", "readWrite", "immutable", "writeOnly")
        self.caseExact = kwargs.get("caseExact", False)
        self.returned = kwargs.get("returned", "default")
        assert self.returned in ("always", "never", "default", "request")
        self.uniqueness = kwargs.get("uniqueness", "none")
        assert self.uniqueness in ("none", "server", "global")
        # Only set name if it differs from the attribute name in the parent
        self.name = kwargs.get("name", None)
        # TODO: implement referenceTypes

        # Check if type is valid
        if not issubclass(self._type, DataTypeBase) and not self.complex:
            raise TypeError("Must provde a valid data type (subclass of DataType or a Complex)")

    def reset(self):
        """Reset the attribute to its default value"""
        if not self.multivalued:
            if self.complex:
                self._value = [self._type()]
            else:
                self._value = [None]
        else:
            self._value = []

    def dict(self):
        """Return dictionary representation of the attribute"""
        if self.complex:
            # Cascade down to the attributes making up the complex attribute
            if self.multivalued:
                return [v.dict() for v in self._value]
            else:
                return self._value[0].dict()
        else:
            if self.multivalued:
                return [self._type.prep_json(v) for v in self._value]
            else:
                return self._type.prep_json(self._value[0])
    
    def load(self, value):
        """Populate attribute values based of json or dictionary representation"""
        if self.complex:
            if self.multivalued:
                if not isinstance(value, list):
                    raise TypeError("Value must be a list")
                self._value = [self._type().load(v) for v in value]
            else:
                self._value = [self._type().load(value)]
        else:
            self.value = value

    # Get and set for the value of the attribute
    @property
    def value(self):
        if not self.multivalued:
            return self._value[0]
        return self._value
    
    @value.setter
    def value(self, value):
        if not self.multivalued:
            # Convert the value to the correct type
            self._value[0] = self._type.convert(value)
        elif isinstance(value, list):
            try:
                self._value = [self._type.convert(v) for v in value]
            except TypeError:
                raise TypeError("All values in the list must be of the correct type")
        else:
            raise TypeError("Value must be a list if multivalued")
    
    def __str__(self):
        dict_value = self.dict()
        # Only dump to json if the value is a dictionary or list
        # Otherwise primitive values end up with quotes like '"value"'
        if type(dict_value) in (dict, list):
            return json.dumps(dict_value)
        else:
            return str(dict_value)

    def get_schema(self):
        """Get the schema representation for the attribute
        
        RFC7643 section 7
        """
        schema = {
            "required": self.required,
            "mutability": self.mutability,
            "returned": self.returned,
            "uniqueness": self.uniqueness,
            "description": self.description,
            "multiValued": self.multivalued,
            "type": self._type.name
        }
        if self.complex:
            schema["subAttributes"] = self._type.get_schema()

        if isinstance(self._type, String):
            schema["caseExact"] = self.caseExact
        if self.name:
            schema["name"] = self.name

        return schema
        

class Base():
    """Base class SCIM objects Resource, Extension, Complex"""

    def __init__(self, scim_repr=None):
        self._original_repr = None

        # Copy all the SCIM object such that two instances don't share the same attributes
        # Without copying a change in object_a will reflect also in object_b. Highly undesirable!
        for k, v in self._class_schema_attrs().items():
            setattr(self, k, deepcopy(v))

        self.load(scim_repr)

    @property
    def _schema_attrs(self):
        """Get all the attributes that are part of the schema"""
        return self._filter_schema_attrs(vars(self))

    @classmethod
    def _class_schema_attrs(cls, shallow=False):
        """Get all the attributes that are part of the schema to be used for class not class instance
        
        Args:
            shallow (bool): If True, only return the schema attributes of the current

        Returns:
            dict: A dictionary of schema attributes
        """
        # TODO: why did I split this into separate methods for class and class instance?
        # Get attributes of superclass
        inherited_attrs = {}
        if not shallow:
            # Shallow determines if superclass attributes are required to be returned
            for base in cls.__bases__:
                if issubclass(base, Base):
                    inherited_attrs.update(base._class_schema_attrs())

        # Get attributes of current class
        own_attrs = cls._filter_schema_attrs(vars(cls))

        # Merge the two sets of attributes, with the subclass attributes taking precedence
        return {**inherited_attrs, **own_attrs}

    @staticmethod
    def _filter_schema_attrs(attrs):
        """Filter a dictionary of attributes to only include schema attributes"""
        output = {}
        for k, v in attrs.items():
            if isinstance(v, Attribute):
                output[k] = v
        return output

    def __str__(self):
        return str(self.dict())
    
    # Overide the getattribute, setattr and delattr methods to handle the attributes
    # This is done to make the attributes accessible as if they were normal attributes
    # instead of getting the Attribute object you now get the value of the attribute
    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, Attribute):
            return attr.value
        return attr
    
    def __setattr__(self, name, value):
        try:
            attr = super().__getattribute__(name)
        except AttributeError:
            attr = None
        # If the attribute is an Attribute object, set the value of the attribute
        # Exception is if the value is an Attribute object as well. Then the new
        # attribute object replaces the old one. This is required during initialization
        # of the Resource object.
        if isinstance(attr, Attribute) and not isinstance(value, Attribute):
            attr.value = value
        else:
            super().__setattr__(name, value)
        
    def __delattr__(self, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, Attribute):
            attr.reset()
        else:
            super().__delattr__(name)

    def get_attribute(self, name):
        """Returns the attribute object not the value"""
        return super().__getattribute__(name)

    def dict(self):
        """Return dictionary representation of the resource"""
        output = {}
        for k, v in self._schema_attrs.items():
            value = v.dict()
            # Do not include attributes that have no value, a complex type for which all subattributes have no value, or multivalue with length 0
            if value not in [None, {}, []]:
                output[k] = value
        return output

    def load(self, repr):
        """Populate attribute values based of json or dictionary representation"""
        if repr and isinstance(repr, str):
            try:
                # Turn json to dict
                repr = json.loads(repr)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON representation")
        elif repr and not isinstance(repr, dict):
            raise ValueError("Invalid type for scim_repr")
        if repr:
            for k, v in repr.items():
                if k in self._schema_attrs:
                    self._schema_attrs[k].load(v)
            self._original_repr = repr
        return self

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
        return attributes

   
class Complex(Base):
    """Base class for complex attribute content"""
    # Name of the data type RFC7643 section 2.3
    name = "Complex"
    
    @classmethod
    def validate(cls, value):
        """Validate the complex attribute is of the correct type"""
        return isinstance(value, cls)
    
    @classmethod
    def convert(cls, value):
        """Convert the complex attribute to the correct type"""
        if isinstance(value, cls):
            return value
        elif isinstance(value, dict):
            return cls(value)
        else:
            raise ValueError("Cannot convert value to complex attribute")


class ResourceBase(Base):
    """Base class for SCIM Resources and Extensions"""

    class ScimInfo:
        # Note on naming this class, did not pick Metadata, or Schema or variants
        # thereof since these are already keys in the SCIM schema representation
        """Metadata for the SCIM object"""

        # Left name undefined on purpose, should be overridden by subclasses
        id = classproperty(lambda cls: cls.name)
        description = ""

    @classmethod
    def get_schema(cls):
        """Get the schema representation for the class
        The resource object only needs to get the attributes. Other properties are already
        known by parent.
        
        RFC7643 section 7
        """
        # Collect attributes
        attributes = super().get_schema()

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


class Extension(ResourceBase):
    """Base class for SCIM extensions"""

    class ScimInfo(ResourceBase.ScimInfo):
        # Note on naming this class, did not pick Metadata, or Schema or variants
        # thereof since these are already keys in the SCIM schema representation
        """Metadata for the SCIM object"""

        # Left name undefined on purpose, should be overridden by subclasses
        id = classproperty(lambda cls: cls.name)
        schema = classproperty(lambda cls: f'urn:ietf:params:scim:schemas:extension:2.0:{cls.name}')
        description = ""


class MetaData(Complex):
    """Metadata for a resource"""
    
    resourceType = Attribute(String, mutability="readOnly", caseExact=True)
    created = Attribute(DateTime)
    lastModified = Attribute(DateTime)
    location = Attribute(String)
    version = Attribute(String)


class ResourceType(ResourceBase):
    """Base class for SCIM Resource Types which form the root resources of the SCIM API"""

    id = Attribute(String, required=True)
    externalId = Attribute(String)
    meta = Attribute(MetaData)

    class ScimInfo(ResourceBase.ScimInfo):
        # Note on naming this class, did not pick Metadata, or Schema or variants
        # thereof since these are already keys in the SCIM schema representation
        """Metadata for the SCIM object"""

        # Left name undefined on purpose, should be overridden by subclasses
        endpoint = classproperty(lambda cls: "/" + cls.name + "s")
        schema = classproperty(lambda cls: f'urn:ietf:params:scim:schemas:custom:2.0:{cls.name}')

    def __init__(self, *args, **kwargs):
        # Instatiate extensions
        for k, v in self.extensions:
            setattr(self, k, v())

        super().__init__(*args, **kwargs)

    def dict(self):
        """Convert the object to a dictionary"""
        super_dict = super().dict()

        # Add metadata
        super_dict['schemas'] = [self.ScimInfo.schema] + self.extension_schemas
        if "meta" not in super_dict:
            super_dict['meta'] = {}
        super_dict['meta']["resourceType"] = self.ScimInfo.name
        super_dict['meta']["location"] = "{basepath}" + self.ScimInfo.endpoint + "/" + super_dict['id']

        # Add extensions
        for k, v in self.extensions:
            # Get the dict of the instantiated extension object 
            # Going for v directly would get use the uninstantiated class
            extension_dict = self.__getattribute__(k).dict()

            # Add the dict to the super_dict
            # This needs to be in it's own namespace based on the schema name according to the SCIM spec
            if extension_dict:
                super_dict[v.ScimInfo.schema] = extension_dict
        return super_dict
    
    def load(self, repr):
        # Do normal load first, this changes the state of self
        super().load(repr)
        extension_key_mapping = {v.ScimInfo.schema: k for k, v in self.extensions}

        # Load extensions
        if self._original_repr:
            # Loop over all the keys in the original representation
            for k, v in self._original_repr.items():
                # Check if the key is an extension
                if k in extension_key_mapping:
                    # Get the extension key
                    extension_key = extension_key_mapping[k]
                    # Load the extension
                    self.__getattribute__(extension_key).load(v)

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
        output['schemaExtensions'] = [
            {
                "schema": e,
                "required": False
            } 
            for e in cls.extension_schemas
        ]

        return output

    @classproperty
    def extensions(cls):
        """List all the extensions for the resource type"""
        # Get all variables in class and filter for the ones that are subclasses of Extension
        return [(k, v) for k, v in vars(cls).items() if type(v) is type and issubclass(v, Extension)]
    
    @classproperty
    def extension_schemas(cls):
        """List all the extension schemas for the resource type"""
        return [v.ScimInfo.schema for k, v in cls.extensions]