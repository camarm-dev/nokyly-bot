import json
import operator
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix=".", intents=intents)
bot.remove_command("help")
infos = json.loads(open('level.json').read())
MESSAGE_XP = infos['messagexp']
LEVEL_UP = infos['levelup']
LEVEL = infos['level']


async def getlv(user):
    levels = json.loads(open('level.json').read())
    if str(user) in list(levels['users'].keys()):
        return levels['users'][f'{user}']
    levels['users'][f'{user}'] = {'lv': 0, 'xp': 0, 'up': LEVEL}
    open('level.json', 'w+').write(json.dumps(levels))
    return levels['users'][f'{user}']


async def writelv(userid, infos):
    levels = json.loads(open('level.json').read())
    levels['users'][f'{userid}'] = infos
    open('level.json', 'w+').write(json.dumps(levels))


async def getrank(userid):
    levels = json.loads(open('level.json').read())
    ranks = {}
    for u in levels['users']:
        ranks[u] = levels['users'][u]['lv']
    listed = sorted(ranks, key=operator.itemgetter(1), reverse=True)
    index = listed.index(str(userid))
    return index + 1


async def getranks():
    levels = json.loads(open('level.json').read())
    ranks = {}
    for u in levels['users']:
        ranks[u] = levels['users'][u]['lv']
    listed = sorted(ranks, key=operator.itemgetter(1), reverse=True)[:9]
    ranks = []
    for i in listed:
        doc = levels['users'][i]
        doc['rank'] = listed.index(i) + 1
        doc['id'] = i
        ranks.append(doc)
    return ranks


@bot.event
async def on_ready():
    print("Bot running with:")
    print("Username: ", bot.user.name)
    print("User ID: ", bot.user.id)


@bot.event
async def on_member_remove(member):
    channel = await bot.fetch_channel(797147802014580766)
    em = discord.Embed(title=f"{member.name}#{member.discriminator} nous a quitté :(", description="", color=0x00a8ff)
    em.add_field(name=f"Mention:", value=f"{member.mention}", inline=True)
    em.add_field(name=f"Compte créé:", value=f"depuis le {member.created_at}", inline=True)
    em.add_field(name=f"Rejoin a:", value=f"{member.joined_at}", inline=True)
    em.set_footer(text='Nokyly Bot Hosted by hosted-project.org', icon_url='https://cdn.discordapp.com/icons'
                                                                           '/878202593422241802'
                                                                           '/9b727565a48db05fa6fc108cdbb6fad4'
                                                                           '.webp?size=96')
    em.set_thumbnail(url=member.avatar.url)
    await channel.send(embed=em)
    # link = await channel.create_invite(reason='Quit Person', max_uses=0, max_age=0)
    # await member.send(f"Nous sommes triste que tu parte de **{member.guild.name}** :(\nTu peux toujours changer d'avis: {link.url}")


@bot.event
async def on_member_join(member: discord.Member):
    channel = await bot.fetch_channel(797147636457013288)
    em = discord.Embed(title=f"{member.name}#{member.discriminator} a rejoin !", description="", color=0x00a8ff)
    em.add_field(name=f"Mention:", value=f"{member.mention}", inline=True)
    em.add_field(name=f"Compte créé:", value=f"depuis le {member.created_at}", inline=True)
    em.add_field(name=f"Rejoin a:", value=f"{member.joined_at}", inline=True)
    em.set_footer(text='Nokyly Bot Hosted by hosted-project.org', icon_url='https://cdn.discordapp.com/icons'
                                                                              '/878202593422241802'
                                                                              '/9b727565a48db05fa6fc108cdbb6fad4'
                                                                              '.webp?size=96')
    em.set_thumbnail(url=member.avatar.url)
    await channel.send(embed=em)
    await member.send(f"Bienvenue sur **{member.guild.name}** !\nAccepte les règles dans "
                      f"https://discord.com/channels/797147469111623692/797787118130692106 pour avoir accès au reste "
                      f"du "
                      f"serveur")


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id or message.author.bot:
        return
    author = message.author.id
    xp = await getlv(author)
    xp['xp'] = xp['xp'] + MESSAGE_XP
    if xp['xp'] >= xp['up']:
        xp['lv'] += 1
        xp['xp'] = 0
        xp['up'] = int(xp['up'] * LEVEL_UP)
        em = discord.Embed(title="Nokyly Levels", description="", color=0x00a8ff)
        em.add_field(name=f"{message.author.name}, tu est maintenant level {xp['lv']} !",
                     value=f"{message.author.mention}, prochain niveau: 0/{xp['up']}xp")
        await message.channel.send(embed=em)
    await writelv(author, xp)
    if message.content == '.rank':
        rank = await getrank(author)
        em = discord.Embed(title=f"{message.author.name}#{message.author.discriminator} Levels", description="", color=0x00a8ff)
        em.add_field(name=f"Level:", value=f"{xp['lv']}", inline=True)
        em.add_field(name=f"XP:", value=f"{xp['xp']}/{xp['up']}xp", inline=True)
        em.add_field(name=f"Rank:", value=f"#{rank}", inline=True)
        em.set_footer(text='Nokyly Levels Hosted by hosted-project.org', icon_url='https://cdn.discordapp.com/icons'
                                                                                  '/878202593422241802'
                                                                                  '/9b727565a48db05fa6fc108cdbb6fad4'
                                                                                  '.webp?size=96')
        em.set_thumbnail(url=message.author.avatar)
        await message.channel.send(embed=em)

    elif message.content == '.classement':
        em = discord.Embed(title=f"Server Levels", description="", color=0x00a8ff)
        rank = await getranks()
        for u in rank:
            user = await bot.fetch_user(int(u['id']))
            em.add_field(name=f"{user.name}#{user.discriminator} `#{u['rank']}`", value=f"Level: {u['lv']}\nXP: {u['xp']}/{u['up']}xp", inline=False)
        em.set_footer(text='Nokyly Levels Hosted by hosted-project.org', icon_url='https://cdn.discordapp.com/icons'
                                                                                  '/878202593422241802'
                                                                                  '/9b727565a48db05fa6fc108cdbb6fad4'
                                                                                  '.webp?size=96')
        em.set_thumbnail(url=str(message.guild.icon))
        await message.channel.send(embed=em)


