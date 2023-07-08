from datetime import datetime
import asyncio
import discord
import discord.ext.commands as commands
import sqlite3
import asyncio
import psutil
from discord import ui, app_commands
from discord.utils import get

global cursor, connection
token = ''
global embed_color
embed_color = 0x36393f


class PersistentViewBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix='!', intents=discord.Intents.all())

    async def setup_hook(self):
        await bot.load_extension("cogs.shops")
        await bot.tree.sync(guild=discord.Object(id=1125004551066484767))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("У вас нет прав на выполнение данной команды.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("Команда не найдена!")

    async def on_ready(self):
        CPU = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        percentmem = int(mem.percent)
        print(
            f"\n_-_-_-_-_-_-_-_-_-_-_-_-\n\n𝕯𝖊𝖛𝖊𝖑𝖔𝖕 𝕸𝖆𝖞𝖔𝖗𝕷𝖊𝖔𝖓\n\n-_-_-_-_-_-_-_-_-_-_-_-_\nИнформация о боте:\nЗагруженность процессора: {CPU}%\nЗагруженность памяти: {percentmem}%")
        print(f"--------\nТокен: {token}")

        while True:
            await self.change_presence(status=discord.Status.idle, activity=discord.Activity(name=f'за чебоксарами',
                                                                                             type=discord.ActivityType.watching))  # Идёт инфа о команде помощи (префикс изменить)
            await asyncio.sleep(15)
bot = PersistentViewBot()
@bot.hybrid_command(name='embed', description="Выводит embed сообщение", with_app_command=True)
@app_commands.guilds(discord.Object(id=1125844020892012656))
async def first_command(ctx):
    await ctx.channel.send("Hello!")
bot.run(token)