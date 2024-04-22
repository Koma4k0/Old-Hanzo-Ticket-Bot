import discord
import asyncio
import json
import sqlite3
import datetime
import chat_exporter
import io
from discord.interactions import Interaction
from vars import *
from discord.ext import commands
from cogs.Selectables.Payment import *


class StaffReport(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        button = discord.ui.Button(label="Report Staff", style=discord.ButtonStyle.link, url="https://docs.google.com/forms/d/e/1FAIpQLSfiGl5ueCDxVv81SoV_2qS7U1N7F8HmDirHS2t5aMwPTGYvBw/viewform?usp=sf_link")
        self.add_item(button)


class StaffRating(discord.ui.View):
    def __init__(self, bot, staff):
        self.bot = bot
        super().__init__(timeout=None)
        self.staff = staff
        self.has_rated = False

    @discord.ui.select(
        custom_id="StaffRating",
        placeholder="Rate the ticket support",
        options=[
            discord.SelectOption(
                label="⭐",
                value="1Star"
            ),
            discord.SelectOption(
                label="⭐⭐",
                value="2Star"
            ),
            discord.SelectOption(
                label="⭐⭐⭐",
                value="3Star"
            ),
            discord.SelectOption(
                label="⭐⭐⭐⭐",
                value="4Star"
            ),
            discord.SelectOption(
                label="⭐⭐⭐⭐⭐",
                value="5Star"
            )
        ]
    )

    async def callback(self, interaction, select):
        
        rating = 0
        if interaction.data['values'][0] == "1Star":
            rating = 1
        elif interaction.data['values'][0] == "2Star":
            rating = 2
        elif interaction.data['values'][0] == "3Star":
            rating = 3
        elif interaction.data['values'][0] == "4Star":
            rating = 4
        elif interaction.data['values'][0] == "5Star":
            rating = 5

        connStaff = sqlite3.connect('staffstats.db')
        curStaff = connStaff.cursor()

        curStaff.execute("SELECT * FROM staffer WHERE discord_id=?", (self.staff,))
        staffer_row = curStaff.fetchone()

        if not staffer_row:
            curStaff.execute("INSERT INTO staffer (discord_id, staff_rating) VALUES (?, ?)", (self.staff, rating))
        else:
            curStaff.execute("UPDATE staffer SET staff_rating = staff_rating + ? WHERE discord_id=?", (rating, self.staff,))
            curStaff.execute("UPDATE staffer SET total_rates = total_rates + 1 WHERE discord_id=?", (self.staff,))
        connStaff.commit()
        connStaff.close()
        await interaction.message.edit(view=StaffReport(self.bot))
        await interaction.response.send_message("thank you for the rate!", ephemeral=True)