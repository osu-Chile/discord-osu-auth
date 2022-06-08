import mysql.connector


def db_connect():
    return mysql.connector.connect(option_files="db.conf")


def select_by_discordid(discordid: int):
    parameters = [discordid]
    sql = f"SELECT * FROM users WHERE discordid = %s"

    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql, parameters)
    data = cursor.fetchone()

    cursor.close()
    db_connection.close()
    return data


def select_by_osuid(osuid: int):
    parameters = [osuid]
    sql = f"SELECT * FROM users WHERE osuid = %s"

    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql, parameters)
    data = cursor.fetchone()

    cursor.close()
    db_connection.close()
    return data


def insert_user(discordname: str, osuname: str, discordtag: str, medals: int, osuid: int, discordid: int):
    parameters = [discordname, osuname, discordtag, medals, osuid, discordid]
    sql = "INSERT INTO users (id, discordname, osuname, discordtag, medals, osuid, discordid) " \
          "VALUES (NULL, %s, %s, %s, %s, %s, %s);"

    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql, parameters)
    db_connection.commit()
    rows = cursor.rowcount

    cursor.close()
    db_connection.close()
    return rows


def update_user(discordid: int, discordname: str, discordtag: str, osuname: str):
    parameters = [discordname, discordtag, osuname, discordid]
    sql = "UPDATE users SET discordname = %s, discordtag = %s, osuname = %s WHERE discordid = %s;"

    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql, parameters)
    db_connection.commit()
    rows = cursor.rowcount

    cursor.close()
    db_connection.close()
    return rows


def delete_by_userid(discordid: int):
    parameters = [discordid]
    sql = f"DELETE FROM users WHERE discordid = %s"

    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql, parameters)
    db_connection.commit()
    rows = cursor.rowcount

    cursor.close()
    db_connection.close()
    return rows
