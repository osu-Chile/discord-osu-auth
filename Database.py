import mysql.connector


def db_connect():
    return mysql.connector.connect(option_files="db.conf")


def select_by_discordid(discordid: int):
    sql = f"SELECT * FROM users WHERE discordid = {discordid}"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    db_connection.close()
    return data


def select_by_osuid(osuid: int):
    sql = f"SELECT * FROM users WHERE osuid = {osuid}"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    db_connection.close()
    return data


def insert_user(discordname: str, osuname: str, discordtag: str, medals: int, osuid: int, discordid: int):
    sql = "INSERT INTO users (id, discordname, osuname, discordtag, medals, osuid, discordid) " \
          f"VALUES (NULL, '{discordname}', '{osuname}','{discordtag}', {medals}, {osuid}, {discordid});"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    db_connection.commit()
    rows = cursor.rowcount
    cursor.close()
    db_connection.close()
    return rows


def update_user(discordid: int, discordname: str, discordtag: str, osuname: str):
    sql = f"UPDATE users SET discordname='{discordname}', discordtag='{discordtag}', " \
          f"osuname='{osuname}' WHERE discordid = {discordid};"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    db_connection.commit()
    rows = cursor.rowcount
    cursor.close()
    db_connection.close()
    return rows


def delete_by_userid(discordid: int):
    sql = f"DELETE FROM users WHERE discordid = {discordid}"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    db_connection.commit()
    rows = cursor.rowcount
    cursor.close()
    db_connection.close()
    return rows
