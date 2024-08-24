from scim2.attributes import Singular, MultiValue, Complex, Base

class TestSingular:
    def test_value(self):
        """Test setting and getting value"""
        s = Singular()
        s.value = "test"
        assert s.value == "test"

    def test_dict(self):
        """Test dict method"""
        s = Singular()
        s.value = "test"
        assert s.dict() == "test"

    def test_instance_separation(self):
        """Test if two instances don't share a state"""

        s = Singular()
        s.value = "test"
        assert Singular.value != "test"
        assert s.value == "test"

        a = Singular()
        a.value = "different"
        assert a.value == "different"
        assert s.value == "test"

    # def test_deepcopy(self):
    #     """Test deepcopy method to ensure separation between instances"""
    #     s = Singular()
    #     s.value = "test"
    #     s_copy = s.__deepcopy__({})
    #     assert s_copy.value == "test"

    #     a = Singular()
    #     a.value = "different"
    #     assert a.value == "different"
    #     assert s.value == "test"

    def test_str(self):
        """Test str method"""
        s = Singular()
        s.value = "test"
        assert str(s) == "test"

    def test_load(self):
        """Test load method"""
        s = Singular()
        s.load("abc")
        assert s.value == "abc"

class TestMultiValue:
    def test_value(self):
        """Test setting and getting value"""
        m = MultiValue()
        m.value = ["test"]
        assert m.value == ["test"]

    def test_append(self):
        """Test adding to list"""
        m = MultiValue()
        m.value = ["test"]
        m.value.append("new")
        assert m.value == ["test", "new"]

    def test_dict(self):
        """Test dict method"""
        m = MultiValue()
        m.value = ["test"]
        assert m.dict() == ["test"]

    def test_instance_separation(self):
        """Test if two instances don't share a state"""
        m = MultiValue()
        m.value = ["test"]
        assert MultiValue.value != ["test"]
        assert m.value == ["test"]

        a = MultiValue()
        a.value = ["different"]
        assert a.value == ["different"]
        assert m.value == ["test"]

    # def test_deepcopy(self):
    #     """Test deepcopy method to ensure separation between instances"""
    #     m = MultiValue()
    #     m.value = ["test"]
    #     m_copy = m.__deepcopy__({})
    #     assert m_copy.value == ["test"]

    #     a = MultiValue()
    #     a.value = ["different"]
    #     assert a.value == ["different"]
    #     assert m.value == ["test"]

    def test_str(self):
        """Test str method"""
        m = MultiValue()
        m.value = ["test"]
        assert str(m) == "['test']"

    def test_load(self):
        """Test load method"""
        m = MultiValue()
        m.load(["abc"])
        assert m.value == ["abc"]

class TestComplex:
    class Fruit(Base):
        name = Singular()
        color = Singular()
    
    def test_value(self):
        """Test setting and getting value"""
        c = Complex(self.Fruit)
        c.value.name.value = "apple"
        c.value.color.value = "red"
        assert c.value.name.value == "apple"
        assert c.value.color.value == "red"

    def test_dict(self):
        """Test dict method"""
        c = Complex(self.Fruit)
        c.value.name.value = "apple"
        c.value.color.value = "red"
        assert c.dict() == {"name": "apple", "color": "red"}

    def test_instance_separation(self):
        """Test if two instances don't share a state"""
        c = Complex(self.Fruit)
        c.value.name.value = "apple"
        c.value.color.value = "red"
        assert self.Fruit.name.value != "apple"
        assert self.Fruit.color.value != "red"

        a = Complex(self.Fruit)
        a.value.name.value = "banana"
        a.value.color.value = "yellow"
        assert a.value.name.value == "banana"
        assert a.value.color.value == "yellow"
        assert c.value.name.value == "apple"
        assert c.value.color.value == "red"


    # def test_deepcopy(self):
    #     """Test deepcopy method to ensure separation between instances"""
    #     c = Complex(self.Fruit)
    #     c.value.name.value = "apple"
    #     c.value.color.value = "red"
    #     c_copy = c.__deepcopy__({})
    #     assert c_copy.value.name.value == "apple"
    #     assert c_copy.value.color.value == "red"

    #     a = Complex(self.Fruit)
    #     a.value.name.value = "banana"
    #     a.value.color.value = "yellow"
    #     assert a.value.name.value == "banana"
    #     assert a.value.color.value == "yellow"
    #     assert c.value.name.value == "apple"
    #     assert c.value.color.value == "red"

    def test_str(self):
        """Test str method"""
        c = Complex(self.Fruit)
        c.value.name.value = "apple"
        c.value.color.value = "red"
        assert str(c) == "{'name': 'apple', 'color': 'red'}"

    def test_load(self):
        """Test load method"""
        c = Complex(self.Fruit)
        c.load({"name": "apple", "color": "red"})
        assert c.value.name.value == "apple"
        assert c.value.color.value == "red"
