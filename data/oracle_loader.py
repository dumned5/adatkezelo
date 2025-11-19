from dataclasses import dataclass, field
import random
from faker import Faker
import cx_Oracle
import os
import pandas as pd
from typing import List, Optional
from model_dataclasses import Person, Address, Phone
from data.basic.generator import generate_people, generate_Address, generate_Phone


# ---------------- ORACLE INIT & CONNECTION ----------------

cx_Oracle.init_oracle_client(lib_dir=r"E:\Oracle\instantclient_23_0")

DEFAULT_DSN = "egyetem szerver"

def get_conn_from_prompt() -> cx_Oracle.Connection:
    """Bekéri a felhasználónevet és jelszót futás közben és létrehoz egy kapcsolatot."""
    username = input("U_Neptun").strip()
    password = input("jelszo").strip()
    dsn = os.environ.get("ORACLE_DSN", DEFAULT_DSN)
    return cx_Oracle.connect(user="U_NEPTUN", password="jelszo", dsn="egyetem szerver")

# ---------------- DDL: tábla létrehozása/törlése ----------------
def drop_tables(conn: cx_Oracle.Connection):
    cur = conn.cursor()
    tables = ["PHONE", "ADDRESS", "PERSON"]
    for t in tables:
        try:
            cur.execute(f"DROP TABLE {t} PURGE")
            print(f"Dropped {t}")
        except cx_Oracle.DatabaseError:
            pass
    conn.commit()
    cur.close()

def create_tables(conn: cx_Oracle.Connection):
    cur = conn.cursor()
    # PERSON
    cur.execute("""
        CREATE TABLE PERSON (
            PERSON_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            EXTERNAL_ID VARCHAR2(20) UNIQUE,
            NAME VARCHAR2(200) NOT NULL,
            AGE NUMBER,
            MALE NUMBER(1) CHECK (MALE IN (0,1))
        )
    """)
    # ADDRESS (1:1 -> PERSON_ID UNIQUE)
    cur.execute("""
        CREATE TABLE ADDRESS (
            ADDRESS_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            EXTERNAL_ID VARCHAR2(20) UNIQUE,
            STREET_NAME VARCHAR2(200),
            CITY VARCHAR2(100),
            POSTAL_CODE VARCHAR2(50),
            PERSON_ID NUMBER UNIQUE,
            CONSTRAINT FK_ADDRESS_PERSON FOREIGN KEY (PERSON_ID) REFERENCES PERSON(PERSON_ID)
        )
    """)
    # PHONE (1:N -> many phones may reference same PERSON_ID)
    cur.execute("""
        CREATE TABLE PHONE (
            PHONE_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            EXTERNAL_ID VARCHAR2(20) UNIQUE,
            PHONE_NUMBER VARCHAR2(100),
            TYPE VARCHAR2(50),
            PERSON_ID NUMBER,
            CONSTRAINT FK_PHONE_PERSON FOREIGN KEY (PERSON_ID) REFERENCES PERSON(PERSON_ID)
        )
    """)
    conn.commit()
    cur.close()
    print("Tables created: PERSON, ADDRESS, PHONE")

# ---------------- INSERT helper-ek ----------------
def insert_persons(conn: cx_Oracle.Connection, people: List[Person]):
    cur = conn.cursor()
    sql = "INSERT INTO PERSON (EXTERNAL_ID, NAME, AGE, MALE) VALUES (:1, :2, :3, :4)"
    data = [(p.id, p.name, p.age if p.age is not None else None, 1 if p.male else 0) for p in people]
    cur.executemany(sql, data)
    conn.commit()
    cur.close()
    print(f"{len(data)} személy beszúrva.")

def fetch_person_id_map(conn: cx_Oracle.Connection) -> dict:
    """Visszaadja: external_id -> PERSON_ID (int) map-ot."""
    cur = conn.cursor()
    cur.execute("SELECT PERSON_ID, EXTERNAL_ID FROM PERSON")
    mapping = {row[1]: int(row[0]) for row in cur.fetchall() if row[1] is not None}
    cur.close()
    return mapping

def insert_addresses(conn: cx_Oracle.Connection, addresses: List[Address], person_map: dict):
    cur = conn.cursor()
    sql = "INSERT INTO ADDRESS (EXTERNAL_ID, STREET_NAME, CITY, POSTAL_CODE, PERSON_ID) VALUES (:1,:2,:3,:4,:5)"
    data = []
    # Determine available person_ids for random assignment if no explicit mapping provided
    available_person_ids = list(person_map.values())
    for a in addresses:
        # if CSV includes person_external_id and it's known, use it; else choose random person
        person_id = None
        if getattr(a, "person_external_id", None):
            person_id = person_map.get(a.person_external_id)
        if person_id is None and available_person_ids:
            # ensure 1:1 -> pick a person without an address yet
            # So first we will query which persons already have addresses; but simpler: we try to assign unique persons here
            person_id = available_person_ids.pop(random.randrange(len(available_person_ids)))
        data.append((a.id, a.street_name, a.city, a.postal_code, person_id))
    cur.executemany(sql, data)
    conn.commit()
    cur.close()
    print(f"{len(data)} cím beszúrva (PERSON_ID-ok beállítva, ahol lehetséges).")

def insert_phones(conn: cx_Oracle.Connection, phones: List[Phone], person_map: dict):
    cur = conn.cursor()
    sql = "INSERT INTO PHONE (EXTERNAL_ID, PHONE_NUMBER, TYPE, PERSON_ID) VALUES (:1,:2,:3,:4)"
    data = []
    available_person_ids = list(person_map.values())
    for ph in phones:
        person_id = None
        if getattr(ph, "person_external_id", None):
            person_id = person_map.get(ph.person_external_id)
        if person_id is None and available_person_ids:
            # For phones we allow multiple phones per person -> choose random person (not removing)
            person_id = random.choice(available_person_ids)
        data.append((ph.id, ph.number, ph.type, person_id))
    cur.executemany(sql, data)
    conn.commit()
    cur.close()
    print(f"{len(data)} telefon beszúrva (PERSON_ID-ok beállítva, ahol lehetséges).")

"""# ---------------- CSV loader (project CSV-ekhez igazítva) ----------------
def read_people_csv(path: str) -> List[Person]:
    df = pd.read_csv(path, dtype=str).fillna("")
    out = []
    for _, r in df.iterrows():
        # CSV expected columns: id, name, age, male
        age_val = int(r.get("age")) if str(r.get("age")).strip() != "" else None
        male_val = 1 if str(r.get("male")).lower() in ("true", "1", "yes") else 0
        out.append(PersonDC(r.get("id"), r.get("name"), age_val, male_val==1))
    return out

def read_addresses_csv(path: str) -> List[AddressDC]:
    df = pd.read_csv(path, dtype=str).fillna("")
    out = []
    # Expected columns in original generator: id, street_name, city, postal_code
    # Optionally a person_external_id column can be present to link addresses to persons.
    for _, r in df.iterrows():
        out.append(AddressDC(
            id=r.get("id"),
            street_name=r.get("street_name", ""),
            city=r.get("city", ""),
            postal_code=r.get("postal_code", ""),
            person_external_id=r.get("person_external_id") if "person_external_id" in r.index else None
        ))
    return out

def read_phones_csv(path: str) -> List[PhoneDC]:
    df = pd.read_csv(path, dtype=str).fillna("")
    out = []
    # Expected columns: id, number, type
    for _, r in df.iterrows():
        out.append(PhoneDC(
            id=r.get("id"),
            number=r.get("number", ""),
            type=r.get("type", ""),
            person_external_id=r.get("person_external_id") if "person_external_id" in r.index else None
        ))
    return out
"""
# ---------------- MAIN LOADER (folder alapértelmezett) ----------------
DEFAULT_CSV_FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "generated_data")
DEFAULT_CSV_FOLDER = os.path.normpath(DEFAULT_CSV_FOLDER)

def load_all_from_csv_folder(conn: cx_Oracle.Connection, folder: Optional[str] = None, create_tables_flag: bool = False):
    if folder is None:
        folder = DEFAULT_CSV_FOLDER
    people_file = os.path.join(folder, "people.csv")
    addresses_file = os.path.join(folder, "addresses.csv")
    phones_file = os.path.join(folder, "phones.csv")

    if create_tables_flag:
        try:
            drop_tables(conn)
        except Exception:
            pass
        create_tables(conn)

    people = read_people_csv(people_file)
    addresses = read_addresses_csv(addresses_file)
    phones = read_phones_csv(phones_file)

    insert_persons(conn, people)
    person_map = fetch_person_id_map(conn)  # external_id -> PERSON_ID
    insert_addresses(conn, addresses, person_map)
    insert_phones(conn, phones, person_map)

# ---------------- READ BACK helpers ----------------
def read_persons_from_db(conn: cx_Oracle.Connection) -> List[PersonDC]:
    cur = conn.cursor()
    cur.execute("SELECT EXTERNAL_ID, NAME, AGE, MALE FROM PERSON")
    out = []
    for row in cur.fetchall():
        out.append(PersonDC(row[0], row[1], int(row[2]) if row[2] is not None else None, bool(row[3])))
    cur.close()
    return out

def read_addresses_from_db(conn: cx_Oracle.Connection) -> List[AddressDC]:
    cur = conn.cursor()
    cur.execute("SELECT EXTERNAL_ID, STREET_NAME, CITY, POSTAL_CODE, PERSON_ID FROM ADDRESS")
    out = []
    for row in cur.fetchall():
        out.append(AddressDC(row[0], row[1], row[2], row[3], None))
    cur.close()
    return out

def read_phones_from_db(conn: cx_Oracle.Connection) -> List[PhoneDC]:
    cur = conn.cursor()
    cur.execute("SELECT EXTERNAL_ID, PHONE_NUMBER, TYPE, PERSON_ID FROM PHONE")
    out = []
    for row in cur.fetchall():
        out.append(Phone(row[0], row[1], row[2], None))
    cur.close()
    return out

# ---------------- RUN EXAMPLE ----------------
if __name__ == "__main__":
    print("Oracle loader (Person / Address / Phone) — használat: futtasd, add meg a felhasználót/jelszót, majd a mappa helyét (opcionális).")
    conn = get_conn_from_prompt()
    folder = input(f"Add meg a CSV mappa elérési útját (üres = default {DEFAULT_CSV_FOLDER}): ").strip() or None
    create_flag_input = input("Létrehozza a táblákat? (y/N): ").strip().lower()
    create_flag = create_flag_input in ("y", "yes")
    load_all_from_csv_folder(conn, folder, create_flag)
    print("Beolvasás után kiírom röviden a táblák tartalmát:")
    print("Persons:", read_persons_from_db(conn))
    print("Addresses:", read_addresses_from_db(conn)[:5])
    print("Phones:", read_phones_from_db(conn)[:5])
    conn.close()