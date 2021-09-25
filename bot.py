import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import json
import asyncio

bot = commands.Bot(command_prefix=".")
bot.remove_command("help")


@bot.event
async def on_ready():
    print("Bot running with:")
    print("Username: ", bot.user.name)
    print("User ID: ", bot.user.id)


@bot.command()
async def help(ctx):
    with open("data.json") as f:
        data = json.load(f)

    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if ctx.author.guild_permissions.administrator or valid_user:

        em = discord.Embed(title="Nokyly Bot Help", description="", color=0x00a8ff)
        em.add_field(name="`.new <message>`",
                     value="Pour créé un nouveau ticket. Ajoute un message après pour qu'il soit envoyer en premier "
                           "ans le salon")
        em.add_field(name="`.close`", value="Clore un ticket. Marche seulement dans un channel ticket.")
        em.add_field(name="`.addaccess <role_id>`",
                     value="**Admin commande**, ajouter un rôle qui a accès à tout les ticket.")
        em.add_field(name="`.delaccess <role_id>`",
                     value="**Admin commande**, retirer un rôle qui a accès à tout les ticket.")
        em.add_field(name="`.addpingedrole <role_id>`",
                     value="**Admin commande**, ajouter un rôle qui sera ping à la création d'un ticket.")
        em.add_field(name="`.delpingedrole <role_id>`",
                     value="**Admin commande**, retirer un rôle qui sera ping à la création d'un ticket.")
        em.add_field(name="`.addadminrole <role_id>`",
                     value="**Admin commande**, ajouter un rôle qui pourra config le bot.")
        em.add_field(name="`.deladminrole <role_id>`",
                     value="**Admin commande**, retirer un rôle qui pourra config le bot.")
        em.set_author(name="Brawl Nokyly, Hosted by hosted-project.org", icon_url="https://cdn.discordapp.com/icons"
                                                                                  "/878202593422241802"
                                                                                  "/9b727565a48db05fa6fc108cdbb6fad4"
                                                                                  ".webp?size=96", url="hosted"
                                                                                                       "-project.org")

        await ctx.send(embed=em)

    else:

        em = discord.Embed(title="Nokyly Bot Help", description="", color=0x00a8ff)
        em.add_field(name="`.new <message>`",
                     value="Pour créé un nouveau ticket. Ajoute un message après pour qu'il soit envoyer en premier "
                           "ans le salon")
        em.add_field(name="`.close`", value="Clore un ticket. Marche seulement dans un channel ticket.")
        em.set_footer(text="Brawl Nokyly, Hosted by hosted-project.org")

        await ctx.send(embed=em)


@bot.command()
async def new(ctx, *, args=None):
    await bot.wait_until_ready()

    if args is None:
        message_content = "Ce salon est a vous, discutez !"

    else:
        message_content = "".join(args)

    with open("data.json") as f:
        data = json.load(f)

    ticket_number = int(data["ticket-counter"])
    ticket_number += 1

    ticket_channel = await ctx.guild.create_text_channel("ticket-{}".format(ticket_number))
    await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)

    for role_id in data["valid-roles"]:
        role = ctx.guild.get_role(role_id)

        await ticket_channel.set_permissions(role, send_messages=True, read_messages=True, add_reactions=True,
                                             embed_links=True, attach_files=True, read_message_history=True,
                                             external_emojis=True)

    await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True,
                                         embed_links=True, attach_files=True, read_message_history=True,
                                         external_emojis=True)

    em = discord.Embed(title="Nouveau ticket de {}#{}".format(ctx.author.name, ctx.author.discriminator),
                       description="{}".format(message_content), color=0x00a8ff)

    await ticket_channel.send(embed=em)

    pinged_msg_content = ""
    non_mentionable_roles = []

    if data["pinged-roles"] != []:

        for role_id in data["pinged-roles"]:
            role = ctx.guild.get_role(role_id)

            pinged_msg_content += role.mention
            pinged_msg_content += " "

            if role.mentionable:
                pass
            else:
                await role.edit(mentionable=True)
                non_mentionable_roles.append(role)

        await ticket_channel.send(pinged_msg_content)

        for role in non_mentionable_roles:
            await role.edit(mentionable=False)

    data["ticket-channel-ids"].append(ticket_channel.id)

    data["ticket-counter"] = int(ticket_number)
    with open("data.json", 'w') as f:
        json.dump(data, f)

    created_em = discord.Embed(title="Nokyly Tickets",
                               description="Votre ticket a été créé sur {}".format(ticket_channel.mention),
                               color=0x00a8ff)

    await ctx.send(embed=created_em)


@bot.command()
async def close(ctx):
    with open('data.json') as f:
        data = json.load(f)

    if ctx.channel.id in data["ticket-channel-ids"]:

        channel_id = ctx.channel.id

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "oui"

        try:

            em = discord.Embed(title="Nokyly Tickets",
                               description="Etes vous sur de clore ce ticket ? Répondez avec `oui` si vous êtes sur.",
                               color=0x00a8ff)

            await ctx.send(embed=em)
            await bot.wait_for('message', check=check, timeout=60)
            await ctx.channel.delete()

            index = data["ticket-channel-ids"].index(channel_id)
            del data["ticket-channel-ids"][index]

            with open('data.json', 'w') as f:
                json.dump(data, f)

        except asyncio.TimeoutError:
            em = discord.Embed(title="Nokyly Tickets",
                               description="Trop de temps attendu, refaites la commande pour clore le ticket.",
                               color=0x00a8ff)
            await ctx.send(embed=em)


@bot.command()
async def addaccess(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)

    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if valid_user or ctx.author.guild_permissions.administrator:
        role_id = int(role_id)

        if role_id not in data["valid-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["valid-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Nokyly Tickets",
                                   description="Rôle `{}` bien ajouté a la liste des `Ticket Viewers Roles`.".format(
                                       role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="Nokyly Tickets",
                                   description="Veuillez mettre un ID de rôle valide.")
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="Nokyly Tickets", description="Ce rôle est déjà dans la liste des `Ticket "
                                                                    "Viewers Roles`.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    else:
        em = discord.Embed(title="Nokyly Tickets", description="Vous devez êtres administrateur.",
                           color=0x00a8ff)
        await ctx.send(embed=em)


@bot.command()
async def delaccess(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)

    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            valid_roles = data["valid-roles"]

            if role_id in valid_roles:
                index = valid_roles.index(role_id)

                del valid_roles[index]

                data["valid-roles"] = valid_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Nokyly Tickets",
                                   description="Rôle `{}` bien supprimé de la liste des `Ticket Viewers Roles`.".format(
                                       role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            else:

                em = discord.Embed(title="Nokyly Tickets",
                                   description="Le rôle `{}` n'est pas dans la liste des `Ticket Viewers Roles`.", color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="Nokyly Tickets",
                               description="Veuillez mettre un ID de rôle valide")
            await ctx.send(embed=em)

    else:
        em = discord.Embed(title="Nokyly Tickets", description="Vous devez êtres administrateur.",
                           color=0x00a8ff)
        await ctx.send(embed=em)


@bot.command()
async def addpingedrole(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)

    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if valid_user or ctx.author.guild_permissions.administrator:

        role_id = int(role_id)

        if role_id not in data["pinged-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["pinged-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Nokyly Tickets",
                                   description="Rôle `{}` bien ajouté a la liste des `Ticket Pinged Roles`.".format(
                                       role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="Nokyly Tickets",
                                   description="Veuillez mettre un ID de rôle valide")
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="Nokyly Tickets",
                               description="Le rôle `{}` est déjà dans la liste des `Ticket Pinged Roles`.", color=0x00a8ff)
            await ctx.send(embed=em)

    else:
        em = discord.Embed(title="Nokyly Tickets", description="Vous devez êtres administrateur.",
                           color=0x00a8ff)
        await ctx.send(embed=em)


@bot.command()
async def delpingedrole(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)

    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            pinged_roles = data["pinged-roles"]

            if role_id in pinged_roles:
                index = pinged_roles.index(role_id)

                del pinged_roles[index]

                data["pinged-roles"] = pinged_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Nokyly Tickets",
                                   description="Rôle `{}` bien supprimé de la liste des `Ticket Pinged Roles`.".format(
                                       role.name), color=0x00a8ff)
                await ctx.send(embed=em)

            else:
                em = discord.Embed(title="Nokyly Tickets",
                                   description="Le rôle `{}` n'est pas dans la liste des `Ticket Pinged Roles`.",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="Nokyly Tickets",
                               description="Veuillez mettre un ID de rôle valide.")
            await ctx.send(embed=em)

    else:
        em = discord.Embed(title="Nokyly Tickets", description="Vous devez être administrateur.",
                           color=0x00a8ff)
        await ctx.send(embed=em)


@bot.command()
@has_permissions(administrator=True)
async def addadminrole(ctx, role_id=None):
    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        data["verified-roles"].append(role_id)

        with open('data.json', 'w') as f:
            json.dump(data, f)

        em = discord.Embed(title="Nokyly Tickets",
                           description="Rôle `{}` bien ajouté a la liste des `Ticket Admin Roles`.".format(
                               role.name), color=0x00a8ff)
        await ctx.send(embed=em)

    except:
        em = discord.Embed(title="Nokyly Tickets",
                           description="Veuillez mettre un ID de rôle valide.")
        await ctx.send(embed=em)


@bot.command()
@has_permissions(administrator=True)
async def deladminrole(ctx, role_id=None):
    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        admin_roles = data["verified-roles"]

        if role_id in admin_roles:
            index = admin_roles.index(role_id)

            del admin_roles[index]

            data["verified-roles"] = admin_roles

            with open('data.json', 'w') as f:
                json.dump(data, f)

            em = discord.Embed(title="Nokyly Tickets",
                               description="Rôle `{}` bien supprimé de la liste des `Ticket Admin Roles`.".format(
                                   role.name), color=0x00a8ff)

            await ctx.send(embed=em)

        else:
            em = discord.Embed(title="Nokyly Tickets",
                               description="Le rôle `{}` n'est pas dans la liste des `Ticket Admin Roles`.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    except:
        em = discord.Embed(title="Nokyly Tickets",
                           description="Veuillez mettre un  ID de rôle valide.")
        await ctx.send(embed=em)


