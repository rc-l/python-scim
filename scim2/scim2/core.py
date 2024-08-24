import json
from copy import deepcopy, copy

from .attributes import Base, Singular, MultiValue

class ResourceBase(Base):
    """Base class for SCIM resources which form the root of a SCIM object"""

    def __init__(self, scim_repr=None):        
        # Super of init
        super().__init__()

        # Load the SCIM representation if provided
        self.load(scim_repr)

class User(ResourceBase):
    username = Singular()
    emails = MultiValue()