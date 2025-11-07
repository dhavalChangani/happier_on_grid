"""OnGrid enumeration types"""

from enum import Enum


class VerificationDocType(str, Enum):
    """OnGrid Verification Document Types"""

    PANV = "pan"
    EDUV = "edu"
    EMPV = "emp"
    PRC = "prc"
    BAV = "ba"
    EHC = "ehc"


class Gender(str, Enum):
    """Gender options"""

    MALE = "M"
    FEMALE = "F"
    TRANSGENDER = "T"
    OTHER = "O"
    UNSPECIFIED = "U"


class FileDataType(str, Enum):
    """File data types for document uploads"""

    URL = "Url"
    BINARY = "Binary"
    BASE64 = "Base64"
