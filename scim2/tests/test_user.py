# Test for default user class

from copy import deepcopy
from datetime import datetime, timezone
import json

from scim2.core import User

def test_minimal_to_dict():
    """User defined in code to dictonary representation
    See section 8.1 in RFC7643"""

    user = User()
    user.id = "2819c223-7f76-453a-919d-413861904646"
    user.userName = "bjensen@example.com"
    user.meta.created = datetime(2010, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
    user.meta.lastModified = datetime(2011, 5, 13, 4, 42, 34, tzinfo=timezone.utc)
    # Leave out version number, escaping doesn't work well

    result = user.dict()
    result['meta']['location'] = result['meta']['location'].format(basepath="https://example.com/v2")

    # Schemas is not the same as in RFC. Since the Enterprise extension is already in place
    assert result == {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User", "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"],
        "id": "2819c223-7f76-453a-919d-413861904646",
        "userName": "bjensen@example.com",
        "meta": {
            "resourceType": "User",
            "created": "2010-01-23T04:56:22+00:00",
            "lastModified": "2011-05-13T04:42:34+00:00",
            "location": "https://example.com/v2/Users/2819c223-7f76-453a-919d-413861904646"
        }
    }

def test_minimal_from_json():
    """Conver the mininmal user json to python object
    
    See section 8.1 in RFC7643"""
    # Ignoring version because the escape characters cause problems
    data = """
        {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": "2819c223-7f76-453a-919d-413861904646",
            "userName": "bjensen@example.com",
            "meta": {
                "resourceType": "User",
                "created": "2010-01-23T04:56:22Z",
                "lastModified": "2011-05-13T04:42:34Z",
                "location":
                "https://example.com/v2/Users/2819c223-7f76-453a-919d-413861904646"
            }
        }
    """
    user = User(data)
    assert user.id == "2819c223-7f76-453a-919d-413861904646"
    assert user.userName == "bjensen@example.com"
    assert user.meta.resourceType == "User"
    assert user.meta.created == datetime(2010, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
    assert user.meta.lastModified == datetime(2011, 5, 13, 4, 42, 34, tzinfo=timezone.utc)
    # Ignoring location since this is generated on dictionary creation

def test_resource_type_representation():
    """Test the resource type representation of the User class
    
    Example from RFC7643 section 8.3"""
    # Note worthy differences with RFC:
    # - The location is not filled in
    # - The schemaExtensions are not required here

    output = User.resource_type_representation()
    assert output == {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
        "id": "User",
        "name": "User",
        "endpoint": "/Users",
        "description": "User Account",
        "schema": "urn:ietf:params:scim:schemas:core:2.0:User",
        "schemaExtensions": [
            {
                "schema":
                "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User",
                "required": False
            }
        ],
        "meta": {
            "resourceType": "ResourceType",
            "location": "{basepath}/ResourceTypes/User"
        }  
    }