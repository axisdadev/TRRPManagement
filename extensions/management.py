import datetime
import json

import hikari, lightbulb, time, pathlib, aiosqlite, sqlite3

conn = sqlite3.connect(database="database.db")
cursor = conn.cursor()

plugin = lightbulb.Plugin("management")
bot = None

## STAFF DB EVENTS

@plugin.command()
@lightbulb.option(name="user", description="User to add", type=hikari.Member)
@lightbulb.command("add_staff", description="Add to staff DB")
@lightbulb.implements(lightbulb.SlashCommand)
async def ad_to_db(ctx: lightbulb.Context):
    cursor.execute("SELECT management_role FROM server_data")
    response = cursor.fetchone()[0]

    bot = ctx.app
    roles = ctx.member.get_roles()

    ## db check
    cursor.execute(f"SELECT * FROM staff_data WHERE user_id={ctx.options.user.id}")
    response_2 = cursor.fetchone()

    if response_2 is not None:
        await ctx.respond("User is in DB, cant add to DB.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if response in ctx.member.role_ids:
      cursor.execute(f"INSERT INTO staff_data VALUES ('{ctx.options.user.id}', 0, 0, NULL)")
      conn.commit()
      await ctx.respond(f"Sucesfully added {ctx.options.user.mention} to staff_DB", flags=hikari.MessageFlag.EPHEMERAL)
    else:
      await ctx.respond("You do not have permission to run this.", flags=hikari.MessageFlag.EPHEMERAL)
      return

@plugin.command()
@lightbulb.option(name="user", description="User to remove", type=hikari.Member)
@lightbulb.command("remove_staff", description="Remove from DB")
@lightbulb.implements(lightbulb.SlashCommand)
async def remove_from_db(ctx: lightbulb.Context):
    cursor.execute("SELECT management_role FROM server_data")
    response = cursor.fetchone()[0]

    bot = ctx.app
    roles = ctx.member.get_roles()

    ## in db check
    cursor.execute(f"SELECT * FROM staff_data WHERE user_id={ctx.options.user.id}")
    response_2 = cursor.fetchone()

    if response_2 is None:
        await ctx.respond("User isnt in DB, cant remove from DB.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if response in ctx.member.role_ids:
      cursor.execute(f"DELETE FROM staff_data WHERE user_id={ctx.member.id}")
      conn.commit()
      await ctx.respond(f"Sucesfully removed {ctx.options.user.mention} from staff_DB", flags=hikari.MessageFlag.EPHEMERAL)
    else:
      await ctx.respond("You do not have permission to run this.", flags=hikari.MessageFlag.EPHEMERAL)
      return

## STAFF INFO!

@plugin.command()
@lightbulb.option(name="user", description="Staff member to look up.", type=hikari.Member)
@lightbulb.command("lookup", description="Get info about a certain staff member.")
@lightbulb.implements(lightbulb.SlashCommand)
async def lookup(ctx: lightbulb.context):
    cursor.execute(f"SELECT * FROM staff_data WHERE user_id={ctx.options.user.id}")
    result = cursor.fetchone()
    if result is None:
        await ctx.respond(f"{ctx.options.user.mention} Is not a staff member, therefore there is no information about them. ❌",
                          flags=hikari.MessageFlag.EPHEMERAL)
        return

    user_id = result[0]
    warnings = result[1]
    strikes = result[2]
    links = json.dumps(result[3])

    print(user_id)

    staff_info_embed = hikari.Embed(
        title="Staff Info 📈🧑",
        description=f"All of current staff info for {ctx.options.user.mention}! \n----------------------",
        colour="#89CFF0"
    )

    staff_user = ctx.options.user

    joined_at = str(staff_user.joined_at)
    joined_at_format = joined_at.split(" ")

    staff_info_embed.add_field(name="Warnings 📉", value=str(warnings), inline=True)
    staff_info_embed.add_field(name="Strikes ❌", value=str(strikes), inline=True)
    staff_info_embed.add_field(name="🧑 ↓ Other Details ↓ 🧑", value="-----------------------")
    staff_info_embed.add_field(name="Joined Server 🌍", value=joined_at_format[0])
    staff_info_embed.add_field(name="User ID 🏷️", value=staff_user.id)
    staff_info_embed.set_thumbnail(staff_user.avatar_url)
    staff_info_embed.add_field(name="Warning Links 🔗",value=str(links))

    await ctx.respond(embed=staff_info_embed,content=f"Staff info for {ctx.options.user.mention} 🏷️")




## WARNINGS SYS BELOW!
@plugin.command()
@lightbulb.option(name="id", description="ID of request to deny")
@lightbulb.option(name="reason", description="Reason for the denial.")
@lightbulb.command("deny_warn", description="Denies. a warn request")
@lightbulb.implements(lightbulb.SlashCommand)
async def deny_warn(ctx: lightbulb.Context):
    embed = ctx.bot.d[f"{ctx.options.id}_warning_embed"]
    staff_affected = ctx.bot.d[f"{ctx.options.id}_warning_staff"]
    issuer = ctx.bot.d[f"{ctx.options.id}_warning_issuer"]
    roles = ctx.member.role_ids

    cursor.execute("SELECT director_role FROM server_data")
    response = cursor.fetchone()[0]

    if not response in roles:
        await ctx.respond("You arent allowed to deny warn requests. ❌", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if embed.title == "Warning 📉":
        embed.colour = "#00FF00"
        embed.set_footer(text=f"Toms River Roleplay, copyright @axisdadev 2023 🌍")
    else:
        await ctx.respond("Invalid request id, was request already accepted or denied? 🤷", flags=hikari.MessageFlag.EPHEMERAL)
        return

    cursor.execute("SELECT approval_channel FROM server_data")
    approval_channel = cursor.fetchone()[0]

    await ctx.bot.rest.edit_message(approval_channel, ctx.options.id, content=f"Denied by {ctx.author.mention}. ❌",
                                    embed=embed)

    await ctx.bot.rest.create_message(channel=response, content=f"{staff_affected.mention}", embed=embed)
    await ctx.respond(f"Denied warn request {ctx.options.id}", flags=hikari.MessageFlag.EPHEMERAL)

    try:
     await issuer.send(f"Your warn request, {ctx.options.id} Was denied by: ``{ctx.member.username}`` :no_entry_sign: \nReasoning: ``{ctx.options.reason}``")
    except:
     print("Couldn't DM the moderator about the denial.")

    ctx.bot.d[f"{ctx.options.id}_warning_embed"] = None
    ctx.bot.d[f"{ctx.options.id}_warning_staff"] = None
    ctx.bot.d[f"{ctx.options.id}_warning_issuer"] = None

@plugin.command()
@lightbulb.option(name="id", description="id of request to accept.")
@lightbulb.option(name="reason", description="reason for the approval.")
@lightbulb.command("accept_warn", description="accepts a warn request")
@lightbulb.implements(lightbulb.SlashCommand)
async def accept_warn(ctx: lightbulb.Context):
    embed = ctx.bot.d[f"{ctx.options.id}_warning_embed"]
    staff_affected = ctx.bot.d[f"{ctx.options.id}_warning_staff"]
    issuer = ctx.bot.d[f"{ctx.options.id}_warning_issuer"]
    roles = ctx.member.role_ids

    cursor.execute("SELECT director_role FROM server_data")
    response = cursor.fetchone()[0]

    if not response in roles:
        await ctx.respond("You arent allowed to accept warn requests. ❌", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if embed.title == "Warning 📉":
        embed.colour = "#00FF00"
        embed.set_footer(text=f"Toms River Roleplay, copyright @axisdadev 2023 🌍")
    else:
        await ctx.respond("Invalid request id, was request already accepted or denied?", flags=hikari.MessageFlag.EPHEMERAL)
        return

    cursor.execute("SELECT approval_channel FROM server_data")
    approval_channel = cursor.fetchone()[0]

    await ctx.bot.rest.edit_message(approval_channel, ctx.options.id, content=f"Accepted by {ctx.author.mention}.",
                                    embed=embed)

    ## actually send to warn channel.

    cursor.execute("SELECT punishment_channel FROM server_data")
    response = cursor.fetchone()[0]

    embed.colour = "#D22B2B"

    warningmsg = await ctx.bot.rest.create_message(channel=response, content=f"{staff_affected.mention}", embed=embed)
    await ctx.respond(f"Accepted warn request {ctx.options.id}", flags=hikari.MessageFlag.EPHEMERAL)

    try:
     await staff_affected.send(content=f"Hey, {staff_affected.mention} You've been warned. Go into #warnings to look at the reasoning.\nIf you believe this was a mistake please make a ticket.")
    except:
     print("Couldn't DM the user about warning.")

    try:
     await issuer.send(f"Your warn request, {ctx.options.id} Was accepted by: ``{ctx.member.username}`` :tada: \nReasoning: ``{ctx.options.reason}``")
    except:
     print("Couldn't DM the moderator about the success.")

    ctx.bot.d[f"{ctx.options.id}_warning_embed"] = None
    ctx.bot.d[f"{ctx.options.id}_warning_staff"] = None
    ctx.bot.d[f"{ctx.options.id}_warning_issuer"] = None

    cursor.execute(f"SELECT * FROM staff_data WHERE user_id={staff_affected.id}")
    result = cursor.fetchone()

    user_id = result[0]
    warnings = result[1]
    strikes = result[2]
    warning_links = result[3]

    cursor.execute(f"UPDATE staff_data SET WARNINGS={warnings+1} WHERE user_id={staff_affected.id}")
    conn.commit()

@plugin.command()
@lightbulb.option(name="user", description="Username of the staff getting infracted.", type=hikari.Member,
                  required=True)
@lightbulb.option(name="reason", description="Reasoning behind infraction.", type=str, required=True)
@lightbulb.option(name="outcome", description="Outcome of this infraction.", type=str, required=True)
@lightbulb.command("warn", "Allows management to create a warn request.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def staff_warn(ctx: lightbulb.Context):
    cursor.execute("SELECT management_role FROM server_data")
    response = cursor.fetchone()[0]
    print(response)

    bot = ctx.app
    roles = ctx.member.get_roles()

    print(roles)

    if response in ctx.member.role_ids:
        cursor.execute(f"SELECT * FROM staff_data WHERE user_id={ctx.options.user.id}")
        result = cursor.fetchone()
        if result is None:
            await ctx.respond(f"{ctx.options.user.mention} Is not a staff member, you may not warn them. ❌", flags=hikari.MessageFlag.EPHEMERAL)
            return

        embed = hikari.Embed(
            title="Warning 📉",
            description=f"{ctx.options.user.mention} \n -̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶ \n Reason: ``{ctx.options.reason}`` \n Outcome: ``{ctx.options.outcome}`` \n Punishment issued by: {ctx.author.mention} \n -̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶ \n",
            colour="#f00"
        )

        embed.set_thumbnail("https://cdn.discordapp.com/emojis/1122289009071247511.webp?size=96&quality=lossless")

        embed.set_footer(text="Waiting to be approved.")

        cursor.execute("SELECT approval_channel FROM server_data")
        approval_channel = cursor.fetchone()[0]

        cursor.execute("SELECT director_role FROM server_data")
        director_role = cursor.fetchone()[0]

        ActionRow = bot.rest.build_message_action_row()
        ActionRow.add_interactive_button(hikari.ButtonStyle.SUCCESS, "accept_req", label="Accept", is_disabled=False)
        ActionRow.add_interactive_button(hikari.ButtonStyle.DANGER, "deny_req", label="Deny", is_disabled=False)

        msg = await bot.rest.create_message(channel=approval_channel, embed=embed,
                                            content=f"<@&{director_role}>, respond with -accept_warn/deny_warn [msg_id]")
        await ctx.respond("Warn request sent successfully! a director must approve of this request.",
                          flags=hikari.MessageFlag.EPHEMERAL)

        embed.set_footer(f"Waiting to be approved, MSGID: {msg.id}")

        await msg.edit(embed=embed, content=f"<@&{director_role}>, respond with /accept_warn or /deny_warn [msg_id]")

        ctx.bot.d[f"{msg.id}_warning_embed"] = embed
        ctx.bot.d[f"{msg.id}_warning_staff"] = ctx.options.user
        ctx.bot.d[f"{msg.id}_warning_issuer"] = ctx.member
    else:
        await ctx.respond(f"You do not have permission to run this, only <@&{response}> and above may run this. ❌",
                          flags=hikari.MessageFlag.EPHEMERAL)


@plugin.command()
@lightbulb.option(name="user", description="Username of the staff getting infracted.", type=hikari.Member,
                  required=True)
@lightbulb.option(name="reason", description="Reasoning behind infraction.", type=str, required=True)
@lightbulb.option(name="outcome", description="Outcome of this infraction.", type=str, required=True)
@lightbulb.command("strike", "Allows management to create a strike request.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def staff_strike(ctx: lightbulb.Context):
    cursor.execute("SELECT management_role FROM server_data")
    response = cursor.fetchone()[0]
    print(response)

    bot = ctx.app
    roles = ctx.member.get_roles()

    print(roles)

    if response in ctx.member.role_ids:
        cursor.execute(f"SELECT * FROM staff_data WHERE user_id={ctx.options.user.id}")
        result = cursor.fetchone()
        if result is None:
            await ctx.respond(f"{ctx.options.user.mention} Is not a staff member, you may not strike them. ❌", flags=hikari.MessageFlag.EPHEMERAL)
            return

        embed = hikari.Embed(
            title="Strike 🛑",
            description=f"{ctx.options.user.mention} \n -̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶ \n Reason: ``{ctx.options.reason}`` \n Outcome: ``{ctx.options.outcome}`` \n Punishment issued by: {ctx.author.mention} \n -̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶-̶ \n",
            colour="#f00"
        )

        embed.set_thumbnail("https://cdn.discordapp.com/emojis/1122289009071247511.webp?size=96&quality=lossless")

        embed.set_footer(text="Waiting to be approved.")

        cursor.execute("SELECT approval_channel FROM server_data")
        approval_channel = cursor.fetchone()[0]

        cursor.execute("SELECT director_role FROM server_data")
        director_role = cursor.fetchone()[0]

        msg = await bot.rest.create_message(channel=approval_channel, embed=embed,
                                            content=f"<@&{director_role}>, respond with -accept_strike/deny_strike [msg_id]")
        await ctx.respond("Strike request sent successfully! a director must approve of this request.",
                          flags=hikari.MessageFlag.EPHEMERAL)

        embed.set_footer(f"Waiting to be approved, MSGID: {msg.id}")

        await msg.edit(embed=embed, content=f"<@&{director_role}>, respond with /accept_strike or /deny_strike [msg_id]")

        ctx.bot.d[f"{msg.id}_strike_embed"] = embed
        ctx.bot.d[f"{msg.id}_strike_staff"] = ctx.options.user
        ctx.bot.d[f"{msg.id}_strike_issuer"] = ctx.member
    else:
        await ctx.respond(f"You do not have permission to run this, only <@&{response}> and above may run this. ❌",
                          flags=hikari.MessageFlag.EPHEMERAL)


## STRIKE DIRECTOR COMMANDS

@plugin.command()
@lightbulb.option(name="id", description="ID of request to deny")
@lightbulb.option(name="reason", description="Reason for the denial.")
@lightbulb.command("deny_strike", description="Denies. a warn request")
@lightbulb.implements(lightbulb.SlashCommand)
async def deny_strike(ctx: lightbulb.Context):
    embed = ctx.bot.d[f"{ctx.options.id}_strike_embed"]
    staff_affected = ctx.bot.d[f"{ctx.options.id}_strike_staff"]
    issuer = ctx.bot.d[f"{ctx.options.id}_strike_issuer"]
    roles = ctx.member.role_ids

    cursor.execute("SELECT director_role FROM server_data")
    response = cursor.fetchone()[0]

    if not response in roles:
        await ctx.respond("You arent allowed to deny strike requests. ❌", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if embed.title == "Strike 🛑":
        embed.colour = "#00FF00"
        embed.set_footer(text=f"Toms River Roleplay, copyright @axisdadev 2023 🌍")
    else:
        await ctx.respond("Invalid request id, was request already accepted or denied? 🤷", flags=hikari.MessageFlag.EPHEMERAL)
        return

    cursor.execute("SELECT approval_channel FROM server_data")
    approval_channel = cursor.fetchone()[0]

    await ctx.bot.rest.edit_message(approval_channel, ctx.options.id, content=f"Denied by {ctx.author.mention}. ❌",
                                    embed=embed)

    await ctx.respond(f"Denied strike request {ctx.options.id}", flags=hikari.MessageFlag.EPHEMERAL)

    try:
     await issuer.send(f"Your strike request, {ctx.options.id} Was denied by: ``{ctx.member.username}`` :no_entry_sign: \nReasoning: ``{ctx.options.reason}``")
    except:
     print("Couldn't DM the moderator about the denial.")

    ctx.bot.d[f"{ctx.options.id}_strike_embed"] = None
    ctx.bot.d[f"{ctx.options.id}_strike_staff"] = None
    ctx.bot.d[f"{ctx.options.id}_strike_issuer"] = None

@plugin.command()
@lightbulb.option(name="id", description="id of request to accept.")
@lightbulb.option(name="reason", description="reason for the approval.")
@lightbulb.command("accept_strike", description="accepts a strike request")
@lightbulb.implements(lightbulb.SlashCommand)
async def accept_strike(ctx: lightbulb.Context):
    embed = ctx.bot.d[f"{ctx.options.id}_strike_embed"]
    staff_affected = ctx.bot.d[f"{ctx.options.id}_strike_staff"]
    issuer = ctx.bot.d[f"{ctx.options.id}_strike_issuer"]
    roles = ctx.member.role_ids

    cursor.execute("SELECT director_role FROM server_data")
    response = cursor.fetchone()[0]

    if not response in roles:
        await ctx.respond("You arent allowed to accept strike requests. ❌", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if embed.title == "Strike 🛑":
        embed.colour = "#00FF00"
        embed.set_footer(text=f"Toms River Roleplay, copyright @axisdadev 2023 🌍")
    else:
        await ctx.respond("Invalid request id, was request already accepted or denied?", flags=hikari.MessageFlag.EPHEMERAL)
        return

    cursor.execute("SELECT approval_channel FROM server_data")
    approval_channel = cursor.fetchone()[0]

    await ctx.bot.rest.edit_message(approval_channel, ctx.options.id, content=f"Accepted by {ctx.author.mention}.",
                                    embed=embed)

    ## actually send to warn channel.

    cursor.execute("SELECT punishment_channel FROM server_data")
    response = cursor.fetchone()[0]

    embed.colour = "#D22B2B"

    warningmsg = await ctx.bot.rest.create_message(channel=response, content=f"{staff_affected.mention}", embed=embed)
    await ctx.respond(f"Accepted strike request {ctx.options.id}", flags=hikari.MessageFlag.EPHEMERAL)

    try:
     await staff_affected.send(content=f"Hey, {staff_affected.mention} You've been striked. Go into #warnings to look at the reasoning.\nIf you believe this was a mistake please make a ticket.")
    except:
     print("Couldn't DM the user about the strike.")

    try:
     await issuer.send(f"Your strike request, {ctx.options.id} Was accepted by: ``{ctx.member.username}`` :tada: \nReasoning: ``{ctx.options.reason}``")
    except:
     print("Couldn't DM the moderator about the success.")

    ctx.bot.d[f"{ctx.options.id}_strike_embed"] = None
    ctx.bot.d[f"{ctx.options.id}_strike_staff"] = None
    ctx.bot.d[f"{ctx.options.id}_strike_issuer"] = None

    cursor.execute(f"SELECT * FROM staff_data WHERE user_id={staff_affected.id}")
    result = cursor.fetchone()

    user_id = result[0]
    warnings = result[1]
    strikes = result[2]
    warning_links = result[3]

    cursor.execute(f"UPDATE staff_data SET STRIKES={strikes+1} WHERE user_id={staff_affected.id}")
    conn.commit()


def load(bot):
    botVar = bot
    print("management.py loaded.")
    print(botVar)
    bot.add_plugin(plugin)


def unload(bot):
    print("utility.py unloaded.")
    bot.remove_plugin(plugin)
