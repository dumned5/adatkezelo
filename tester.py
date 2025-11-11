from data.basic.generator import generate_people, generate_Address, generate_Phone
from model_classes import Person, Address, Phone
from data.basic.Handlers.csv_handler import CSVHandler

def main():
    print("=" * 50)
    print("TESTING PERSON_GENERATOR CLASS")
    print("=" * 50)
    print(generate_people(5, 0.5, "hu_HU", True, 18, 90))
    print("=" * 50)
    print("TESTING ADRESS_GENERATOR CLASS")
    print("=" * 50)
    print(generate_Address(5, "hu_HU", True))
    print("=" * 50)
    print("TESTING PHONE_GENERATOR CLASS")
    print("=" * 50)
    print(generate_Phone(5,"hu_HU", True))
    print("=" * 50)
    print("TESTING CSVHANLDER CLASS")
    print("=" * 50)
    people = generate_people(3)
    addresses = generate_Address(3)
    phones = generate_Phone(3)

    CSVHandler.csv_writer(people, "people.csv")
    CSVHandler.csv_writer(addresses, "addresses.csv")
    CSVHandler.csv_writer(phones, "phones.csv")

    people_from_csv = CSVHandler.csv_reader(Person, "people.csv")
    addresses_from_csv = CSVHandler.csv_reader(Address, "addresses.csv")
    phones = CSVHandler.csv_reader(Phone, "phones.csv")
if __name__ == "__main__":
    main()