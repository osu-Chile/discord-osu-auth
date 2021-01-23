import argparse
import threading
import discord
import mysql.connector
import requests
import re
from discord.utils import get
from discord.ext import commands
import base64

from flask import Flask,Response,jsonify,abort,request
from os import system
import base64, uuid

app = Flask(__name__)

# datos de la db ._.XD

def dbconnect():
    return mysql.connector.connect(
        host="localhost",
        database="osudb",
        user="",
        password="",
        auth_plugin='mysql_native_password'
    )

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="osu!cl-", intents=intents)

async def reg(o, d):
    mydb = dbconnect()
    sql_select_Query = "SELECT * FROM users WHERE discordid = '" + str(d) + "'"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()
    dires = cursor.rowcount

    sql_select_Query = "SELECT * FROM users WHERE osuid = '" + str(o) + "'"
    cursor = mydb.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()
    osres = cursor.rowcount

    guild = bot.get_guild(771221822745477130)
    channel = bot.get_channel(771815223932747786)
    embed = discord.Embed(title="Nueva solicitud", description="osu! link: https://osu.ppy.sh/users/" + str(o) + "\ndiscord tag: <@" + str(d) + ">", color=0xaaaa00)
    await channel.send(embed=embed)
    user = bot.get_user(int(d))
    member = guild.get_member(int(d))
    
    if(osres == 0):
        print("osu! id not signed up")
        
        if(dires == 0):
            print("discord id not signed up")
            guild = bot.get_guild(771221822745477130)
            
            if guild.get_member(int(d)) is not None:
                print("osu! id: " + o)
                print("discord id: " + d)
                print("user is in server")
                roles = guild.get_member(int(d)).roles
                amount = len(roles)
                rolesstr = str(roles)
                if "Server Booster" in rolesstr:
                    amount -= 1

                # tabien
                
                if amount == 1:
                    print("user has no roles")
                    await user.send('¡Autenticación exitosa! En unos segundos recibirás el rol.')
                    print("getting medal count")
                    url = 'https://osu.ppy.sh/users/' + str(o)
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
                    }
                    cookies = requests.head(url)
                    r = requests.get(url, headers=headers, allow_redirects=True, cookies=cookies)
                    content = str(r.content)
                    medals = content.count("achievement_id")
                    print("getting roles")
                    r95cid = 771229635622207488
                    r95c = get(guild.roles, id=r95cid)
   
                    print("applying roles")
                    if(medals > 1):
                        print("osuplayer")
                        await member.add_roles(r95c)
    
                    
                    print("setting username")
                    uname = re.search('<title>(.*?) ', content).group(1)
                    uname = uname.replace("&nbsp;", " ") 
                    uname = uname.replace("\u2665", " ")
                    print("setting up user info with this info:")
                    print("osuid: " + str(o))
                    print("discordid: " + str(o))
                    print("osuname: " + uname)
                    await member.edit(nick=uname)
                    string_bytes = user.name.encode("utf-8")
                    base64_bytes = base64.b64encode(string_bytes) 
                    base64_string = base64_bytes.decode("ascii") 
                    dname = base64_string
                    print("discordname: " + dname + "#" + user.discriminator)
                    mycursor = mydb.cursor()
                    print("INSERT INTO users (`id`, `discordname`, `osuname`, `discordtag`, `medals`, `osuid`, `discordid`) VALUES (NULL, '" + dname + "', '" + uname + "', " + str(user.discriminator) + ", " + str(medals) + ", " + str(o) + ", " + str(d) + ");")
                    sql = "INSERT INTO users (`id`, `discordname`, `osuname`, `discordtag`, `medals`, `osuid`, `discordid`) VALUES (NULL, '" + dname + "', '" + uname + "', " + str(user.discriminator) + ", " + str(medals) + ", " + str(o) + ", " + str(d) + ");"
                    mycursor.execute(sql)
                    mydb.commit()
                    print(mycursor.rowcount, "record(s) affected") 

                    embed = discord.Embed(title="¡Solicitud aceptada!", description="osu! link: https://osu.ppy.sh/users/" + str(o) + "\ndiscord tag: <@" + str(d) + ">", color=0x00aa00) # make green embed
                    await channel.send(embed=embed)
                    
                    print("quitting\n\n")
                else:
                    print("has roles")
                    await user.send("ERROR : Lamentamos las molestias, pero necesitarás realizar el proceso nuevamente. Contacta a un administrador de nuestro Discord, con una screenshot de este mensaje.")
                    
            else:
                print("user is not in server")
                await user.send('ERROR : Al parecer, no estás en nuestro servidor de Discord (https://discord.gg/osuchile)')
                
        else:
            print("discord id taken")
            await user.send('ERROR : ¡Esta cuenta de Discord está asociada a otro usuario!\n¡La cuenta de osu! está asociada a otra persona!\nSi crees que se trata de un error, no dudes en contactar a algún administrador.')
            
    else:
        print("osu! id taken")
        await user.send('ERROR : ¡La cuenta de osu! está asociada a otra persona!\nSi crees que se trata de un error, no dudes en contactar a algún administrador.')

@bot.event
async def on_ready():
    print('bot logged in :3')
    

@bot.event
async def on_member_join(member):
    await member.send('¡Bienvenido al servidor! Para entrar a nuestro servidor, necesitamos verificar tu identidad. Para eso, clickea en el siguiente link: http://d.osuchile.com/?discord='+str(member.id))

# xD

@app.route('/')
def test():
    osuid = str(request.args.get('osuid'))
    disid = str(request.args.get('disid'))

    if osuid == None or osuid == "":
        return Response(response='bad osuid', status=400, mimetype="text/plain")

    if disid == None or disid == "":
        return Response(response='bad disid', status=400, mimetype="text/plain")

    print("[x] get data from request (osuid / disid): "+osuid+" / "+disid)
    
    bot.loop.create_task(reg(osuid, disid))
    result = "osuid: {}, disid: {}".format(osuid, disid)

    return Response(response=result, status=200, mimetype="text/plain")

# testing ping pong w bot lol

'''@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)'''

def hehe():
    app.run(host='0.0.0.0', port=5050)
    
if __name__ == '__main__':
    t1 = threading.Thread(target=hehe)
    t1.start()
    bot.run('')
    

    