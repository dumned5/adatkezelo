import cx_Oracle
import os
from typing import List
from model_dataclasses import Person, Address, Phone
from generator import generate_people, generate_Address, generate_Phone

# ---------------- ORACLE KAPCSOLAT ----------------
def get_connection() -> cx_Oracle.Connection:
    """Oracle kapcsolat létrehozása"""
    username = input("Neptun kód: ").strip()
    password = input("Jelszó: ").strip()
    dsn = "egyetem szerver"  # Egyetemi szerver DSN
    return cx_Oracle.connect(user=username, password=password, dsn=dsn)

# ---------------- TÁBLA LÉTREHOZÁS ----------------
def create_tables(conn: cx_Oracle.Connection):
    """Táblák létrehozása elsődleges és külső kulcsokkal"""
    cur = conn.cursor()
    
    # PERSON tábla
    cur.execute("""
        CREATE TABLE PERSON (
            PERSON_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            EXTERNAL_ID VARCHAR2(20) UNIQUE,
            NAME VARCHAR2(200) NOT NULL,
            AGE NUMBER,
            MALE NUMBER(1) CHECK (MALE IN (0,1))
        )
    """)
    
    # ADDRESS tábla (1:1 kapcsolat)
    cur.execute("""
        CREATE TABLE ADDRESS (
            ADDRESS_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            EXTERNAL_ID VARCHAR2(20) UNIQUE,
            STREET_NAME VARCHAR2(200),
            CITY VARCHAR2(100),
            POSTAL_CODE VARCHAR2(50),
            PERSON_ID NUMBER UNIQUE,
            CONSTRAINT FK_ADDRESS_PERSON FOREIGN KEY (PERSON_ID) 
                REFERENCES PERSON(PERSON_ID)
        )
    """)
    
    # PHONE tábla (1:N kapcsolat)
    cur.execute("""
        CREATE TABLE PHONE (
            PHONE_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            EXTERNAL_ID VARCHAR2(20) UNIQUE,
            PHONE_NUMBER VARCHAR2(100),
            TYPE VARCHAR2(50),
            PERSON_ID NUMBER,
            CONSTRAINT FK_PHONE_PERSON FOREIGN KEY (PERSON_ID) 
                REFERENCES PERSON(PERSON_ID)
        )
    """)
    
    conn.commit()
    cur.close()

# ---------------- ADAT BESZÚRÁS ----------------
def insert_data(conn: cx_Oracle.Connection, count: int = 10):
    """Adatok generálása és beszúrása"""
    # Adatok generálása
    people = generate_people(count)
    addresses = generate_Address(count, people)
    phones = generate_Phone(count, people)
    
    cur = conn.cursor()
    
    # Person beszúrás
    person_sql = "INSERT INTO PERSON (EXTERNAL_ID, NAME, AGE, MALE) VALUES (:1, :2, :3, :4)"
    person_data = [(p.id, p.name, p.age, 1 if p.male else 0) for p in people]
    cur.executemany(person_sql, person_data)
    
    # Person ID-k lekérése
    cur.execute("SELECT PERSON_ID, EXTERNAL_ID FROM PERSON")
    person_map = {ext_id: person_id for person_id, ext_id in cur.fetchall()}
    
    # Address beszúrás
    address_sql = """INSERT INTO ADDRESS (EXTERNAL_ID, STREET_NAME, CITY, POSTAL_CODE, PERSON_ID) 
                     VALUES (:1, :2, :3, :4, :5)"""
    address_data = []
    used_person_ids = set()
    
    for address in addresses:
        person_id = None
        if hasattr(address, 'person_external_id') and address.person_external_id:
            person_id = person_map.get(address.person_external_id)
        
        # 1:1 kapcsolat - minden person csak egy addresssel
        if person_id and person_id not in used_person_ids:
            address_data.append((address.id, address.street_name, address.city, 
                               address.postal_code, person_id))
            used_person_ids.add(person_id)
    
    if address_data:
        cur.executemany(address_sql, address_data)
    
    # Phone beszúrás
    phone_sql = """INSERT INTO PHONE (EXTERNAL_ID, PHONE_NUMBER, TYPE, PERSON_ID) 
                   VALUES (:1, :2, :3, :4)"""
    phone_data = []
    
    for phone in phones:
        person_id = None
        if hasattr(phone, 'person_external_id') and phone.person_external_id:
            person_id = person_map.get(phone.person_external_id)
        
        if person_id:
            phone_data.append((phone.id, phone.number, phone.type, person_id))
    
    if phone_data:
        cur.executemany(phone_sql, phone_data)
    
    conn.commit()
    cur.close()
    
    print(f"Adatbázis feltöltve: {len(person_data)} személy, {len(address_data)} cím, {len(phone_data)} telefon")
