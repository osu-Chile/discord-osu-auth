import mysql.connector


def db_connect():
    return mysql.connector.connect(
        host="localhost",
        database="osudb",
        user="",
        password="",
        auth_plugin='mysql_native_password'
    )


def select_by_discord_id(discord_id: int):
    sql = f"SELECT * FROM users WHERE discordid = '{discord_id}'"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    db_connection.close()
    return cursor.fetchone()


def select_by_osu_id(osu_id: int):
    sql = f"SELECT * FROM users WHERE osuid = '{osu_id}'"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    db_connection.close()
    return cursor.fetchone()


def insert_user(discord_name: str, osu_username: str, discord_tag: int, medals: int, osu_id: int, discord_id: int):
    sql = "INSERT INTO users (`id`, `discordname`, `osuname`, `discordtag`, `medals`, `osuid`, `discordid`) " \
          f"VALUES (NULL, '{discord_name}', '{osu_username}', {discord_tag}, {medals}, {osu_id}, {discord_id});"
    print(sql)
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    db_connection.commit()
    db_connection.close()
    return cursor.rowcount


def update_user(discord_id: int, discord_username: str, discord_discriminator: str, osu_username: str):
    sql = f"UPDATE users SET discordname='{discord_username}', discordtag='{discord_discriminator}', " \
          f"osuname='{osu_username}' WHERE discordid = '{discord_id}';"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    db_connection.commit()
    db_connection.close()
    return cursor.rowcount
