# Use these data types to take care of formats, validation and conversion of data

from datetime import datetime

__all__ = ["String", "Integer", "Decimal", "Boolean", "DateTime", "Binary", "Reference"]

class DataTypeBase:
    @classmethod
    def validate(cls, value):
        """Validate if the value is of the correct type"""
        return isinstance(value, cls.base_type)
    
    @classmethod
    def convert(cls, value):
        """Convert the value to the correct type"""
        return cls.base_type(value)
    
    @classmethod
    def prep_json(cls, value):
        """Prepare the value for later json serialization.
        Changes may not be necessary for every data type the default is to return the value unchanged
        Override function in subclass to change this behavior"""
        return value
    
class String(DataTypeBase):
    base_type = str
    name = "string"

class Integer(DataTypeBase):
    base_type = int
    name = "integer"

class Decimal(DataTypeBase):
    """Decimal number represented as a float"""
    
    # This may not strictly follow the SCIM spec which states that it must be a 
    # Number per Section 6 of [RFC7159]. But is easier to implement
    base_type = float
    name = "decimal"

class Boolean(DataTypeBase):
    base_type = bool
    name = "boolean"

    @classmethod
    def convert(cls, value):
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            else:
                raise ValueError("Cannot convert value to boolean")
        else:
            raise TypeError("This type/value does not represent a boolean")

class DateTime(DataTypeBase):
    base_type = datetime
    name = "dateTime"

    @classmethod
    def convert(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        elif isinstance(value, cls.base_type):
            return value
        else:
            raise TypeError("This type does not convert to datetime")
        
    @classmethod
    def prep_json(cls, value):
        if value:
            return value.isoformat()
        else:
            return None

class Binary(DataTypeBase):
    name = "binary"

    def validate(cls, value):
        raise NotImplementedError("Binary data type not implemented yet")

class Reference(DataTypeBase):
    name = "reference"

    def validate(cls, value):
        raise NotImplementedError("Reference data type not implemented yet")
