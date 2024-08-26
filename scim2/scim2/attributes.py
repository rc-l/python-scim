import json

from scim2.datatypes import DataTypeBase

# Base class for resource base.
# This is to later check for complex attributes.
# Can't import ResourceBase here because of circular import
class Base():
    pass

class Attribute():
    """Base class for all attributes

    RFC 7643 section 2
    """
    def __init__(self, value_type, **kwargs):
        self.multivalued = kwargs.get("multivalued", False)
        self._type = value_type
        self.complex = issubclass(self._type, Base)
        if not self.multivalued:
            self._value = [self._type()]
        else:
            self._value = []

        # Check if type is valid
        if not issubclass(self._type, DataTypeBase) and not self.complex:
            raise TypeError("Must provde a valid data type (subclass of DataType or a Complex)")

    def dict(self):
        if self.complex:
            if self.multivalued:
                return [v.dict() for v in self._value]
            else:
                return self._value[0].dict()
        else:
            if self.multivalued:
                return self._value
            else:
                return self._value[0]
    
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
