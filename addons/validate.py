from typing import List, Dict, Tuple, Set, Union, Type, Any
from dataclasses import dataclass
from enum import Enum as PyEnum

_DataTypes = Union[str, int, float, bool]

class DefaultPattern(PyEnum):
    EMAIL = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    USERNAME = r"^[a-zA-Z0-9_]{3,30}$"
    URL = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
    HEX_COLOR = r"^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$"

@dataclass
class Length:
   min: int = 0
   max: int = 255
   message: str = "Length must be between {min} and {max}"

@dataclass
class Range:
   min: Union[int, float] = 0
   max: Union[int, float] = 0
   message: str = "Value must be between {min} and {max}"

@dataclass
class Pattern:
   regex: str
   flags: int
   message: str = "Value does not match the required pattern"

@dataclass   
class Enum:
   values: List[Any]
   message: str = "Value must be one of {values}"
   
@dataclass
class Required:
    message: str = "This field is required"

class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)

@dataclass
class Validation:
   field: str
   rules: Tuple[Any, ...]  # Can include Length, Range, Pattern, Enum, Required
   type: Type[_DataTypes]
   
   def __str__(self):
       return f"<Validation field={self.field} rules={self.rules} type={self.type}>"
   
   def __repr__(self):
       return self.__str__()

class Schema:
    @staticmethod
    def validate(data: Dict[str, Any], schema: List[Validation]) -> str:
        """
        Validate data against the provided schema.
        
        :param data: Dictionary of data to validate.
        :param schema: List of `Validation` rules.
        :raises `ValidationError`: If any validation rule fails.

        Example:
        ```python
        if excep := Schema.validate(
            { "username": "baby_user", "age": 6 },
            [
                Validation(
                    field="username",
                    rules=(Length(min=3, max=30), Required()),
                    type=str
                ),
                Validation(
                    field="age",
                    rules=(Range(min=18, max=100, message="It seems you are a baby"), Required()),
                    type=int
                )
            ]
        ):
            return Response(
                { "success": False, "exception": excep },
                mimetype='application/json',
                status=400
            )
        """
        for rule in schema:
            value = data.get(rule.field)
            
            for r in rule.rules:
                if isinstance(r, Required):
                    if value is None:
                        return r.message
                
                if isinstance(r, Length) and isinstance(value, str):
                    if not (r.min <= len(value) <= r.max):
                        return r.message.format(min=r.min, max=r.max)

                if isinstance(r, Range) and isinstance(value, (int, float)):
                    if not (r.min <= value <= r.max):
                        return r.message.format(min=r.min, max=r.max)

                if isinstance(r, Enum):
                    if value not in r.values:
                        return r.message.format(values=r.values)

                if isinstance(r, Pattern) and isinstance(value, str):
                    import re
                    if not re.match(r.regex, value, r.flags):
                        return r.message

                if not isinstance(value, rule.type) and value is not None:
                    return f"Value must be of type {rule.type.__name__}."
        return ""


class Multipart:
    @staticmethod
    def too_large(content_length: int, max_size: int = 2 * 1024 * 1024, message: str = "File too large") -> str:
        """Check if the file size exceeds the maximum allowed size (default 2MB)."""
        if content_length > max_size:
            return message
        return ""
    
    @staticmethod
    def allowed_file(filename: str, allowed_ext: Set[str], message: str = "File type not allowed") -> str:
        """Check if the file has an allowed extension."""
        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_ext:
            return message
        return ""
