"Database layer - next time use SQLAlchemy"
import mysql.connector
import config

def list_employees():
    "Select all the employees from the database"
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT id, object_key, full_name, location, job_title, badges
        FROM employee
        ORDER BY full_name desc""")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def load_employee(employee_id):
    "Select one the employee from the database"
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT id, object_key, full_name, location, job_title, badges
        FROM employee
        WHERE id = %(emp)s;""", {'emp': employee_id})
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def add_employee(object_key, full_name, location, job_title, badges):
    "Add an employee to the database"
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""INSERT INTO employee (object_key, full_name, location, job_title, badges)
     VALUES (%s, %s, %s, %s, %s);""", (object_key, full_name, location, job_title, badges))
    conn.commit()
    cursor.close()
    conn.close()

def update_employee(employee_id, object_key, full_name, location, job_title, badges):
    "Update an employee to the database"
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)


    if object_key:
        cursor.execute("""
            UPDATE employee SET
            object_key=%s, full_name=%s, location=%s, job_title=%s, badges=%s
            WHERE id = %s;
         """, (object_key, full_name, location, job_title, badges, employee_id))
    else:
        # if no object key is supplied, don't update it
        cursor.execute("""
            UPDATE employee SET
            full_name=%s, location=%s, job_title=%s, badges=%s
            WHERE id = %s;
         """, (full_name, location, job_title, badges, employee_id))

    conn.commit()
    cursor.close()
    conn.close()

def delete_employee(employee_id):
    "Delete an employee."
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM employee WHERE id = %(emp)s;""", {'emp': employee_id})
    conn.commit()
    cursor.close()
    conn.close()

def get_database_connection():
    "Build a database connection"
    conn = mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                   host=config.DATABASE_HOST,
                                   database=config.DATABASE_DB_NAME,
                                   use_pure=True) # see https://bugs.mysql.com/90585
    return conn
