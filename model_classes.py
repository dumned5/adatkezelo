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
        return hash(self.id)

    def __repr__(self):
        return f"Person(id={self.id}, name='{self.name}', age={self.age}, male='{self.male}') \n"


class Address:
    id: str
    street_name: str
    city: str
    postal_code: str

    def __str__(self):
        return "#{0}: {1}, {2} ({3})".format(self.id, self.street_name, self.city, self.postal_code)
    
    def __init__(self, id: str,city: str, postal_code: str, street_name: str):
        self.id = id
        self.street_name = street_name
        self.city = city
        self.postal_code = postal_code

    def __eq__(self, o: object):
        return isinstance(o, Address) and self.id == o.id
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Address(id={self.id}, city= '{self.city}', postal_code= {self.postal_code}, street name= '{self.street_name}')\n"
    
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
        return hash(self.id)

    def __repr__(self):
        return f"Phone(id= {self.id}, Number = {self.number}, type= '{self.type}')\n"
