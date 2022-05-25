import os

import mysql.connector


def db_connect():
    return mysql.connector.connect(option_files="db.conf")


def select_by_discord_id(discord_id: int):
    sql = f"SELECT * FROM users WHERE discord_id = {discord_id}"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    db_connection.close()
    return data


def select_by_osu_id(osu_id: int):
    sql = f"SELECT * FROM users WHERE osu_id = {osu_id}"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    db_connection.close()
    return data


def insert_user(discord_name: str, osu_username: str, discord_tag: int, medals: int, osu_id: int, discord_id: int):
    sql = "INSERT INTO users (id, discord_name, osu_name, discord_tag, medals, osu_id, discord_id) " \
          f"VALUES (NULL, '{discord_name}', '{osu_username}','{discord_tag}', {medals}, {osu_id}, {discord_id});"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    db_connection.commit()
    rows = cursor.rowcount
    cursor.close()
    db_connection.close()
    return rows


def update_user(discord_id: int, discord_username: str, discord_tag: str, osu_username: str):
    sql = f"UPDATE users SET discord_name='{discord_username}', discord_tag='{discord_tag}', " \
          f"osu_name='{osu_username}' WHERE discord_id = {discord_id};"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(sql)
    db_connection.commit()
    rows = cursor.rowcount
    cursor.close()
    db_connection.close()
    return rows
