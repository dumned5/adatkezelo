from model_classes import Person, Address, Phone
from faker import Faker
import random as rnd


def generate_people(n: int, male_ratio: float = 0.5, locale: str = "en_US",
                    unique: bool = False, min_age: int = 0, max_age: int = 100) -> list[Person]:
    assert n > 0
    assert 0 < male_ratio < 1
    assert min_age >= 0

    fake = Faker(locale)
    people = []

    for i in range(n):
        male = rnd.random() < male_ratio
        generator = fake if not unique else fake.unique
        people.append(Person(
            "P-" + (str(i).zfill(6)),
            generator.name_male() if male else generator.name_female(),
            rnd.randint(min_age, max_age + 1),
            male))

    return people

def generate_Address(n: int, locale: str = "en_US", unique: bool = False) -> list[Address]:
    assert n > 0

    fake = Faker(locale)
    addresses = []

    for i in range(n):
        generator = fake if not unique else fake.unique

        street_name = generator.street_name()
        city = generator.city()
        postal_code = generator.postcode()

        addresses.append(Address(
            "AD-" + (str(i).zfill(6)),
            street_name,
            city,
            postal_code,

        ))
    return addresses

def generate_Phone(n: int, locale: str = "en_US", unique: bool = False) -> list[Phone]:
    assert n > 0

    fake = Faker(locale)
    phones = []
    phone_types = ['mobile', 'home', 'work', 'office', 'cell']


    for i in range(n):
        generator = fake if not unique else fake.unique

        number = generator.phone_number()
        phone_type = rnd.choice(phone_types)

        phones.append(Phone(
        "PH-" + (str(i).zfill(6)),
        number,
        phone_type
        ))
    return phones