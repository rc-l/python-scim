from scim2.base import Attribute, Base
from scim2.datatypes import String

class TestBase:
# Create user here for testing so it will not be affected by changed in the core user
    class User(Base):
        username = Attribute(String)
        emails = Attribute(String, multivalued=True)

    def test_attribute_sharing(self):
        """Attributes for two instances should not be shared"""
        # Check if instance and class attributes are different (not same object id)
        assert self.User().get_attribute('username') is not self.User.username

        # Check if two instances have different attributes
        assert self.User().get_attribute('username') is not self.User().get_attribute('username')

        # Check value assignment is not shared
        userA = self.User()
        userB = self.User()
        userA.username = "userA"
        assert userA.username == "userA"
        assert userB.username != "userA"

    def test_attribute_assignment(self):
        """Assign attributes in python code.
        Assigned attribute should be remembered and returned in dict"""
        # Pythonic attribute assignment
        user = self.User()
        user.username = "test"
        assert user.dict() == {'username': 'test'}

    def test_attribute_delete(self):
        """Delete an attribute value"""
        user = self.User()
        user.username = "test"
        assert user.dict() == {'username': 'test'}
        del user.username
        assert user.dict() == {}
        # Do this extra check to ensure the Attribute object is still there
        assert user.get_attribute('username').value is None
    

    def test_creation_from_dict(self):
        """Create a User object from a dictionary"""
        user = self.User({"username": "test", "emails": ["user@example.com", "admin@something.com"]})
        assert user.username == "test"
        assert user.emails == ["user@example.com", "admin@something.com"]
