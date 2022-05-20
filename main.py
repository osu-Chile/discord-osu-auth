import base64
import threading

import discord
from discord.ext import commands
from discord.utils import get
from flask import Flask, Response, request

import Database
from RestClient import RestClient

app = Flask(__name__)

bot = commands.Bot(command_prefix="bot!", intents=discord.Intents.all())
osu_client = RestClient(0, "", "", "")


async def register(osu_id, discord_id):
    discord_id_query = Database.select_by_discord_id(discord_id)
    osu_id_query = Database.select_by_osu_id(osu_id)

    guild = bot.get_guild(771221822745477130)
    channel = bot.get_channel(771815223932747786)
    embed = discord.Embed(title="Nueva solicitud",
                          description=f"osu! link: https://osu.ppy.sh/users/{osu_id}\n"
                                      f"Discord tag: <@{discord_id}>",
                          color=0xaaaa00)  # make green embed

    await channel.send(embed=embed)
    user = bot.get_user(int(discord_id))
    member = guild.get_member(int(discord_id))

    if osu_id_query is not None:
        print("osu! id taken")
        await user.send(
            'ERROR : ¡La cuenta de osu! está asociada a otra persona!\n'
            'Si crees que se trata de un error, no dudes en contactar a algún administrador.')
        return

    print("osu! id not signed up")

    if discord_id_query is not None:
        print("discord id taken")
        await user.send(
            'ERROR : ¡Esta cuenta de Discord está asociada a otro usuario!\n'
            '¡La cuenta de osu! está asociada a otra persona!\n'
            'Si crees que se trata de un error, no dudes en contactar a algún administrador.')
        return

    print("Discord ID not signed up")
    guild = bot.get_guild(771221822745477130)

    if member is None:
        print("user is not in server")
        await user.send(
            'ERROR : Al parecer, no estás en nuestro servidor de Discord (https://discord.gg/osuchile)')
        return

    print(f"osu! id: {osu_id}\n"
          f"Discord ID: {discord_id}\n"
          f"User is in the server.")

    await user.send("¡Autenticación exitosa! En unos segundos recibirás el rol.")
    print("getting medal count")
    osu_user = osu_client.get_user(osu_id)
    medal_count = len(osu_user["user_achievements"])

    verified_role = get(guild.roles, id=771229635622207488)

    print("applying roles")
    if medal_count > 1:
        print(f"osuplayer")
        await member.add_roles(verified_role)

    print("setting username")
    osu_username = osu_user["username"]
    print("Setting up user info with this info:\n"
          f"osu! ID: {osu_id}\n"
          f"Discord ID: {discord_id}\n"
          f"osu! username: {osu_username}")
    await member.edit(nick=osu_username)
    string_bytes = user.name.encode("utf-8")
    discord_username = base64.b64encode(string_bytes).decode("ascii")
    rows = Database.insert_user(discord_username, osu_username, user.discriminator, medal_count, osu_id,
                                discord_id)
    print(f"{rows} row(s) affected.")

    embed = discord.Embed(title="¡Solicitud aceptada!",
                          description=f"osu! link: https://osu.ppy.sh/users/{osu_id}\n"
                                      f"Discord tag: <@{discord_id}>",
                          color=0x00aa00)  # make green embed
    await channel.send(embed=embed)

    print("quitting\n\n")


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
    query = Database.select_by_discord_id(discord_id)

    if query is None:
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

    query = Database.select_by_discord_id(discord_id)

    if query is None:
        await ctx.send("Usuario no se encuentra en la base de datos")
        return

    embed = discord.Embed(title="Información usuario verificado",
                          description=f"**osu! link:** https://osu.ppy.sh/users/{query[5]}\n"
                                      f"**Discord tag:** <@{query[6]}>\n"
                                      f"**Database ID:** {query[0]}",
                          color=0xaaaa00)
    await ctx.send(embed=embed)


@bot.command()
async def update(ctx):
    discord_id = ctx.message.author.id
    print(discord_id)
    query = Database.select_by_discord_id(discord_id)

    if query is None:
        await ctx.message.author.send("No estas verificado en el servidor. Utiliza bot!verify para verificarte")
        return

    osu_id = query[5]
    osu_user = osu_client.get_user(osu_id)
    print("setting username")
    osu_username = osu_user["username"]
    print("setting up user info with this info:")
    print(f"osu! username: {osu_username}")
    await ctx.message.author.edit(nick=osu_username)
    string_bytes = ctx.message.author.name.encode("utf-8")
    discord_username = base64.b64encode(string_bytes).decode("ascii")
    print(f"Discord tag: {discord_username}#{ctx.message.author.discriminator}")
    rows = Database.update_user(discord_id, discord_username, ctx.message.author.discriminator, osu_username)
    print(f"{rows} row(s) affected")
    await ctx.message.author.send(f"Tu nombre ha sido actualizado a {osu_username}")


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
    bot.run()
