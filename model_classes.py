class Person:
    id: str
    name: str
    age: int
    male: bool

    def __str__(self):
        return "#{0}: {1} ({2}, {3})".format(self.id, self.name, self.age, self.male)
    
    def __init__(self, id: str, name: str, age: int, male: bool= True) -> None:
        self.id = id
        self.name = name
        self.age = age
        self.male = male
    
    def __eq__(self, o: object):
        return isinstance(o, Person) and self.id == o.id
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return id.__hash__()


class Address:
    id: str
    street: str
    city: str
    postal_code: int

    def __str__(self):
        return "#{0}: {1}, {2} ({3})".format(self.id, self.street, self.city, self.postal_code)
    
    def __init__(self, id: str, street: str, city: str, postal_code: int):
        self.id = id
        self.street = street
        self.city = city
        self.postal_code = postal_code

    def __eq__(self, o: object):
        return isinstance(o, Address) and self.id == o.id
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return id.__hash__()
    
class Phone:
    id: str
    number: str
    type: str

    def __str__(self):
        return "#{0}: {1} ({2})".format(self.id, self.number, self.type)
    
    def __init__(self, id: str, number: str, type: str):
        self.id = id
        self.number = number
        self.type = type

    def __eq__(self, o: object):
        return isinstance(o, Phone) and self.id == o.id
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return id.__hash__()
