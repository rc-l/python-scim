from scim2.base import Attribute, ResourceBase, ComplexBase
from scim2.datatypes import String, Integer

class Fruit(ComplexBase):
    """Class for testing Complex attribute"""
    name = Attribute(String)
    color = Attribute(String)

class TestSingular:
    def test_value(self):
        """Test setting and getting value"""
        s = Attribute(String)
        s.value = "test"
        assert s.value == "test"

        a = Attribute(Integer)
        a.value = 1
        assert a.value == 1
        a.value = "2"
        assert a.value == 2

    def test_dict(self):
        """Test dict method"""
        s = Attribute(String)
        s.value = "test"
        assert s.dict() == "test"

    def test_instance_separation(self):
        """Test if two instances don't share a state"""
        s = Attribute(String)
        s.value = "test"
        assert Attribute.value != "test"
        assert s.value == "test"

        a = Attribute(String)
        a.value = "different"
        assert a.value == "different"
        assert s.value == "test"

    def test_str(self):
        """Test str method"""
        s = Attribute(String)
        s.value = "test"
        assert str(s) == "test"

    def test_load(self):
        """Test load method"""
        s = Attribute(String)
        s.load("abc")
        assert s.value == "abc"

class TestMultiValue:
    def test_value(self):
        """Test setting and getting value"""
        m = Attribute(String, multivalued=True)
        m.value = ["test"]
        assert m.value == ["test"]

    def test_append(self):
        """Test adding to list"""
        m = Attribute(String, multivalued=True)
        m.value = ["test"]
        m.value.append("new")
        assert m.value == ["test", "new"]

    def test_dict(self):
        """Test dict method"""
        m = Attribute(String, multivalued=True)
        m.value = ["test"]
        assert m.dict() == ["test"]

    def test_instance_separation(self):
        """Test if two instances don't share a state"""
        m = Attribute(String, multivalued=True)
        m.value = ["test"]
        assert Attribute.value != ["test"]
        assert m.value == ["test"]

        a = Attribute(String, multivalued=True)
        a.value = ["different"]
        assert a.value == ["different"]
        assert m.value == ["test"]

    def test_str(self):
        """Test str method"""
        m = Attribute(String, multivalued=True)
        m.value = ["test"]
        assert str(m) == '["test"]'

    def test_load(self):
        """Test load method"""
        m = Attribute(String, multivalued=True)
        m.load(["abc"])
        assert m.value == ["abc"]

class TestComplex:
    
    def test_value(self):
        """Test setting and getting value"""
        c = Attribute(Fruit)
        c.value.name.value = "apple"
        c.value.color.value = "red"
        assert c.value.name.value == "apple"
        assert c.value.color.value == "red"

    def test_dict(self):
        """Test dict method"""
        c = Attribute(Fruit)
        c.value.name.value = "apple"
        c.value.color.value = "red"
        assert c.dict() == {"name": "apple", "color": "red"}

    def test_instance_separation(self):
        """Test if two instances don't share a state"""
        c = Attribute(Fruit)
        c.value.name.value = "apple"
        c.value.color.value = "red"
        assert Fruit.name.value != "apple"
        assert Fruit.color.value != "red"

        a = Attribute(Fruit)
        a.value.name.value = "banana"
        a.value.color.value = "yellow"
        assert a.value.name.value == "banana"
        assert a.value.color.value == "yellow"
        assert c.value.name.value == "apple"
        assert c.value.color.value == "red"

    def test_str(self):
        """Test str method"""
        c = Attribute(Fruit)
        c.value.name.value = "apple"
        c.value.color.value = "red"
        assert str(c) == '{"name": "apple", "color": "red"}'

    def test_load(self):
        """Test load method"""
        c = Attribute(Fruit)
        c.load({"name": "apple", "color": "red"})
        assert c.value.name.value == "apple"
        assert c.value.color.value == "red"

class TestComplexMultiValue:
    """Tests for multivalue attribute with complex type"""
    def test_value(self):
        """Test setting and getting value"""
        c = Attribute(Fruit, multivalued=True)
        c.value = [Fruit().load({"name": "apple", "color": "red"})]
        assert c.value[0].name.value == "apple"
        assert c.value[0].color.value == "red"

    def test_append(self):
        """Test adding to list"""
        c = Attribute(Fruit, multivalued=True)
        c.value.append(Fruit().load({"name": "apple", "color": "red"}))
        c.value.append(Fruit().load({"name": "banana", "color": "yellow"}))
        assert c.value[0].name.value == "apple"
        assert c.value[0].color.value == "red"
        assert c.value[1].name.value == "banana"
        assert c.value[1].color.value == "yellow"

    def test_dict(self):
        """Test dict method"""
        c = Attribute(Fruit, multivalued=True)
        f1 = Fruit()
        f1.name.value = "apple"
        f1.color.value = "red"
        c.value = [f1]
        assert c.dict() == [{"name": "apple", "color": "red"}]

    def test_instance_separation(self):
        """Test if two instances don't share a state"""	
        c = Attribute(Fruit, multivalued=True)
        c.value = [Fruit().load({"name": "apple", "color": "red"})]
        assert Fruit.name.value != "apple"
        assert Fruit.color.value != "red"

        a = Attribute(Fruit, multivalued=True)
        a.value = [Fruit().load({"name": "banana", "color": "yellow"})]
        assert a.value[0].name.value == "banana"
        assert a.value[0].color.value == "yellow"
        assert c.value[0].name.value == "apple"
        assert c.value[0].color.value == "red"

    def test_str(self):
        """Test str method"""
        c = Attribute(Fruit, multivalued=True)
        c.value = [Fruit().load({"name": "apple", "color": "red"})]
        assert str(c) == '[{"name": "apple", "color": "red"}]'

    def test_load(self):
        """Test load method"""	
        c = Attribute(Fruit, multivalued=True)
        c.load([{"name": "apple", "color": "red"}, {"name": "banana", "color": "yellow"}])
        assert c.value[0].name.value == "apple"
        assert c.value[0].color.value == "red"
        assert c.value[1].name.value == "banana"
        assert c.value[1].color.value == "yellow"