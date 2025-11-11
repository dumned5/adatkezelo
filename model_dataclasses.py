from dataclasses import dataclass, field




@dataclass
class Person:
    id: str = field(hash= True, compare= True)
    name: str = field(repr = True, compare= False)
    age: int = field(repr = True, compare=False)
    male: bool = field(default=True, repr= True, compare= False)

@dataclass(repr = True, order = False, frozen = True)
class Address:
    id: str
    street_name: str
    city: str
    postal_code: str

@dataclass (repr = True, order = False, frozen= True)
class Phone:
    id: str
    number: str
    type: str