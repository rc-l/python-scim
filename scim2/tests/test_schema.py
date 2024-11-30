from datetime import datetime, timezone

from scim2.core import BaseSchema
from scim2.base import Attribute, ResourceBase, ComplexBase
from scim2.datatypes import *

class TestBaseSchema:
    """Tests for the BaseSchema class and generic functions"""

    def test_from_dict(self):
        """Test creating a BaseSchema object from a dictionary"""
        data = {
            "id": "test", 
            "externalId": "test2",
            "meta": {
                "resourceType": "BaseObject",
                "created": "2010-01-23T04:56:22Z",
                "lastModified": "2010-01-23T04:56:22Z",
                "location": "https://example.com/Users/test",
                "version": 'W/"3694e05e9dff594"'
            }
        }
        user = BaseSchema(data)
        assert user.id.value == "test"
        assert user.externalId.value == "test2"
        assert user.meta.value.resourceType.value == "BaseObject"
        assert user.meta.value.created.value == datetime(2010, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
        assert user.meta.value.lastModified.value == datetime(2010, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
        assert user.meta.value.location.value == "https://example.com/Users/test"
        assert user.meta.value.version.value == 'W/"3694e05e9dff594"'

    def test_to_dict(self):
        """Test converting a BaseSchema object to a dictionary"""
        user = BaseSchema()
        user.id.value = "foo"
        user.externalId.value = "bar"
        user.meta.value.resourceType.value = "BaseObject"
        user.meta.value.created.value = datetime(2012, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
        user.meta.value.lastModified.value = datetime(2013, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
        user.meta.value.location.value = "https://example.com/Users/test"
        user.meta.value.version.value = 'W/"3694e05e9eee594"'
        assert user.dict() == {
            "id": "foo",
            "externalId": "bar",
            "meta": {
                "resourceType": BaseSchema._info_name,
                "created": "2012-01-23T04:56:22+00:00",
                "lastModified": "2013-01-23T04:56:22+00:00",
                "location": "{basepath}/BaseSchema",
                "version": 'W/"3694e05e9eee594"'
            }
        }

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
        assert user.id.value == "test"
        assert user.externalId.value == "foo456"
        assert user.meta.value.resourceType.value == "BaseObject"
        assert user.meta.value.created.value == datetime(2015, 6, 9, 4, 56, 22, tzinfo=timezone.utc)
        assert user.meta.value.lastModified.value == datetime(2015, 6, 9, 5, 56, 22, tzinfo=timezone.utc)
        assert user.meta.value.location.value == "https://example.com/Users/test"

class TestInheritence:
    """Test inheritance of BaseSchema"""

    # Define a new schema that inherits from BaseSchema
    class TestSchema(BaseSchema):
        fruit = Attribute(String)

    def test_from_dict(self):
        """Test with attributes from both BaseSchema and TestSchema to check if inheritance works"""
        data = {
            "id": "inheritencTest",
            "fruit": "kiwi"
        }

        o = self.TestSchema(data)
        assert o.id.value == "inheritencTest"
        assert o.fruit.value == "kiwi"