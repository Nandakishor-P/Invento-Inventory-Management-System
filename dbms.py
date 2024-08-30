import psycopg2

def create_database():
    try:
        conn = psycopg2.connect(database="Project", user="nanda", password="nanda", host="localhost", port="5432")
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("DROP DATABASE IF EXISTS Project")
        cur.execute("CREATE DATABASE Project")
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

def create_tables():
    try:
        conn = psycopg2.connect(database="Project", user="nanda", password="nanda", host="localhost", port="5432")
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE Person (
                person_id SERIAL PRIMARY KEY,
                phone_no bigint,
                name VARCHAR(50),
                email VARCHAR(50)
                password varchar(50)
            );

            CREATE TABLE Customer (
                customer_id SERIAL PRIMARY KEY,
                person_id INT REFERENCES Person(person_id)
                password varchar(50)
            );

            CREATE TABLE Supplier (
                supplier_id SERIAL PRIMARY KEY,
                person_id INT REFERENCES Person(person_id)
                password varchar(50)
            );

            CREATE TABLE Product (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(50),
                price DECIMAL,
            );

            CREATE TABLE Sales_Order (
                order_id SERIAL PRIMARY KEY,
                customer_id INT REFERENCES Customer(customer_id),
                order_date DATE
            );

            CREATE TABLE Order_Product (
                order_id INT REFERENCES Sales_Order(order_id),
                product_id INT REFERENCES Product(product_id),
                quantity INT,
                PRIMARY KEY (order_id, product_id)
            );
        ''')

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error creating tables: {e}")

create_database()
create_tables()
