import csv
from typing import List, Type, TypeVar
import os
from model_dataclasses import Person, Address, Phone



T = TypeVar('T')

class CSVHandler:

    @staticmethod
    def csv_writer(data: list[object], filename: str):
        # Mezőnevek meghatározása (az első objektum attribútumai alapján)
        mezonevek = list(data[0].__dict__.keys())

        with open(filename, 'w', newline='', encoding= 'utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames= mezonevek)
            writer.writeheader()

            for i in data:
                writer.writerow(i.__dict__)
        print(f"{len(data)} elem mentve a {filename} fájlba")

    @staticmethod
    def csv_reader(cls: Type[T], filename: str) -> List[T]:

        lista = []

        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                converted_row = {}
                for field, value in row.items():
                    field_type = cls.__annotations__.get(field, str)
                    try:
                        if field_type == bool:
                            converted_row[field] = value.lower() == 'true'
                        elif field_type == int:
                            converted_row[field] = int(value)
                        else:
                            converted_row[field] = value
                    except (ValueError, AttributeError):
                        converted_row[field] = value
                lista.append(cls(**converted_row))
            print(f"{len(lista)} elem sikeresen beolvasva a {filename} fájlból")

        return lista
