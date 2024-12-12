from scim2.base import Attribute, Complex
from scim2.datatypes import String, Integer

class Fruit(Complex):
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

        x = Attribute(String)
        assert x.dict() == None

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
        # Need to go through c.value to access the complex class inside the attribute object
        # Normally this step would be done throug the parent Resource class
        c.value.name = "apple"
        c.value.color = "red"
        assert c.value.name == "apple"
        assert c.value.color == "red"

    def test_dict(self):
        """Test dict method"""
        c = Attribute(Fruit)
        c.value.name = "apple"
        c.value.color = "red"
        assert c.dict() == {"name": "apple", "color": "red"}

    def test_dict_empty(self):
        """Test complex attribute whose subattributes are all empty
        
        Should return empty dictionary
        """
        c = Attribute(Fruit)
        assert c.dict() == {}

    def test_instance_separation(self):
        """Test if two instances don't share a state"""
        c = Attribute(Fruit)
        c.value.name = "apple"
        c.value.color = "red"
        assert Fruit.name != "apple"
        assert Fruit.color != "red"

        a = Attribute(Fruit)
        a.value.name = "banana"
        a.value.color = "yellow"
        assert a.value.name == "banana"
        assert a.value.color == "yellow"
        assert c.value.name == "apple"
        assert c.value.color == "red"

    def test_str(self):
        """Test str method"""
        c = Attribute(Fruit)
        c.value.name = "apple"
        c.value.color = "red"
        assert str(c) == '{"name": "apple", "color": "red"}'

    def test_load(self):
        """Test load method"""
        c = Attribute(Fruit)
        c.load({"name": "apple", "color": "red"})
        assert c.value.name == "apple"
        assert c.value.color == "red"

class TestComplexMultiValue:
    """Tests for multivalue attribute with complex type"""
    def test_value(self):
        """Test setting and getting value"""
        c = Attribute(Fruit, multivalued=True)
        c.value = [Fruit().load({"name": "apple", "color": "red"})]
        assert c.value[0].name == "apple"
        assert c.value[0].color == "red"

    def test_append(self):
        """Test adding to list"""
        c = Attribute(Fruit, multivalued=True)
        c.value.append(Fruit().load({"name": "apple", "color": "red"}))
        c.value.append(Fruit().load({"name": "banana", "color": "yellow"}))
        assert c.value[0].name == "apple"
        assert c.value[0].color == "red"
        assert c.value[1].name == "banana"
        assert c.value[1].color == "yellow"

    def test_dict(self):
        """Test dict method"""
        c = Attribute(Fruit, multivalued=True)
        f1 = Fruit()
        f1.name = "apple"
        f1.color = "red"
        c.value = [f1]
        assert c.dict() == [{"name": "apple", "color": "red"}]

    def test_instance_separation(self):
        """Test if two instances don't share a state"""	
        c = Attribute(Fruit, multivalued=True)
        c.value = [Fruit().load({"name": "apple", "color": "red"})]
        assert Fruit.name != "apple"
        assert Fruit.color != "red"

        a = Attribute(Fruit, multivalued=True)
        a.value = [Fruit().load({"name": "banana", "color": "yellow"})]
        assert a.value[0].name == "banana"
        assert a.value[0].color == "yellow"
        assert c.value[0].name == "apple"
        assert c.value[0].color == "red"

    def test_str(self):
        """Test str method"""
        c = Attribute(Fruit, multivalued=True)
        c.value = [Fruit().load({"name": "apple", "color": "red"})]
        assert str(c) == '[{"name": "apple", "color": "red"}]'

    def test_load(self):
        """Test load method"""	
        c = Attribute(Fruit, multivalued=True)
        c.load([{"name": "apple", "color": "red"}, {"name": "banana", "color": "yellow"}])
        assert c.value[0].name == "apple"
        assert c.value[0].color == "red"
        assert c.value[1].name == "banana"
        assert c.value[1].color == "yellow"