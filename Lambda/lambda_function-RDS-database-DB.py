import pymysql
import os

class DB:
    """ Database layer
    """
    def query(self, statement, host,username,password,db_name,port, *positional_parameters):
        conn = conn = pymysql.connect(host=host, user=username, passwd=password, db=db_name, connect_timeout=5)
        
        result = None
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(statement, positional_parameters)
                result = cursor.fetchall()
        finally:
            conn.commit()
            conn.close()
        return result