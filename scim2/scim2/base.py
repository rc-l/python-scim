from copy import deepcopy
import json

from .datatypes import DataTypeBase, String

class Attribute():
    """Base class for all attributes

    RFC 7643 section 2
    """
    def __init__(self, value_type, **kwargs):
        self.multivalued = kwargs.get("multivalued", False)
        self._type = value_type
        self.complex = issubclass(self._type, ResourceBase)
        if not self.multivalued:
            if self.complex:
                self._value = [self._type()]
            else:
                self._value = [None]
        else:
            self._value = []

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

    def dict(self):
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
        if self.complex:
            if self.multivalued:
                if not isinstance(value, list):
                    raise TypeError("Value must be a list")
                self._value = [self._type().load(v) for v in value]
            else:
                self._value = [self._type().load(value)]
        else:
            self.value = value

    # Not overriding __set__ and __get__ methods of the entire attribute
    # because this creates conflicts full replacement of the attribute in parent level
    # hence the use of value, like User.username.value = "John" instead of User.username = "John" 
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
        

class ResourceBase():
    """Base class for SCIM resources which form the root of a SCIM object"""

    def __init__(self, scim_repr=None):        
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
                if issubclass(base, ResourceBase):
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

    def dict(self):
        """Return dictionary representation of the resource"""
        output = {}
        for k, v in self._schema_attrs.items():
            value = v.dict()
            # Do not include attributes that have no value, a complex type for which all subattributes have no value, or multivalue with length 0
            if value not in [None, {}, []]:
                output[k] = value
        return output
    
    def __str__(self):
        return str(self.dict())

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
    
class ComplexBase(ResourceBase):
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