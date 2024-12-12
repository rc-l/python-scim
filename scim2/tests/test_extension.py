from scim2.base import Extension, Attribute
from scim2.datatypes import String, Integer

class Pet(Extension):
    class ScimInfo(Extension.ScimInfo):
        name = "Pet"

    animal = Attribute(String)
    age = Attribute(Integer)

def test_from_dict():
    """Test loading dictionary during object creation"""
    pet = Pet({"animal": "dog", "age": 5})
    assert pet.animal == "dog"
    assert pet.age == 5

def test_to_dict():
    """Test converting object to dictionary"""
    pet = Pet()
    pet.animal = "cat"
    pet.age = 7
    assert pet.dict() == {"animal": "cat", "age": 7}

def test_get_schema():
    """Test getting schema"""
    pet = Pet()
    schema = pet.get_schema()
    assert schema["id"] == Pet.ScimInfo.schema
    assert schema["name"] == "Pet"
    assert len(schema["attributes"]) == 2
    attribute_names = [attr["name"] for attr in schema["attributes"]]
    assert "animal" in attribute_names
    assert "age" in attribute_names
    