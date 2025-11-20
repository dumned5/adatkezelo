from data.basic.generator import generate_people, generate_Address, generate_Phone
from model_classes import Person, Address, Phone
from data.basic.Handlers.csv_handler import CSVHandler
from data.basic.Handlers.json_handler import JSONHandler
from data.basic.Handlers.xlsx_handler import XLSXHandler
from data.basic.Handlers.oracle_loader import get_connection, create_tables, insert_data, read_all


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
    print(generate_Phone(5, "hu_HU", True))
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
    print("=" * 50)
    print("TESTING JSONHHANDLER CLASS")
    print("=" * 50)

    JSONHandler.write_json(people + addresses + phones)
    readed_json = JSONHandler.read_json()
    print(readed_json)

    print("=" * 50)
    print("TESTING XLSXHHANDLER CLASS")
    print("=" * 50)
    XLSXHandler.write_xlsx(
        people,
        addresses,
        phones,
        "data.xlsx")

    readed_xlsx = XLSXHandler.read_xlsx("data.xlsx")
    print(readed_xlsx)


print("=" * 50)
print("TESTING ORACLE_LOADER")
print("=" * 50)

conn = get_connection()
create_tables(conn)
insert_data(conn, 10)
read_all(conn)
conn.close()

if __name__ == "__main__":
    main()