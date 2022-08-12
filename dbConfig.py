import json
#import sqlite3
#from sqlite3 import Error
import mysql.connector
from mysql.connector import Error


def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        #conn = sqlite3.connect(db_file)
        #conn = sqlite3.connect(db_file)
        conn = mysql.connector.connect(host='us-cdbr-east-06.cleardb.net',
                                         database='heroku_0e73415270b1c3f',
                                         user='bcf7890cfba075',
                                         password='2a36b16d')
        print(conn)
        conn.commit()
        return conn
    except Error as e:
        print(e)

    return conn

def create_table_monitoracao(conn):

    cursor_obj = conn.cursor()

    #table = """ CREATE TABLE IF NOT EXISTS MONITORACAO (
    #        ID INTEGER AUTO_INCREMENT PRIMARY KEY,
    #        Chat_id REAL NOT NULL,
    #        Name CHAR(25) NOT NULL,
    #        Operator CHAR(25),
    #        Variation_number INT
    #    ); """

    table = """CREATE TABLE IF NOT EXISTS MONITORACAO (
              ID INT NOT NULL,
              PRIMARY KEY (ID), 
              Chat_id REAL NOT NULL,
              Name CHAR(25) NOT NULL,
              Operator CHAR(25) NOT NULL,
              Variation_number INT NOT NULL) ENGINE=InnoDB; """

    conn.commit()
    cursor_obj.execute(table)
    print("Tabela Criada")


def insert_monitoracao(conn, monitoracao):

    try:
        cur = conn.cursor()
        cur.execute('''SELECT MAX(ID) FROM MONITORACAO''')
        idAnterior = cur.fetchall()
        novoId = str(idAnterior[0][0])
        #novoId = int(str(idAnterior[0][0]))
        if novoId == 'None':
            novoId = 0
        else:
            novoId = int(novoId)+1

        sql = ''' INSERT INTO MONITORACAO(ID,Chat_id,Name,Operator,Variation_number)
                      VALUES(%s,%s,%s,%s,%s) '''
        cur = conn.cursor()
        cur.execute(sql, (novoId, monitoracao[0], monitoracao[1], monitoracao[2], monitoracao[3]))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False

def excluir_monitoracao(conn, id):
    try:
        cur = conn.cursor()
        #cur.row_factory = sqlite3.Row
        cur.execute("DELETE FROM MONITORACAO WHERE ID = %s", (id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False

def delete_all_table():
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("DROP TABLE MONITORACAO")
        conn.commit()

        return print("Tabela Deletada")
    except Exception as e:
        conn.rollback()
        return False

def consult_table_monitor(conn, message, json_str = True):
    try:

        cur = conn.cursor()
        #cur.row_factory = sqlite3.Row
        cur.execute("SELECT ID, Name, Operator, Variation_number from MONITORACAO where Chat_id = %s",(message,))
        result = cur.fetchall()
        print(len(result))
        tamanhoLista = len(result)

        lista = list(result)

        row_headers = [x[0] for x in cur.description]
        json_data = []
        for rv in result:
            json_data.append(dict(zip(row_headers, rv)))
        return (message, json.dumps(json_data))

        #if json_str:
            #return (message, json.dumps([dict(ix) for ix in result]))

    except Exception as e:
        return e


#if __name__ == '__main__':
#    database = (r"./monitoramento.db")
#    conn = create_connection(database)
#    create_table_monitoracao(conn)
#    consult_table_monitor(conn)

