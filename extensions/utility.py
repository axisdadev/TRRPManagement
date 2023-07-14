import sqlite3

import hikari, lightbulb, time, pathlib, aiosqlite


conn = sqlite3.connect(database="database.db")
cursor = None

plugin = lightbulb.Plugin("utility")
botVar = None


@plugin.command()
@lightbulb.command("ping", "Checks bot latency.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def ping(ctx: lightbulb.Context):
    timeNow = time.time()
    msg = await ctx.respond("Pong! :ping_pong:")
    timeThen = time.time()
    await msg.edit(f"Pong! {round(timeNow-timeThen)}ms :ping_pong: :fire:")

def load(bot):
    botVar = bot
    print("utility.py loaded.")
    print(botVar)
    bot.add_plugin(plugin)

def unload(bot):
    print("utility.py unloaded.")
    bot.remove_plugin(plugin)