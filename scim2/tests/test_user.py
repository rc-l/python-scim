# Test for default user class

from datetime import datetime, timezone
import json

from scim2.core import User

def test_minimal_to_dict():
    """User defined in code to dictonary representation
    See section 8.1 in RFC7643"""
    user = User()
    user.id.value = "2819c223-7f76-453a-919d-413861904646"
    user.userName.value = "bjensen@example.com"
    user.meta.value.created.value = datetime(2010, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
    user.meta.value.lastModified.value = datetime(2011, 5, 13, 4, 42, 34, tzinfo=timezone.utc)
    # Leave out version number, escaping doesn't work well

    result = user.dict()
    result['meta']['location'] = result['meta']['location'].format(basepath="https://example.com/v2")

    assert result == {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
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
    assert user.id.value == "2819c223-7f76-453a-919d-413861904646"
    assert user.userName.value == "bjensen@example.com"
    assert user.meta.value.resourceType.value == "User"
    assert user.meta.value.created.value == datetime(2010, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
    assert user.meta.value.lastModified.value == datetime(2011, 5, 13, 4, 42, 34, tzinfo=timezone.utc)
    # Ignoring location since this is generated on dictionary creation
