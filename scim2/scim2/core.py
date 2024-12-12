from .base import Attribute, Base, ComplexBase, ResourceBase, Extension
from .datatypes import *
from .helpers import inheritors, classproperty

class MetaData(ComplexBase):
    """Metadata for a resource"""
    
    resourceType = Attribute(String, mutability="readOnly", caseExact=True)
    created = Attribute(DateTime)
    lastModified = Attribute(DateTime)
    location = Attribute(String)
    version = Attribute(String)

class ResourceTypeBase(ResourceBase):
    """Base class for SCIM Resource Types which form the root resources of the SCIM API"""

    id = Attribute(String, required=True)
    externalId = Attribute(String)
    meta = Attribute(MetaData)

    class ScimInfo(ResourceBase.ScimInfo):
        # Note on naming this class, did not pick Metadata, or Schema or variants
        # thereof since these are already keys in the SCIM schema representation
        """Metadata for the SCIM object"""

        # Left name undefined on purpose, should be overridden by subclasses
        endpoint = classproperty(lambda cls: "/" + cls.name + "s")
        schema = classproperty(lambda cls: f'urn:ietf:params:scim:schemas:custom:2.0:{cls.name}')

    def __init__(self, *args, **kwargs):
        # Instatiate extensions
        for k, v in self.extensions:
            setattr(self, k, v())

        super().__init__(*args, **kwargs)

    def dict(self):
        """Convert the object to a dictionary"""
        super_dict = super().dict()

        # Add metadata
        super_dict['schemas'] = [self.ScimInfo.schema] + self.extension_schemas
        if "meta" not in super_dict:
            super_dict['meta'] = {}
        super_dict['meta']["resourceType"] = self.ScimInfo.name
        super_dict['meta']["location"] = "{basepath}" + self.ScimInfo.endpoint + "/" + super_dict['id']

        # Add extensions
        for k, v in self.extensions:
            # Get the dict of the instantiated extension object 
            # Going for v directly would get use the uninstantiated class
            extension_dict = self.__getattribute__(k).dict()

            # Add the dict to the super_dict
            # This needs to be in it's own namespace based on the schema name according to the SCIM spec
            if extension_dict:
                super_dict[v.ScimInfo.schema] = extension_dict
        return super_dict
    
    def load(self, repr):
        # Do normal load first, this changes the state of self
        super().load(repr)
        extension_key_mapping = {v.ScimInfo.schema: k for k, v in self.extensions}

        # Load extensions
        if self._original_repr:
            # Loop over all the keys in the original representation
            for k, v in self._original_repr.items():
                # Check if the key is an extension
                if k in extension_key_mapping:
                    # Get the extension key
                    extension_key = extension_key_mapping[k]
                    # Load the extension
                    self.__getattribute__(extension_key).load(v)

    @classmethod
    def resource_type_representation(cls):
        """Generate a resource type representation.

        According to RFC7643 section 6 and in support of RFC7644 section 4."""
        output = dict()
        output['schemas'] = ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"]
        output['meta'] = {}
        output['meta']['resourceType'] = "ResourceType"
        output['meta']['location'] = "{basepath}/ResourceTypes/" + cls.ScimInfo.name
        output['endpoint'] = cls.ScimInfo.endpoint
        output['schema'] = cls.ScimInfo.schema
        output['name'] = cls.ScimInfo.name
        output['id'] = cls.ScimInfo.id

        # Description optional
        try:
            output['description'] = cls.ScimInfo.description
        except AttributeError:
            output['description'] = ""

        # Schema extensions
        # All the schemas that extend this schema
        output['schemaExtensions'] = [
            {
                "schema": e,
                "required": False
            } 
            for e in cls.extension_schemas
        ]

        return output

    @classproperty
    def extensions(cls):
        """List all the extensions for the resource type"""
        # Get all variables in class and filter for the ones that are subclasses of Extension
        return [(k, v) for k, v in vars(cls).items() if type(v) is type and issubclass(v, Extension)]
    
    @classproperty
    def extension_schemas(cls):
        """List all the extension schemas for the resource type"""
        return [v.ScimInfo.schema for k, v in cls.extensions]

class Name(ComplexBase):
    """Complex attribute for the name of a user"""
    formatted = Attribute(String, description="The full name, including all middle names, titles, and suffixes as appropriate, formatted for display (e.g., 'Ms. Barbara J Jensen, III').")
    familyName = Attribute(String, description="The family name of the User, or last name in most Western languages (e.g., 'Jensen' given the full name 'Ms. Barbara J Jensen, III').")
    givenName = Attribute(String, description="The given name of the User, or first name in most Western languages (e.g., 'Barbara' given the full name 'Ms. Barbara J Jensen, III').")
    middleName = Attribute(String, description="The middle name(s) of the User (e.g., 'Jane' given the full name 'Ms. Barbara J Jensen, III').")
    honorificPrefix = Attribute(String, description="The honorific prefix(es) of the User, or title in most Western languages (e.g., 'Ms.' given the full name 'Ms. Barbara J Jensen, III').")
    honorificSuffix = Attribute(String, description="The honorific suffix(es) of the User, or suffix in most Western languages (e.g., 'III' given the full name 'Ms. Barbara J Jensen, III').")


class DefaultMultiValueComplex(ComplexBase):
    """Default format for a multivalue complex attribute"""
    value = Attribute(String, description="attribute value")
    display = Attribute(String, description="A human-readable name, primarily used for display purposes.")
    type = Attribute(String, description="A label indicating the attribute's function, e.g., 'work' or 'home'.")
    primary = Attribute(Boolean, description="A Boolean value indicating the 'primary' or preferred attribute value for this attribute.")


class BinaryMultiValueComplex(DefaultMultiValueComplex):
    """Same as DefaultMultiValueComplex but with binary data"""
    value = Attribute(Binary, description="binary attribute value")


class MultiValueReference(ComplexBase):
    """Default format for a multivalue reference attribute"""
    value = Attribute(Reference, description="Idenitfier of the referenced resource.")
    display = Attribute(String, description="A human-readable name, primarily used for display purposes.")
    type = Attribute(String, description="A label indicating the attribute's function, e.g., 'work' or 'home'.")
    ref = Attribute(Reference, name="$ref", mutability="readOnly", description="URI of the reference resource")


class User(ResourceTypeBase):

    class ScimInfo(ResourceTypeBase.ScimInfo):
        name = "User"
        description = "User Account"
        schema = "urn:ietf:params:scim:schemas:core:2.0:User"

    userName = Attribute(String, required=True)
    name = Attribute(Name, description="The components of the user's real name. Providers MAY return just the full name as a single string in the formatted sub-attribute, or they MAY return just the individual component attributes using the other sub-attributes, or they MAY return both. If both variants are returned, they SHOULD be describing the same name, with the formatted name indicating how the component attributes should be combined.")
    displayName = Attribute(String, description="The name of the User, suitable for display to end-users.The name SHOULD be the full name of the User being described, if known.")
    nickName = Attribute(String, description="The casual way to address the user in real life, e.g., 'Bob' or 'Bobby' instead of 'Robert'. This attribute SHOULD NOT be used to represent a User's username (e.g., 'bjensen' or 'mpepperidge').")
    # TODO: make reference of external type
    profileUrl = Attribute(Reference, description="A fully qualified URL to a page representing the User's online profile.")
    title = Attribute(String, description='The user\'s title, such as "Vice President."')
    userType = Attribute(String, description="Used to identify the relationship between the organization and the user.")
    preferredLanguage = Attribute(String, description="Indicates the User's preferred written or spoken language. Generally used for selecting a localized User interface; e.g., 'en_US' specifies the language English and country US.")
    locale = Attribute(String, description="Used to indicate the User's default location for purposes of localizing items such as currency, date time format, or numerical representations.")
    timezone = Attribute(String, description="The User's time zone in the 'Olson' time zone database format; e.g., 'America/Los_Angeles'.")
    active = Attribute(Boolean, description="A Boolean value indicating the User's administrative status.")
    password = Attribute(String, mutability="writeOnly", returned="never", description="The User's clear text password. This attribute is intended to be used as a means to specify an initial password when creating a new User or to reset an existing User's password.")
    emails = Attribute(DefaultMultiValueComplex, multivalued=True, description="Email addresses for the user.")
    phoneNumbers = Attribute(DefaultMultiValueComplex, multivalued=True, description="Phone numbers for the User.")
    ims = Attribute(DefaultMultiValueComplex, multivalued=True, description="Instant messaging addresses for the User.")
    photos = Attribute(DefaultMultiValueComplex, multivalued=True, description="URLs of photos of the User.")
    addresses = Attribute(DefaultMultiValueComplex, multivalued=True, description="A physical mailing address for this User.")
    groups = Attribute(MultiValueReference, multivalued=True, description="A list of groups to which the user belongs, either through direct membership, nested groups, or dynamically calculated.")
    entitlements = Attribute(DefaultMultiValueComplex, multivalued=True, description="A list of entitlements for the User that represent a thing the User has.")
    roles = Attribute(DefaultMultiValueComplex, multivalued=True, description="A list of roles for the User that collectively represent who the User is, e.g., 'Student', 'Faculty'.")
    x509Certificates = Attribute(BinaryMultiValueComplex, multivalued=True, description="A list of certificates issued to the User.")


class Manager(ComplexBase):
    """Complex attribute for the manager of a user"""
    value = Attribute(Reference, description="The id of of the SCIM resource representing representing the user's manager.")
    displayName = Attribute(String, description="The displayName of the user's manager.")
    ref = Attribute(Reference, name="$ref", mutability="readOnly", description="The URI of the SCIM resource representing the user's manager.")


class EnterpriseUser(Extension):

    class ScimInfo(User.ScimInfo):
        name = "EnterpriseUser"
        description = "Enterprise User Account"
        schema = "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"

    employeeNumber = Attribute(String, description="A string identifier, typically numeric or alphanumeric, assigned to a person, typically based on order of hire or association with an organization.")
    costCenter = Attribute(String, description="Identifies the name of a cost center.")
    organization = Attribute(String, description="Identifies the name of an organization.")
    division = Attribute(String, description="Identifies the name of a division.")
    department = Attribute(String, description="Identifies the name of a department.")
    manager = Attribute(Manager, description="The user's manager. A complex type that optionally allows service providers to represent organizational hierarchy by referencing the 'id' attribute of another User.")


# Add EnterpriseUser extension to User
User.enterpriseUser = EnterpriseUser