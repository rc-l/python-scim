# Use these data types to take care of formats, validation and conversion of data

from datetime import datetime

class DataTypeBase:
    @classmethod
    def validate(cls, value):
        """Validate if the value is of the correct type"""
        return isinstance(value, cls.base_type)
    
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

class DateTime(DataTypeBase):
    base_type = datetime
    name = "dateTime"

class Binary(DataTypeBase):

    def validate(cls, value):
        raise NotImplementedError("Binary data type not implemented yet")

class Reference(DataTypeBase):

    def validate(cls, value):
        raise NotImplementedError("Binary data type not implemented yet")
