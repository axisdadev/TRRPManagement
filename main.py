import hikari, lightbulb, time, pathlib

secret = "MTEyNjUzMjU1MTA2Mjg1OTkxOA.GCBXA-.jYvbk2QtH_RaX-Ezhgmmz3ro0qT-FX5GNUnbJ0"

bot = lightbulb.BotApp(token=secret,intents=hikari.Intents.ALL, prefix="-")

@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(f"Something went wrong during invocation of command `{event.context.command.name}`.")
        print(event.exception)
        raise event.exception

@bot.listen(hikari.StartedEvent)
async def on_start(ctx):
    await bot.update_presence(
        status=hikari.Status.ONLINE,
        activity=hikari.Activity(
            name="Toms River Roleplay, https://discord.gg/HepWwBG2Zw",
            type=hikari.ActivityType.PLAYING,
        ),
    )

path = "extensions"

bot.load_extensions_from(path)

bot.run()

