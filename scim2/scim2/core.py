from .base import Attribute, Complex, Extension, ResourceType
from .datatypes import *

class Name(Complex):
    """Complex attribute for the name of a user"""
    formatted = Attribute(String, description="The full name, including all middle names, titles, and suffixes as appropriate, formatted for display (e.g., 'Ms. Barbara J Jensen, III').")
    familyName = Attribute(String, description="The family name of the User, or last name in most Western languages (e.g., 'Jensen' given the full name 'Ms. Barbara J Jensen, III').")
    givenName = Attribute(String, description="The given name of the User, or first name in most Western languages (e.g., 'Barbara' given the full name 'Ms. Barbara J Jensen, III').")
    middleName = Attribute(String, description="The middle name(s) of the User (e.g., 'Jane' given the full name 'Ms. Barbara J Jensen, III').")
    honorificPrefix = Attribute(String, description="The honorific prefix(es) of the User, or title in most Western languages (e.g., 'Ms.' given the full name 'Ms. Barbara J Jensen, III').")
    honorificSuffix = Attribute(String, description="The honorific suffix(es) of the User, or suffix in most Western languages (e.g., 'III' given the full name 'Ms. Barbara J Jensen, III').")


class DefaultMultiValueComplex(Complex):
    """Default format for a multivalue complex attribute"""
    value = Attribute(String, description="attribute value")
    display = Attribute(String, description="A human-readable name, primarily used for display purposes.")
    type = Attribute(String, description="A label indicating the attribute's function, e.g., 'work' or 'home'.")
    primary = Attribute(Boolean, description="A Boolean value indicating the 'primary' or preferred attribute value for this attribute.")


class BinaryMultiValueComplex(DefaultMultiValueComplex):
    """Same as DefaultMultiValueComplex but with binary data"""
    value = Attribute(Binary, description="binary attribute value")


class MultiValueReference(Complex):
    """Default format for a multivalue reference attribute"""
    value = Attribute(Reference, description="Idenitfier of the referenced resource.")
    display = Attribute(String, description="A human-readable name, primarily used for display purposes.")
    type = Attribute(String, description="A label indicating the attribute's function, e.g., 'work' or 'home'.")
    ref = Attribute(Reference, name="$ref", mutability="readOnly", description="URI of the reference resource")


class User(ResourceType):

    class ScimInfo(ResourceType.ScimInfo):
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


class Manager(Complex):
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