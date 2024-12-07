from datetime import datetime, timezone

from scim2.core import BaseSchema
from scim2.base import Attribute, ResourceBase, ComplexBase
from scim2.datatypes import *

# Objects for testing
# Complex attribute for TestSchema
class Car(ComplexBase):
    make = Attribute(String)
    model = Attribute(String)
    year = Attribute(Integer)


# Define a new schema that inherits from BaseSchema
class TestSchema(BaseSchema):
    class ScimInfo(BaseSchema.ScimInfo):
        name = "TestSchema"
    fruit = Attribute(String)
    car = Attribute(Car)


class TestDict:
    """Tests dictonary conversion"""

    def test_from_dict(self):
        """Test creating am object from a dictionary"""
        data = {
            "id": "test", 
            "externalId": "test2",
            "meta": {
                "resourceType": "TestSchema",
                "created": "2010-01-23T04:56:22Z",
                "lastModified": "2010-01-23T04:56:22Z",
                "location": "https://example.com/TestSchema/test",
                "version": 'W/"3694e05e9dff594"'
            }
        }
        user = TestSchema(data)
        assert user.id == "test"
        assert user.externalId == "test2"
        assert user.meta.resourceType == "TestSchema"
        assert user.meta.created == datetime(2010, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
        assert user.meta.lastModified == datetime(2010, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
        assert user.meta.location == "https://example.com/TestSchema/test"
        assert user.meta.version == 'W/"3694e05e9dff594"'

    def test_to_dict(self):
        """Test converting a BaseSchema object to a dictionary"""
        user = TestSchema()
        user.id = "foo"
        user.externalId = "bar"
        user.meta.resourceType = "BaseObject"
        user.meta.created = datetime(2012, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
        user.meta.lastModified = datetime(2013, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
        user.meta.location = "https://example.com/Users/test"
        user.meta.version = 'W/"3694e05e9eee594"'
        
        result = user.dict()
        assert result['id'] == "foo"
        assert result['externalId'] == "bar"
        # The input resource type is ignored it is readonly
        assert result['meta']['resourceType'] == "TestSchema"
        assert result['meta']['created'] == "2012-01-23T04:56:22+00:00"
        assert result['meta']['lastModified'] == "2013-01-23T04:56:22+00:00"
        assert result['meta']['location'] == "{basepath}/TestSchemas/foo"
        assert result['meta']['version'] == 'W/"3694e05e9eee594"'

    def test_from_json(self):
        data = """{
            "id": "test", 
            "externalId": "foo456",
            "meta": {
                "resourceType": "BaseObject",
                "created": "2015-06-09T04:56:22Z",
                "lastModified": "2015-06-09T05:56:22Z",
                "location": "https://example.com/Users/test"
            }
        }"""
        user = BaseSchema(data)
        assert user.id == "test"
        assert user.externalId == "foo456"
        assert user.meta.resourceType == "BaseObject"
        assert user.meta.created == datetime(2015, 6, 9, 4, 56, 22, tzinfo=timezone.utc)
        assert user.meta.lastModified == datetime(2015, 6, 9, 5, 56, 22, tzinfo=timezone.utc)
        assert user.meta.location == "https://example.com/Users/test"

class TestInheritence:
    """Test inheritance of BaseSchema"""

    def test_from_dict(self):
        """Test with attributes from both BaseSchema and TestSchema to check if inheritance works"""
        data = {
            "id": "inheritencTest",
            "fruit": "kiwi"
        }

        o = TestSchema(data)
        assert o.id == "inheritencTest"
        assert o.fruit == "kiwi"

    def test_schema_representation(self):
        """Test the schema representation of the TestSchema class"""
        schema = TestSchema.get_schema()
        assert schema['id'] == 'urn:ietf:params:scim:schemas:extension:2.0:TestSchema'
        assert schema['name'] == TestSchema.ScimInfo.name
        assert schema['description'] == TestSchema.ScimInfo.description
        assert schema['meta']['resourceType'] == 'Schema'
        assert schema['meta']['location'] == "{basepath}/Schemas/" + TestSchema.ScimInfo.schema
        assert len(schema['attributes']) == 2

    def test_list_schemas(self):
        """Test listing the schemas"""
        # Test with a single level, the base class should not be in the list
        schemas = TestSchema.list_schemas()
        assert len(schemas) == 1
        assert schemas[0] == TestSchema.ScimInfo.schema

        # Test with a subclass that extends the schema
        # Schema of both superclass and subclass should be in the list
        class ExtensionSchema(TestSchema):
            class ScimInfo(TestSchema.ScimInfo):
                name = "ExtensionSchema"

        schemas = ExtensionSchema.list_schemas()
        assert len(schemas) == 2
        assert TestSchema.ScimInfo.schema in schemas
        assert ExtensionSchema.ScimInfo.schema in schemas
