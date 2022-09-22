from enum import Enum
from pydantic import BaseModel, Field
from typing import List


class PhoneType(Enum):
    home = "home"
    work = "work"
    mobile = "mobile"


class Phone(BaseModel):
    number: str
    type: PhoneType


class Name(BaseModel):
    first: str
    middle: str
    last: str


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str


class Contact(BaseModel):
    name: Name
    address: Address
    phone: List[Phone]
    email: str
    id: str = None  # Optional

    def get(self):
        output = {
            "id": self.id,
            "name": self.name.__dict__,
            "address": self.address.__dict__,
            "email": self.email,
            "phone": [
                {
                    "number": p.number,
                    "type": p.type.name
                }
                for p in self.phone
            ]
        }
        return output

    def has_home_phone(self):
        # Checks if any of the phone numbers are "home"
        return any("home" == phone.type.name for phone in self.phone)
