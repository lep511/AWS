import pymysql
import os

from dotenv import load_dotenv
load_dotenv()

rds_host = os.getenv('DATABASE_HOST')
db_user = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_PASSWORD')
db_name = os.getenv('DATABASE_DB_NAME')
port = 3306
table_name = "customertable"

def create_database(db_name):
    try:
        conn = pymysql.connect(host=rds_host, user=db_user, password=password, connect_timeout=5, charset='utf8mb4')

        mycursor = conn.cursor()

        mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")

        print("done")

    except Exception as e:
        print(f"Failed to create database with following error: {e}")

def create_table(table_name):
    try:
        server_address = (rds_host, port)
        conn = pymysql.connect(host=rds_host, user=db_user, password=password, database=db_name, connect_timeout=5, charset='utf8mb4')

        mycursor = conn.cursor()

        mycursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, borrowerName VARCHAR(255), loanRequested VARCHAR(255), propertyValue VARCHAR(255), propertyAddress VARCHAR(255), loanOfficer VARCHAR(255))")

        print("table created!")
    except Exception as e:
        print(f"Failed to create table with following error: {e}")

def add_data(borrowerName, loanRequested, propertyValue, propertyAddress, loanOfficer):

    try:
        conn = pymysql.connect(host=rds_host, user=db_user, password=password, database=db_name, connect_timeout=5, charset='utf8mb4')

        mycursor = conn.cursor()


        sql = "INSERT INTO customerdata (borrowerName, loanRequested, propertyValue, propertyAddress, loanOfficer) VALUES (%s, %s, %s, %s, %s)"
        val = (borrowerName, loanRequested, propertyValue, propertyAddress, loanOfficer)

        mycursor.execute(sql, val)

        conn.commit()

        print(mycursor.rowcount, "record inserted.")
    except Exception as e:
        print(f"Failed to create table with following error: {e}")



if __name__=="__main__":
    create_database(db_name)
    create_table(table_name)