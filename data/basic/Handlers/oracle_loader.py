import cx_Oracle
import os
from typing import List
from model_dataclasses import Person, Address, Phone
from data.basic.generator import generate_people, generate_Address, generate_Phone

cx_Oracle.init_oracle_client(lib_dir=r"E:\Oracle\instantclient_23_0")

# ---------------- ORACLE KAPCSOLAT ----------------
def get_connection() -> cx_Oracle.Connection:
    """Oracle kapcsolat létrehozása"""
    username = input("U_NEPTUN").strip()
    password = input("jelszo").strip()
    dsn = "egyetemi szerver"  # Egyetemi szerver DSN
    return cx_Oracle.connect(user="U_NEPTUN", password="jelszo", dsn="egyetemi szerver")


# ---------------- TÁBLA LÉTREHOZÁS ----------------
def create_tables(conn: cx_Oracle.Connection):
    cur = conn.cursor()

    # ---- TÁBLÁK TÖRLÉSE, ha léteznek ----
    tables = ["PHONE", "ADDRESS", "PERSON"]
    for t in tables:
        try:
            cur.execute(f"DROP TABLE {t} CASCADE CONSTRAINTS PURGE")
        except cx_Oracle.DatabaseError:
            pass

    # ---- PERSON ----
    cur.execute("""
        CREATE TABLE PERSON
        (
            PERSON_ID   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            EXTERNAL_ID VARCHAR2(20) UNIQUE,
            NAME        VARCHAR2(200) NOT NULL,
            AGE         NUMBER,
            MALE        NUMBER(1) CHECK (MALE IN (0,1))
        )
    """)

    # ---- ADDRESS ----
    cur.execute("""
        CREATE TABLE ADDRESS
        (
            ADDRESS_ID  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            EXTERNAL_ID VARCHAR2(20) UNIQUE,
            STREET_NAME VARCHAR2(200),
            CITY        VARCHAR2(100),
            POSTAL_CODE VARCHAR2(50),
            PERSON_ID   NUMBER UNIQUE,
            CONSTRAINT FK_ADDRESS_PERSON FOREIGN KEY (PERSON_ID)
                REFERENCES PERSON (PERSON_ID)
        )
    """)

    # ---- PHONE ----
    cur.execute("""
        CREATE TABLE PHONE
        (
            PHONE_ID     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            EXTERNAL_ID  VARCHAR2(20) UNIQUE,
            PHONE_NUMBER VARCHAR2(100),
            TYPE         VARCHAR2(50),
            PERSON_ID    NUMBER,
            CONSTRAINT FK_PHONE_PERSON FOREIGN KEY (PERSON_ID)
                REFERENCES PERSON (PERSON_ID)
        )
    """)

    conn.commit()
    cur.close()

# ---------------- ADAT BESZÚRÁS ----------------
def insert_data(conn: cx_Oracle.Connection, count: int = 10):
    """Adatok generálása és beszúrása"""

    # --- ADAT GENERÁLÁS ---
    people = generate_people(count)
    addresses = generate_Address(count)
    phones = generate_Phone(count)

    cur = conn.cursor()

    # --- PERSON BESZÚRÁS ---
    person_sql = """
                 INSERT INTO PERSON (EXTERNAL_ID, NAME, AGE, MALE)
                 VALUES (:1, :2, :3, :4) \
                 """
    person_data = [(p.id, p.name, p.age, 1 if p.male else 0) for p in people]
    cur.executemany(person_sql, person_data)

    # Person ID-k lekérése
    cur.execute("SELECT PERSON_ID, EXTERNAL_ID FROM PERSON")
    person_map = {ext_id: pid for pid, ext_id in cur.fetchall()}

    # --- ADDRESS BESZÚRÁS ---
    address_sql = """
                  INSERT INTO ADDRESS (EXTERNAL_ID, STREET_NAME, CITY, POSTAL_CODE, PERSON_ID)
                  VALUES (:1, :2, :3, :4, :5) \
                  """

    address_data = []
    used_person_ids = set()

    for i, address in enumerate(addresses):
        # Ha NINCS person_external_id → kössük az i. emberhez
        if hasattr(address, "person_external_id") and address.person_external_id:
            person_id = person_map.get(address.person_external_id)
        else:
            person_id = person_map.get(people[i].id)

        # 1:1 biztosítása
        if person_id not in used_person_ids:
            address_data.append((
                address.id,
                address.street_name,
                address.city,
                address.postal_code,
                person_id
            ))
            used_person_ids.add(person_id)

    cur.executemany(address_sql, address_data)

    # --- PHONE BESZÚRÁS ---
    phone_sql = """
                INSERT INTO PHONE (EXTERNAL_ID, PHONE_NUMBER, TYPE, PERSON_ID)
                VALUES (:1, :2, :3, :4) \
                """

    phone_data = []
    for i, phone in enumerate(phones):

        if hasattr(phone, "person_external_id") and phone.person_external_id:
            person_id = person_map.get(phone.person_external_id)
        else:
            person_id = person_map.get(people[i].id)

        # Ha nem None, akkor beírjuk
        phone_data.append((
            phone.id,
            phone.number,
            phone.type,
            person_id
        ))

    cur.executemany(phone_sql, phone_data)

    conn.commit()
    cur.close()



    print(f"Adatbázis feltöltve: {len(person_data)} személy, {len(address_data)} cím, {len(phone_data)} telefon")

# ---------------- ADATOK KIOLVASÁSA ----------------
def read_all(conn):
    cur = conn.cursor()

    print("=" * 50)
    print("PERSON tábla tartalma")
    print("=" * 50)
    cur.execute("SELECT PERSON_ID, EXTERNAL_ID, NAME, AGE, MALE FROM PERSON")
    for row in cur.fetchall():
        print(row)

    print("=" * 50)
    print("ADDRESS tábla tartalma")
    print("=" * 50)
    cur.execute("SELECT ADDRESS_ID, EXTERNAL_ID, STREET_NAME, CITY, POSTAL_CODE, PERSON_ID FROM ADDRESS")
    for row in cur.fetchall():
        print(row)

    print("=" * 50)
    print("PHONE tábla tartalma")
    print("=" * 50)
    cur.execute("SELECT PHONE_ID, EXTERNAL_ID, PHONE_NUMBER, TYPE, PERSON_ID FROM PHONE")
    for row in cur.fetchall():
        print(row)

    cur.close()