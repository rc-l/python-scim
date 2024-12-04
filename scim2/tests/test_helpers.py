from scim2.helpers import *

class TestInheritors:

    def test_standard(self):
        """"Test the standard flow for the Inheritors function"""

        # Create 3 classes each a subclass of the previous
        class A:
            pass

        class B(A):
            pass

        class C(B):
            pass

        # Get the inheritors of A
        result = inheritors(A)
        assert result == {B, C}

    def test_middle_class(self):
        """"Test the case where the class is a middle class"""

        # Create 3 classes each a subclass of the previous
        class A:
            pass

        class B(A):
            pass

        class C(B):
            pass

        # Get the inheritors of B
        result = inheritors(B)
        assert result == {C}

    def test_multiple_subclasses(self):
        """"Test the case where the class has multiple subclasses"""

        # Create 3 classes each a subclass of the previous
        class A:
            pass

        class B(A):
            pass

        class C(A):
            pass

        # Get the inheritors of A
        result = inheritors(A)
        assert result == {B, C}

    def test_no_subclasses(self):
        """"Test the case where the class has no subclasses"""

        # Create a class with no subclasses
        class A:
            pass

        # Get the inheritors of A
        result = inheritors(A)
        assert result == set()
