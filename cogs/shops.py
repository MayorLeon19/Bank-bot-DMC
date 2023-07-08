import sqlite3

import discord
from discord.ext import commands

class Claim_Zakaz(ui.Modal, title="Создание заказа"):
    count = ui.TextInput(label='Количество предмета: ')

    def __init__(self, item, bot: commands.Bot) -> None:
        super().__init__()
        self.item = item
        self.bot = bot



    async def on_submit(self, interaction: discord.Interaction):



class Select(discord.ui.Select):
    def __init__(self, items):
        options = []
        for i in items:
            options.append(discord.SelectOption(label="Купить лавку", value=f'{i[0]}', description=f'Подать заявку на покупку {i[0]} лавки.', emoji='💲'))
        print(items)
        super().__init__(placeholder="Выберите лавку", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        free = cursor.execute("SELECT free FROM lavka WHERE id = {}".format(self.values[0])).fetchone()[0]
        if free:
            price = cursor.execute("SELECT price FROM lavka WHERE id = {}".format(self.values[0])).fetchone()[0]

class SelectView(discord.ui.View):
    def __init__(self, items, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(Select(items))

class Buy(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(style=discord.ButtonStyle.gray, label="Купить лавку", emoji='➕', custom_id='persistent_view:buy_lavka')
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        have = cursor.execute("SELECT have FROM licenzies_torg WHERE owner_id = {}".format(interaction.user.id)).fetchone()[0]
        if have:
            print("3")
            gg = cursor.execute("SELECT id, price FROM lavka WHERE free = 1").fetchall()
            print(gg)
            if not gg:
                print("1")
                await interaction.response.send_message("Ошибка! Нет свободных лавок.")
            else:
                print("2")
                await interaction.response.send_message("Есть лавки.", view=SelectView(gg))

class shops(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.add_view(Buy(bot))

    @commands.command()
    async def gg(self, ctx):
        await ctx.channel.send(view=Buy(bot=self.bot))


    @commands.Cog.listener()
    async def on_ready(self):
        global connection, cursor
        connection = sqlite3.connect("main.db")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                            				check_now TIMESTAMP, 
                            				check_other TIMESTAMP,
                            				count_lavka INT
                            		)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS lavka (
                                    				owner_id INT,
                                    				id INT UNIQUE,
                                    				start TIMESTAMP,
                                    				nick TEXT,
                                    				free INT,
                                    				price INT
                                    		)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS licenzies_torg (
                                            				owner_id INT,
                                            				nick TEXT UNIQUE,
                                            				have INT
                                            		)""")
        for guild in self.bot.guilds:
            for member in guild.members:
                if cursor.execute(f"SELECT owner_id FROM licenzies_torg WHERE owner_id = {member.id}").fetchone() is None:
                    cursor.execute(f"INSERT INTO licenzies_torg VALUES (\"{member.id}\", \"{member.name}\", 0)")
                    connection.commit()
                else:
                    pass
        connection.commit()
        connection.commit()

        print("Бот подключился к базе данных.")

    async def on_member_join(self, member):
        if cursor.execute(f"SELECT owner_id FROM licenzies_torg WHERE owner_id = {member.id}").fetchone() is None:
            cursor.execute(f"INSERT INTO licenzies_torg VALUES (\"{member.id}\", \"{member.name}\", 0)")
            connection.commit()
        else:
            pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(shops(bot), guild=discord.Object(id=1125844020892012656))