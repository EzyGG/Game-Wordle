import mysql.connector


connection: mysql.connector.connection.MySQLConnection = None
cursor = None


class DatabaseConnexionError(Exception):
    def __init__(self):
        super().__init__("Cannot connect to the database")


def connexion():
    global connection, cursor
    try:
        connection = mysql.connector.connect(host="luzog.xyz", user="dev", password="root", database="ezy")
        cursor = connection.cursor()
    except (mysql.connector.errors.InterfaceError, mysql.connector.errors.DatabaseError):
        raise DatabaseConnexionError()


def execute(operation, param: tuple = (), multi: bool = False):
    try:
        return cursor.execute(operation, param, multi)
    except (mysql.connector.errors.InterfaceError, mysql.connector.errors.DatabaseError):
        raise DatabaseConnexionError()


def commit():
    try:
        return connection.commit()
    except (mysql.connector.errors.InterfaceError, mysql.connector.errors.DatabaseError):
        raise DatabaseConnexionError()


def fetch(size: int = None) -> list | tuple:
    try:
        return cursor.fetchall() if size is None else cursor.fetchone() if size == 1 else cursor.fetchmany(size)
    except (mysql.connector.errors.InterfaceError, mysql.connector.errors.DatabaseError):
        raise DatabaseConnexionError()


def close():
    try:
        return connection.close()
    except (mysql.connector.errors.InterfaceError, mysql.connector.errors.DatabaseError):
        raise DatabaseConnexionError()
