from datetime import datetime, timezone

from scim2.core import ResourceTypeBase
from scim2.base import Attribute, Base, ComplexBase, Extension
from scim2.datatypes import *

# Objects for testing
# Complex attribute for TestSchema
class Car(ComplexBase):
    make = Attribute(String)
    model = Attribute(String)
    year = Attribute(Integer)


# Define a new schema that inherits from ResourceTypeBase
class TestSchema(ResourceTypeBase):
    class ScimInfo(ResourceTypeBase.ScimInfo):
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
        """Test converting a ResourceTypeBase object to a dictionary"""
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
        user = ResourceTypeBase(data)
        assert user.id == "test"
        assert user.externalId == "foo456"
        assert user.meta.resourceType == "BaseObject"
        assert user.meta.created == datetime(2015, 6, 9, 4, 56, 22, tzinfo=timezone.utc)
        assert user.meta.lastModified == datetime(2015, 6, 9, 5, 56, 22, tzinfo=timezone.utc)
        assert user.meta.location == "https://example.com/Users/test"

class TestExtension:
    """Test incorporating extensions into a ResourceTypeBase subclassess
    
    Extensions are assigned to the class after the class is defined.
    """

    class MyExtension(Extension):
        class ScimInfo(Extension.ScimInfo):
            name = "ExtensionNameCanBeDifferent"

        shape = Attribute(String)

    # Add the extension to the class (no need to instantiate)
    TestSchema.some_ext = MyExtension

    def test_instantiation(self):
        """Test if both the ResourceTypeBase and Extension classes are instantiated
        
        Extension instance should be separate from the class to prevent attribute sharing between instances.
        """
        a = TestSchema()
        b = TestSchema()
        assert a.some_ext.shape is None
        assert b.some_ext.shape is None
        a.some_ext.shape = "square"
        b.some_ext.shape = "circle"
        assert a.some_ext.shape == "square"
        assert b.some_ext.shape == "circle"

    def test_from_dict(self):
        """Test loading dictionary during object creation
        
        Extension attributes need to be in separate namespace defined by their schema.
        """
        data = {
            "id": "8865",
            "fruit": "kiwi",
            self.MyExtension.ScimInfo.schema: {
                "shape": "rectangle"
            }
        }

        s = TestSchema(data)
        assert s.id == "8865"
        assert s.some_ext.shape == "rectangle"

    def test_to_dict(self):
        """Test converting object to dictionary
        
        Extension attributes need to be in separate namespace defined by their schema.
        """
        s = TestSchema()
        s.id = "9f9a"
        s.fruit = "mango"
        s.some_ext.shape = "triangle"
        result = s.dict()
        assert result["id"] == "9f9a"
        assert result["fruit"] == "mango"
        assert result[self.MyExtension.ScimInfo.schema]["shape"] == "triangle"
        assert TestSchema.ScimInfo.schema in result['schemas']
        assert self.MyExtension.ScimInfo.schema in result['schemas']

    def test_get_schema(self):
        """Get schema on resource type should ignore extensions inside the schema and not show it as attributes"""
        s = TestSchema()
        schema = s.get_schema()
        assert schema["id"] == TestSchema.ScimInfo.schema
        assert schema["name"] == "TestSchema"
        assert len(schema["attributes"]) == 2
        attribute_names = [attr["name"] for attr in schema["attributes"]]
        assert "fruit" in attribute_names
        assert "car" in attribute_names
        assert "shape" not in attribute_names
        assert self.MyExtension.ScimInfo.schema not in attribute_names

    def test_resource_type_representation(self):
        """Test the resource type representation of the TestSchema class with extension
        
        The extension should be included in the schemaExtensions list
        """
        rt = TestSchema.resource_type_representation()
        assert "schemaExtensions" in rt
        assert rt['schemaExtensions'][0]['schema'] == self.MyExtension.ScimInfo.schema

    def test_to_dict_with_empty_extension(self):
        """Extension namespace should only be present if at least one attribute is populated"""
        s = TestSchema()
        s.id = "9f9a"
        s.fruit = "mango"
        result = s.dict()
        assert result["id"] == "9f9a"
        assert result["fruit"] == "mango"
        assert self.MyExtension.ScimInfo.schema not in result

class TestInheritence:
    """Test inheritance of ResourceTypeBase"""

    def test_from_dict(self):
        """Test with attributes from both ResourceTypeBase and TestSchema to check if inheritance works"""
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
        assert schema['id'] == 'urn:ietf:params:scim:schemas:custom:2.0:TestSchema'
        assert schema['name'] == TestSchema.ScimInfo.name
        assert schema['description'] == TestSchema.ScimInfo.description
        assert schema['meta']['resourceType'] == 'Schema'
        assert schema['meta']['location'] == "{basepath}/Schemas/" + TestSchema.ScimInfo.schema
        assert len(schema['attributes']) == 2

