from scim2.base import Attribute, ResourceBase
from scim2.datatypes import String

class TestResourceBase:
# Create user here for testing so it will not be affected by changed in the core user
    class User(ResourceBase):
        username = Attribute(String)
        emails = Attribute(String, multivalued=True)

    def test_attribute_sharing(self):
        """Attributes for two instances should not be shared"""
        # Check if instance and class attributes are different
        assert self.User().username is not self.User.username

        # Check if two instances have different attributes
        assert self.User().username is not self.User().username

        # Check value assignment is not shared
        userA = self.User()
        userB = self.User()
        userA.username.value = "userA"
        assert userA.username.value == "userA"
        assert userB.username.value != "userA"

    def test_attribute_assignment(self):
        """Assign attributes in python code.
        Assigned attribute should be remembered and returned in dict"""
        # Pythonic attribute assignment
        user = self.User()
        user.username.value = "test"
        assert user.dict() == {'username': 'test', 'emails': []}

    def test_creation_from_dict(self):
        """Create a User object from a dictionary"""
        user = self.User({"username": "test", "emails": ["user@example.com", "admin@something.com"]})
        assert user.username.value == "test"
        assert user.emails.value == ["user@example.com", "admin@something.com"]
