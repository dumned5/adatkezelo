import json
import os
from typing import cast
from model_dataclasses import Person, Address, Phone

class JSONHandler:
    def write_json(data: list[Person | Address | Phone]) -> None:
        json_list = [data_item.__dict__ for data_item in data]
        with open('data.json', 'w') as json_file:
            json.dump(json_list, json_file, indent=4)

    def read_json() -> list[Person | Address | Phone]:
        if not os.path.exists('data.json'):
            return []
        with open('data.json', 'r') as json_file:
            json_list = json.load(json_file)
            result: list[Person | Address | Phone] = []
            for item in json_list:
                if 'age' in item:
                    result.append(cast(Person, Person(**item)))
                elif 'street_name' in item:
                    result.append(cast(Address, Address(**item)))
                elif 'number' in item:
                    result.append(cast(Phone, Phone(**item)))
            return result