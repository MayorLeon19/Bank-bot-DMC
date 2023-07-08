import sqlite3

import discord
from discord import ui, TextStyle
from discord.ext import commands
from discord.utils import get


class Claim_Zakaz(ui.Modal, title="Создание заказа"):
    def __init__(self, item, bot: commands.Bot) -> None:
        super().__init__()
        self.item = int(item)
        self.bot = bot


    quest1 = ui.TextInput(label='Готовы ли вы платить 15 аров в неделю?', placeholder="Да")
    quest2 = ui.TextInput(label='Есть ли у вас схематика или идея для оформления?', placeholder="Да")
    quest3 = ui.TextInput(label='Как часто вы будет пополнять лавку?', placeholder="Каждый день, в 3 часа дня по МСК")
    quest4 = ui.TextInput(label='Примеры товаров в вашей лавки', placeholder="Несколько примеров...", style=TextStyle.paragraph)


    async def on_submit(self, interaction: discord.Interaction):
        price = cursor.execute("SELECT price FROM lavka WHERE id = {}".format(int(self.item))).fetchone()[0]
        channel = self.bot.get_channel(1126557461772505118)
        embed = discord.Embed(title=f"{interaction.user.name} подал заявку на покупку лавки!", description="Подробная информация:", color=0x2b2d31)
        embed.add_field(name="Кто создал заявку:", value=f"{interaction.user.name}", inline=True)
        embed.add_field(name="Номер лавки: ", value=self.item, inline=True)
        embed.add_field(name="Цена данной лавки:", value=f"{price} <:deepslate_diamond_ore:1126563150922272768>", inline=True)
        embed.add_field(name="Готовы ли вы платить 15 аров в неделю?:", value=self.quest1, inline=True)
        embed.add_field(name="Есть ли у вас схематика или идея для оформления?:", value=self.quest2, inline=True)
        embed.add_field(name="Как часто вы будет пополнять лавку?:", value=self.quest3, inline=True)
        embed.add_field(name="Примеры товаров в вашей лавки:", value=self.quest4, inline=True)
        message = await channel.send(embed=embed, view=Canel_lavka(self.bot))
        cursor.execute(
            f"INSERT INTO messages_lavka VALUES ({interaction.user.id}, {message.id}, 0, \"{self.quest1}\", \"{self.quest2}\", \"{self.quest3}\", \"{self.quest4}\", {self.item}, NULL)")
        connection.commit()
        await interaction.response.send_message(f"Вы успешно подали заявку на покупку {int(self.item)} лавки!", ephemeral=True)



class Select(discord.ui.Select):
    def __init__(self, items, bot: commands.Bot):
        options = []
        self.bot = bot
        for i in items:
            options.append(discord.SelectOption(label=f"Купить {i[0]} лавку", value=f'Лавка {i[0]}', description=f'Подать заявку на покупку, стоимость - {i[1]} АР', emoji='💲'))
        print(items)
        super().__init__(placeholder="Выберите лавку", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        string = self.values[0]
        number = string.replace("Лавка ", "")
        free = cursor.execute("SELECT free FROM lavka WHERE id = {}".format(int(number))).fetchone()[0]
        if free:
            price = cursor.execute("SELECT price FROM lavka WHERE id = {}".format(int(number))).fetchone()[0]
            await interaction.response.send_modal(Claim_Zakaz(number, self.bot))

class SelectView(discord.ui.View):
    def __init__(self, items, bot: commands.Bot, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(Select(items, bot))

class Buy(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(style=discord.ButtonStyle.gray, label="Купить лавку", emoji='➕', custom_id='persistent_view:buy_lavka')
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        gg = cursor.execute("SELECT id, price FROM lavka WHERE free = 1").fetchall()
        if not gg:
            await interaction.response.send_message("Ошибка! Нет свободных лавок.", ephemeral=True)
        else:
            await interaction.response.send_message("Список лавок для покупки: ", view=SelectView(gg, self.bot), ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="Купить лицензию", emoji='➕',
                       custom_id='persistent_view:buy_licenziya')
    async def buy_licen(self, interaction: discord.Interaction, button: discord.ui.Button):
        have = cursor.execute("SELECT have FROM licenzies_torg WHERE owner_id = {}".format(interaction.user.id)).fetchone()[0]
        if have:
            await interaction.response.send_message("Ошибка! У вас уже есть лицензия на торговлю.", ephemeral=True)
        else:
            if cursor.execute(f"SELECT text_channel_id FROM tickets WHERE owner_id = {interaction.user.id}").fetchone() is not None:
                channel = cursor.execute("SELECT text_channel_id FROM tickets WHERE owner_id = {}".format(interaction.user.id)).fetchone()[0]
                chan = self.bot.get_channel(channel)
                await chan.delete()
                cursor.execute("DELETE FROM tickets WHERE owner_id = {}".format(interaction.user.id))
                connection.commit()
            text_channel = await interaction.guild.create_text_channel(name=f'Получение лицензии-{interaction.user}',
                                                                       category=get(interaction.guild.categories,
                                                                                    id=1126556408444362843))
            await text_channel.set_permissions(interaction.user, send_messages=True, read_messages=True)

            embed = discord.Embed(title="Вы успешно создали тикет на получение лицензии!", description="Подробная информация:",
                                  color=0x2b2d31)
            embed.add_field(name="Кто создал тикет: ", value=interaction.user.mention, inline=True)
            message = await text_channel.send(embed=embed, view=Canel_license(self.bot))
            cursor.execute("INSERT INTO tickets(owner_id, text_channel_id, type, general_message) VALUES ({}, {}, {}, {})".format(interaction.user.id, text_channel.id, 2, message.id))
            connection.commit()
            await interaction.response.send_message("Тикет успешно создан!", ephemeral=True)


class Canel_license(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='✅', custom_id='persistent_view:licenziya_yes')
    async def true(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.get_role(1126200636459995254) or interaction.user.get_role(1125463556469567588):
            owner = cursor.execute("SELECT owner FROM channel_licenziya WHERE text_channel_id = {}".format(
                interaction.channel.id)).fetchone()[0]
            await interaction.channel.delete()
            cursor.execute("DELETE FROM channel_licenziya WHERE owner = {}".format(interaction.user.id))
            connection.commit()
            cursor.execute("UPDATE licenzies_torg SET have = 1 WHERE owner_id = {}".format(owner))
            connection.commit()
            user = self.bot.get_user(owner)
            await user.send("Вам успешно выдана лицензия!")
        else:
            await interaction.response.send_message("У вас нет прав.", ephemeral=True)


    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='❌', custom_id='persistent_view:licenziya_no')
    async def false(self, interaction: discord.Interaction, button: discord.ui.Button):
        owner = cursor.execute("SELECT owner_id FROM tickets WHERE text_channel_id = {}".format(interaction.channel.id)).fetchone()[0]
        user = self.bot.get_user(owner)
        if interaction.user.get_role(1126200636459995254) or interaction.user.get_role(1125463556469567588):
            await interaction.channel.delete()
            cursor.execute("DELETE FROM tickets WHERE owner = {}".format(interaction.user.id))
            connection.commit()

            await user.send("Ваш тикет был обработан, а затем отклонен!")
        elif owner == interaction.user.id:
            cursor.execute("DELETE FROM channel_licenziya WHERE owner = {}".format(interaction.user.id))
            connection.commit()
            await interaction.response.send_message("Вы успешно закрыли тикет!", ephemeral=True)
            await user.send("Вы успешно закрыли тикет!")


class Canel_lavka(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='✅', custom_id='persistent_view:lavka_yes')
    async def true(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.get_role(1126200636459995254) or interaction.user.get_role(1125463556469567588):
            owner = cursor.execute("SELECT owner_id FROM messages_lavka WHERE message_id = {}".format(interaction.message.id)).fetchone()[0]
            member = self.bot.get_user(owner)
            clicked = cursor.execute("SELECT clicked FROM messages_lavka WHERE message_id = {}".format(interaction.message.id)).fetchone()[0]
            if clicked:
                await interaction.response.send_message("На данную лавку уже ответили!")
            else:
                lavka = cursor.execute("SELECT lavka FROM messages_lavka WHERE message_id = {}".format(interaction.message.id)).fetchone()[0]
                cursor.execute("UPDATE messages_lavka SET clicked = 1 WHERE owner_id = {}".format(owner))
                connection.commit()
                cursor.execute("UPDATE messages_lavka SET otvet = 1 WHERE owner_id = {}".format(owner))
                connection.commit()
                embed = interaction.message.embeds[0]
                embed.description = f"На данную заявку ответил: {interaction.user.mention}\n\nОтвет: Принята\n\nПодробная информация:"
                await interaction.message.edit(embed=embed)
                await member.send(f"Ваша заявка на покупку {lavka} была принята!")


        else:
            await interaction.response.send_message("У вас нет прав.", ephemeral=True)


    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='❌', custom_id='persistent_view:lavka_no')
    async def false(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.get_role(1126200636459995254) or interaction.user.get_role(1125463556469567588):
            owner = cursor.execute(
                "SELECT owner_id FROM messages_lavka WHERE message_id = {}".format(interaction.message.id)).fetchone()[
                0]
            member = self.bot.get_user(owner)
            clicked = cursor.execute(
                "SELECT clicked FROM messages_lavka WHERE message_id = {}".format(interaction.message.id)).fetchone()[0]
            if clicked:
                await interaction.response.send_message("На данную лавку уже ответили!")
            else:
                lavka = cursor.execute(
                    "SELECT lavka FROM messages_lavka WHERE message_id = {}".format(interaction.message.id)).fetchone()[
                    0]
                cursor.execute("UPDATE messages_lavka SET clicked = 1 WHERE owner_id = {}".format(owner))
                connection.commit()
                cursor.execute("UPDATE messages_lavka SET otvet = 0 WHERE owner_id = {}".format(owner))
                connection.commit()
                embed = interaction.message.embeds[0]
                embed.description = f"На данную заявку ответил: {interaction.user.mention}\n\nОтвет: Отклонена\n\nПодробная информация:"
                await interaction.message.edit(embed=embed)
                await member.send(f"Ваша заявка на покупку {lavka} была принята!")


class shops(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.add_view(Buy(bot))
        bot.add_view(Canel_license(bot))
        bot.add_view(Canel_lavka(self.bot))


    @commands.command()
    async def buy_license(self, ctx):
        await ctx.channel.send(view=Buy(bot=self.bot))
        await ctx.message.delete()


    @commands.Cog.listener()
    async def on_ready(self):
        global connection, cursor
        connection = sqlite3.connect("main.db")
        cursor = connection.cursor()
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
        cursor.execute("""CREATE TABLE IF NOT EXISTS tickets ( 
                                            				owner_id INT,
                                            				text_channel_id INT,
                                            			    type INT,
                                            			    general_message	
                                            		)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS messages_lavka ( 
                                                    				owner_id INT,
                                                    				message_id INT,
                                                    				clicked INT,
                                                    				quest1 TEXT,
                                                    				quest2 TEXT,
                                                    				quest3 TEXT,
                                                    				quest4 TEXT,
                                                    				lavka INT,
                                                    				otvet INT
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
    await bot.add_cog(shops(bot), guild=discord.Object(id=1125004551066484767))