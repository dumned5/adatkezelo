import os
import pandas as pd
import openpyxl
from model_dataclasses import Person, Address, Phone


class XLSXHandler:
    @staticmethod
    def write_xlsx(persons: list[Person], addresses: list[Address], phones: list[Phone], file_path: str) -> None:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            pd.DataFrame([p.__dict__ for p in persons]).to_excel(writer, sheet_name='Persons', index=False)
            pd.DataFrame([a.__dict__ for a in addresses]).to_excel(writer, sheet_name='Addresses', index=False)
            pd.DataFrame([ph.__dict__ for ph in phones]).to_excel(writer, sheet_name='Phones', index=False)
    
    def read_xlsx(file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        workbook = openpyxl.load_workbook(file_path)
        persons, addresses, phones = [], [], []
        sheet = workbook.active

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if sheet.title == 'Persons':
                persons.append(Person(*row))
            elif sheet.title == 'Addresses':
                addresses.append(Address(*row))
            elif sheet.title == 'Phones':
                phones.append(Phone(*row))
        workbook.close()
        return persons, addresses, phones

        