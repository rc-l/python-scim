from datetime import datetime

from scim2.datatypes import String, Integer, Decimal, Boolean, DateTime, Binary, Reference

class TestString:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert String.validate("test")
        assert not String.validate(1)

class TestInteger:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert Integer.validate(1)
        assert not Integer.validate("test")

class TestDecimal:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert Decimal.validate(1.0)
        assert not Decimal.validate("test")
        assert not Decimal.validate(1)

class TestBoolean:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert Boolean.validate(True)
        assert not Boolean.validate("test")
        assert not Boolean.validate(1)

class TestDateTime:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert DateTime.validate(datetime.now())
        assert not DateTime.validate("test")
        assert not DateTime.validate(1)

