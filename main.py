import base64
import os
import threading

import discord
from discord.ext import commands
from discord.utils import get
from flask import Flask, Response, request
from dotenv import load_dotenv

import Database
from RestClient import RestClient

app = Flask(__name__)

load_dotenv()
bot = commands.Bot(command_prefix="bot!", intents=discord.Intents.all())
osu_client = RestClient(int(os.environ["OSU_CLIENT_ID"]), os.environ["OSU_CLIENT_SECRET"],
                        "https://osu.ppy.sh/oauth/token", "https://osu.ppy.sh/api/v2/")


async def register(osu_id, discord_id):
    discord_id_query_data = Database.select_by_discordid(discord_id)
    osu_id_query_data = Database.select_by_osuid(osu_id)

    guild = bot.get_guild(771221822745477130)
    channel = bot.get_channel(771815223932747786)
    embed = discord.Embed(title="Nueva solicitud",
                          description=f"osu! link: https://osu.ppy.sh/users/{osu_id}\n"
                                      f"Discord tag: <@{discord_id}>",
                          color=0xF2E15E)

    await channel.send(embed=embed)
    user = bot.get_user(int(discord_id))
    member = guild.get_member(int(discord_id))

    if osu_id_query_data is not None:
        print(f"osu! ID ({osu_id}) is taken")
        await user.send(
            'ERROR : ¡La cuenta de osu! está asociada a otra persona!\n'
            'Si crees que se trata de un error, no dudes en contactar a algún administrador.')
        return

    print(f"osu! ID ({osu_id}) not signed up")

    if discord_id_query_data is not None:
        print(f"Discord ID ({discord_id}) is taken")
        await user.send(
            'ERROR : ¡Esta cuenta de Discord está asociada a otro usuario!\n'
            '¡La cuenta de osu! está asociada a otra persona!\n'
            'Si crees que se trata de un error, no dudes en contactar a algún administrador.')
        return

    print(f"Discord ID ({discord_id}) not signed up")
    guild = bot.get_guild(771221822745477130)

    if member is None:
        print("user is not in server")
        await user.send(
            'ERROR : Al parecer, no estás en nuestro servidor de Discord (https://discord.gg/osuchile)')
        return

    print(f"osu! ID: {osu_id}\n"
          f"Discord ID: {discord_id}\n"
          f"User is in the server.")

    await user.send("¡Autenticación exitosa! En unos segundos recibirás el rol.")
    print("Getting medal count")
    osu_user = osu_client.get_user(osu_id)
    medal_count = len(osu_user["user_achievements"])

    verified_role = get(guild.roles, id=771229635622207488)

    if medal_count > 1:
        print(f"Giving user with ID ({discord_id}) the verified role.")
        await member.add_roles(verified_role)

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
                          color=0x87F25E)  # make green embed
    await channel.send(embed=embed)


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
    query_data = Database.select_by_discordid(discord_id)

    if query_data is None:
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

    query_data = Database.select_by_discordid(discord_id)

    if query_data is None:
        await ctx.reply("Usuario no se encuentra en la base de datos", mention_author=False)
        return

    embed = discord.Embed(title="Información usuario verificado",
                          description=f"**osu! link:** https://osu.ppy.sh/users/{query_data[5]}\n"
                                      f"**Discord tag:** <@{query_data[6]}>\n"
                                      f"**Database ID:** {query_data[0]}",
                          color=0x5E97F2)
    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
@commands.has_role(771245699648061440)
async def remove(ctx, discord_id):
    if not discord_id.isnumeric():
        await ctx.send("y ese discord id? D:")
        return

    query_data = Database.select_by_discordid(discord_id)

    if query_data is None:
        await ctx.reply("Usuario no encontrado en la base de datos", mention_author=False)
        return

    embed = discord.Embed(title="Informacion usuario eliminado",
                          description=f"**osu! link:** https://osu.ppy.sh/users/{query_data[5]}\n"
                                      f"**Discord tag:** <@{query_data[6]}>\n"
                                      f"**Database ID:** {query_data[0]}",
                          color=0xF25E5E)

    rows_affected = Database.delete_by_discordid(discord_id)

    if rows_affected >= 1:
        await ctx.reply(embed=embed, mention_author=False)
        return

    await ctx.reply("No se pudo eliminar el usuario de la base de datos.", mention_author=False)


@bot.command()
async def update(ctx):
    discord_id = ctx.message.author.id
    print(discord_id)
    query_data = Database.select_by_discordid(discord_id)

    if query_data is None:
        await ctx.message.author.send("No estas verificado en el servidor. Utiliza bot!verify para verificarte")
        return

    osu_id = query_data[5]
    osu_user_data = osu_client.get_user(osu_id)
    osu_username = osu_user_data["username"]
    print("Setting up user info with this info:")
    print(f"osu! username: {osu_username}")
    await ctx.message.author.edit(nick=osu_username)
    string_bytes = ctx.message.author.name.encode("utf-8")
    discord_username = base64.b64encode(string_bytes).decode("ascii")
    print(f"Discord tag: {discord_username}#{ctx.message.author.discriminator}")
    rows = Database.update_user(discord_id, discord_username, ctx.message.author.discriminator, osu_username)
    print(f"{rows} row(s) affected")
    await ctx.message.author.send(f"Tu nombre ha sido actualizado a {osu_username}")


@bot.event
async def on_member_join(member):
    registered_user = Database.select_by_discordid(member.id)

    if registered_user is None:
        return

    member.edit(nick=registered_user["osu_username"])


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
    bot.run(os.environ["DISCORD_TOKEN"])
