import threading
import discord
import mysql.connector
import requests
import re
from discord.utils import get
from discord.ext import commands

from flask import Flask, Response, request
import base64

app = Flask(__name__)


def db_connect():
    return mysql.connector.connect(
        host="localhost",
        database="osudb",
        user="",
        password="",
        auth_plugin='mysql_native_password'
    )


bot = commands.Bot(command_prefix="bot!", intents=discord.Intents.all())


def select_by_discord_id(discord_id: int):
    query = f"SELECT * FROM users WHERE discordid = '{discord_id}'"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(query)
    db_connection.close()
    return cursor.rowcount


def select_by_osu_id(osu_id: int):
    query = f"SELECT * FROM users WHERE osuid = '{osu_id}'"
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(query)
    db_connection.close()
    return cursor.rowcount


def insert_user(discord_name: str, osu_username: str, discord_tag: int, medals: int, osu_id: int, discord_id: int):
    query = "INSERT INTO users (`id`, `discordname`, `osuname`, `discordtag`, `medals`, `osuid`, `discordid`)" \
            f" VALUES (NULL, '{discord_name}', '{osu_username}', {discord_tag}, {medals}, {osu_id}, {discord_id});"
    print(query)
    db_connection = db_connect()
    cursor = db_connection.cursor()
    cursor.execute(query)
    print(f"{cursor.rowcount} row(s) affected.")
    db_connection.commit()
    db_connection.close()


async def register(osu_id, discord_id):
    discord_id_results = select_by_discord_id(discord_id)
    osu_id_results = select_by_osu_id(osu_id)

    guild = bot.get_guild(771221822745477130)
    channel = bot.get_channel(771815223932747786)
    embed = discord.Embed(title="Nueva solicitud",
                          description=f"osu! link: https://osu.ppy.sh/users/{osu_id}\n"
                                      f"discord tag: <@{discord_id}>",
                          color=0xaaaa00)  # make green embed

    await channel.send(embed=embed)
    user = bot.get_user(int(discord_id))
    member = guild.get_member(int(discord_id))

    if osu_id_results == 0:
        print("osu! id not signed up")

        if discord_id_results == 0:
            print("discord id not signed up")
            guild = bot.get_guild(771221822745477130)

            if guild.get_member(int(discord_id)) is not None:
                print("osu! id: " + osu_id)
                print("discord id: " + discord_id)
                print("user is in server")
                roles = guild.get_member(int(discord_id)).roles
                amount = len(roles)
                roles_string = str(roles)
                if "Server Booster" in roles_string:
                    amount -= 1

                if True:
                    print("user has no roles")
                    await user.send("¡Autenticación exitosa! En unos segundos recibirás el rol.")
                    print("getting medal count")
                    url = f"https://osu.ppy.sh/users/{osu_id}"
                    headers = {
                        "User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
                    }
                    cookies = requests.head(url)
                    r = requests.get(url, headers=headers,
                                     allow_redirects=True, cookies=cookies)
                    content = str(r.content)
                    medals = content.count("achievement_id")
                    print("getting roles")
                    r95cid = 771229635622207488
                    r95c = get(guild.roles, id=r95cid)

                    print("applying roles")
                    if medals > 1:
                        print("osuplayer")
                        await member.add_roles(r95c)

                    print("setting username")
                    osu_username = re.search('<title>(.*?) ', content).group(1)
                    osu_username = osu_username.replace("&nbsp;", " ")
                    osu_username = osu_username.replace("\u2665", " ")
                    print("setting up user info with this info:")
                    print(f"osuid: {osu_id}")
                    print(f"discordid: {discord_id}")
                    print(f"osuname: {osu_username}")
                    await member.edit(nick=osu_username)
                    string_bytes = user.name.encode("utf-8")
                    base64_bytes = base64.b64encode(string_bytes)
                    base64_string = base64_bytes.decode("ascii")
                    discord_name = base64_string
                    insert_user(discord_name, osu_username, user.discriminator, medals, osu_id, discord_id)

                    embed = discord.Embed(title="¡Solicitud aceptada!",
                                          description="osu! link: https://osu.ppy.sh/users/" + str(
                                              osu_id) + "\ndiscord tag: <@" + str(discord_id) + ">",
                                          color=0x00aa00)  # make green embed
                    await channel.send(embed=embed)

                    print("quitting\n\n")

            else:
                print("user is not in server")
                await user.send(
                    'ERROR : Al parecer, no estás en nuestro servidor de Discord (https://discord.gg/osuchile)')

        else:
            print("discord id taken")
            await user.send(
                'ERROR : ¡Esta cuenta de Discord está asociada a otro usuario!\n'
                '¡La cuenta de osu! está asociada a otra persona!\n'
                'Si crees que se trata de un error, no dudes en contactar a algún administrador.')

    else:
        print("osu! id taken")
        await user.send(
            'ERROR : ¡La cuenta de osu! está asociada a otra persona!\n'
            'Si crees que se trata de un error, no dudes en contactar a algún administrador.')


@bot.event
async def on_ready():
    print('bot logged in :3')


@app.route('/')
def test():
    osu_id = str(request.args.get('osuid'))
    discord_id = str(request.args.get('disid'))

    if osu_id is None or osu_id == "":
        return Response(response='bad osuid', status=400, mimetype="text/plain")

    if discord_id is None or discord_id == "":
        return Response(response='bad disid', status=400, mimetype="text/plain")

    print(f"[x] get data from request (osu_id / discord_id): {osu_id} / {discord_id}")

    bot.loop.create_task(register(osu_id, discord_id))
    result = f"osuid: {osu_id}, disid: {discord_id}"

    return Response(response=result, status=200, mimetype="text/plain")


@bot.command()
@commands.has_role(771245699648061440)
async def msg(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def verify(ctx):
    discord_id = ctx.message.author.id
    mydb = db_connect()
    sql_select_query = f"SELECT * FROM users WHERE discordid = \"{discord_id}\""
    cursor = mydb.cursor()
    cursor.execute(sql_select_query)
    rowcount = cursor.rowcount

    if rowcount == 0:
        await ctx.message.author.send(
            f"Para verificar tu identidad de osu!, haz click en el siguiente link: "
            f"https://osuchile.com/auth/?discord={discord_id}")
    else:
        await ctx.message.author.send("Tu cuenta de osu! ya esta verificada, "
                                      "si deseas cambiar el nombre, escribe bot!update")


@bot.command()
async def info(ctx, discord_id):
    if not discord_id.isnumeric():
        ctx.send("y ese discord id? D:")
        return

    mydb = db_connect()
    sql_select_query = f"SELECT * FROM users WHERE discordid = \"{discord_id}\""
    cursor = mydb.cursor()
    cursor.execute(sql_select_query)
    records = cursor.fetchone()

    if records is None:
        await ctx.send("Usuario no se encuentra en la base de datos")
        return

    embed = discord.Embed(title="Información usuario verificado",
                          description=f"osu! link: https://osu.ppy.sh/users/{records[5]}"
                                      f"\ndiscord tag: <@{records[6]}>",
                          color=0xaaaa00)
    await ctx.send(embed=embed)


@bot.command()
async def update(ctx):
    discord_id = ctx.message.author.id
    print(discord_id)
    mydb = db_connect()
    sql_select_query = f"SELECT * FROM users WHERE discordid = \"{discord_id}\""
    print(sql_select_query)
    cursor = mydb.cursor()
    cursor.execute(sql_select_query)
    records = cursor.fetchone()
    # await ctx.send(str(records) + " - " + str(type(records))+ " - " + str(cursor.rowcount))
    # await ctx.send(str(records))
    if records is None:
        await ctx.message.author.send('No estas verificado en el servidor. Utiliza bot!verify')
    else:
        osuid = records[5]
        url = 'https://osu.ppy.sh/users/' + str(osuid)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
        }
        cookies = requests.head(url)
        r = requests.get(url, headers=headers,
                         allow_redirects=True, cookies=cookies)
        content = str(r.content)
        print("setting username")
        uname = re.search('<title>(.*?) ', content).group(1)
        uname = uname.replace("&nbsp;", " ")
        uname = uname.replace("\u2665", " ")
        print("setting up user info with this info:")
        print("osuname: " + uname)
        await ctx.message.author.edit(nick=uname)
        string_bytes = ctx.message.author.name.encode("utf-8")
        base64_bytes = base64.b64encode(string_bytes)
        base64_string = base64_bytes.decode("ascii")
        dname = base64_string
        print("discordname: " + dname + "#" + ctx.message.author.discriminator)
        mycursor = mydb.cursor()
        sql = f"UPDATE users SET discordname='{dname}', discordtag='{ctx.message.author.discriminator}', " \
              f"osuname='{uname}' WHERE discordid = '{discord_id}';"
        print(sql)
        mycursor.execute(sql)
        mydb.commit()
        print(mycursor.rowcount, "record(s) affected")
        await ctx.message.author.send(f"Tu nombre ha sido actualizado a {uname}")


'''@bot.command()
async def testdb(ctx):
    mydb = dbconnect()
    sql_select_Query = "SELECT * FROM users WHERE discordid = '209051034318929920'"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchone()
    await ctx.send(str(records))'''


def hehe():
    app.run(host='127.0.0.1', port=5050)


if __name__ == '__main__':
    t1 = threading.Thread(target=hehe)
    t1.start()
    bot.run(' ')
