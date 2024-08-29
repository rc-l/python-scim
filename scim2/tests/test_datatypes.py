from datetime import datetime, timezone, timedelta
import pytest

from scim2.datatypes import String, Integer, Decimal, Boolean, DateTime, Binary, Reference

class TestString:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert String.validate("test")
        assert not String.validate(1)

    def test_convert(self):
        """Test if the value is converted to the correct type"""
        assert String.convert("test") == "test"
        assert String.convert(1) == "1"

    def test_prep_json(self):
        """Test if the value is prepared for json serialization"""
        assert String.prep_json("test") == "test"

class TestInteger:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert Integer.validate(1)
        assert not Integer.validate("test")

    def test_convert(self):
        """Test if the value is converted to the correct type"""
        assert Integer.convert(1) == 1
        assert Integer.convert("1") == 1

    def test_prep_json(self):
        """Test if the value is prepared for json serialization"""
        assert Integer.prep_json(1) == 1

class TestDecimal:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert Decimal.validate(1.0)
        assert not Decimal.validate("test")
        assert not Decimal.validate(1)

    def test_convert(self):
        """Test if the value is converted to the correct type"""
        assert Decimal.convert(1.0) == 1.0
        assert Decimal.convert("1.0") == 1.0
        assert Decimal.convert(1) == 1.0
    
    def test_prep_json(self):
        """Test if the value is prepared for json serialization"""
        assert Decimal.prep_json(1.0) == 1.0

class TestBoolean:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert Boolean.validate(True)
        assert not Boolean.validate("test")
        assert not Boolean.validate(1)

    def test_convert(self):
        """Test if the value is converted to the correct type"""
        assert Boolean.convert(True) == True
        assert Boolean.convert("true") == True
        assert Boolean.convert("false") == False
        assert Boolean.convert("True") == True
        assert Boolean.convert("False") == False
        with pytest.raises(ValueError):
            Boolean.convert("foo")
        with pytest.raises(TypeError):
            Boolean.convert(1)

    def test_prep_json(self):
        """Test if the value is prepared for json serialization"""
        assert Boolean.prep_json(True) == True

class TestDateTime:
    def test_validate(self):
        """Test if the value is of the correct type"""
        assert DateTime.validate(datetime.now())
        assert not DateTime.validate("test")
        assert not DateTime.validate(1)

    def test_convert(self):
        """Test if the value is converted to the correct type"""
        now = datetime.now()
        assert DateTime.convert(now) == now
        assert DateTime.convert("2008-01-23T04:56:22Z") == datetime(2008, 1, 23, 4, 56, 22, tzinfo=timezone.utc)
        assert DateTime.convert("2008-01-23T04:56:22+02:00") == datetime(2008, 1, 23, 4, 56, 22, tzinfo=timezone(timedelta(hours=2)))
        with pytest.raises(ValueError):
            DateTime.convert("1")
        with pytest.raises(ValueError):
            DateTime.convert("foo")
        with pytest.raises(TypeError):
            DateTime.convert(1)

