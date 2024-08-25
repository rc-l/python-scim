import json
from copy import deepcopy, copy

from .attributes import Attribute, Base

class ResourceBase(Base):
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
    def _class_schema_attrs(cls):
        """Get all the attributes that are part of the schema to be used for class not class instance"""
        return cls._filter_schema_attrs(vars(cls))

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
            if value:
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
        

# class User(ResourceBase):
#     username = Singular()
#     emails = MultiValue()