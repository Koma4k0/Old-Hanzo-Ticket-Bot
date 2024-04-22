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
from cogs.Buttons.Buttons import *

class PermWoofer(discord.ui.View):
    def __init__(self, bot, selected_product):
        self.bot = bot
        super().__init__(timeout=None)
        self.selected_product = selected_product

    @discord.ui.select(
        custom_id="Permanent HWID Spoofer",
        placeholder="Chose the subscription duration",
        options=[
            discord.SelectOption(
                label="One Time",
                description="$19.99",
                emoji=emoji_money,
                value="OneTime"
            ),
            discord.SelectOption(
                label="Unlimited Uses",
                description="$49.99",
                emoji=emoji_money,
                value="Lifetime"
            )
        ]
    )

    async def callback(self, interaction, select):
        PlanChosen = interaction.data['values'][0]
        print(interaction.data)

        embed = discord.Embed(
            title=f"{emoji_money2} Purchase {emoji_money2}",
            description=(
                f"Follow the instructions to continue with your ticket. \n\n{emoji_hanzo} **Product Choosen** {emoji_hanzo}\n```{self.selected_product}```\n{emoji_hanzo} **Subscription Duration** {emoji_hanzo}\n```{PlanChosen}```\n{emoji_info} Payment Method {emoji_info}\nClick below to choose the payment method you prefer\n\n"
            ),
            color=default_color
        )
        
        if PlanChosen == "OneTime":
            await interaction.message.edit(embed=embed, view=PaymentMethodSelectable(self.bot, self.selected_product, PlanChosen,"19.99"))            
        elif PlanChosen == "Lifetime":
            await interaction.message.edit(embed=embed, view=PaymentMethodSelectable(self.bot, self.selected_product, PlanChosen,"49.99"))   

        await interaction.response.defer()

class PrivateFN(discord.ui.View):
    def __init__(self, bot, selected_product):
        self.bot = bot
        super().__init__(timeout=None)
        self.selected_product = selected_product

    @discord.ui.select(
        custom_id="Private Fortnite Cheat",
        placeholder="Chose the subscription duration",
        options=[
            discord.SelectOption(
                label="1 Day",
                description="$12.99",
                emoji=emoji_money,
                value="1Day"
            ),
            discord.SelectOption(
                label="1 Week",
                description="$29.99",
                emoji=emoji_money,
                value="Week"
            ),
            discord.SelectOption(
                label="1 Month",
                description="$89.99",
                emoji=emoji_money,
                value="Month"
            )
        ]
    )

    async def callback(self, interaction, select):
        PlanChosen = interaction.data['values'][0]
        print(interaction.data)

        embed = discord.Embed(
            title=f"{emoji_money2} Purchase {emoji_money2}",
            description=(
                f"Follow the instructions to continue with your ticket. \n\n{emoji_hanzo} **Product Choosen** {emoji_hanzo}\n```{self.selected_product}```\n{emoji_hanzo} **Subscription Duration** {emoji_hanzo}\n```{PlanChosen}```\n{emoji_info} Payment Method {emoji_info}\nClick below to choose the payment method you prefer\n\n"
            ),
            color=default_color
        )
        
        if PlanChosen == "1Day":
            await interaction.message.edit(embed=embed, view=PaymentMethodSelectable(self.bot, self.selected_product, PlanChosen,"12.99"))            
        elif PlanChosen == "Week":
            await interaction.message.edit(embed=embed, view=PaymentMethodSelectable(self.bot, self.selected_product, PlanChosen,"29.99"))   
        elif PlanChosen == "Month":
            await interaction.message.edit(embed=embed, view=PaymentMethodSelectable(self.bot, self.selected_product, PlanChosen,"89.99"))   

        await interaction.response.defer()

class Cheats(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="Products",
        placeholder="Choose a product",
        options=[
            discord.SelectOption(
                label="Permanent HWID Spoofer",
                emoji=emoji_hanzo,
                value="PermSpoofer"
            ),
            discord.SelectOption(
                label="Hanzo Fortnite Cheat",
                emoji=emoji_hanzo,
                value="PrivateFNCheat"
            )
        ]
    )
    async def callback(self, interaction, select):

        ChoosenProduct = interaction.data['values'][0]
        if ChoosenProduct == "PermSpoofer":
            ChoosenProduct = "Permanent HWID Spoofer"
        elif ChoosenProduct == "PrivateFNCheat":
            ChoosenProduct = "Private Fortnite Cheats"

        embed = discord.Embed(
            title=f"{emoji_money2} Purchase {emoji_money2}",
            description=(
                f"To proceed with your ticket, please make sure to follow the instructions provided. \n\n{emoji_hanzo} **Product Choosen** {emoji_hanzo}\n```{ChoosenProduct}```\n{emoji_info} Choose Duration {emoji_info}\nClick below to choose the subscription duration"
            ),
            color=default_color
        )

        if ChoosenProduct == "Permanent HWID Spoofer":
            await interaction.message.edit(embed=embed, view=PermWoofer(self.bot, ChoosenProduct))
        elif ChoosenProduct == "Private Fortnite Cheats":
            await interaction.message.edit(embed=embed, view=PrivateFN(self.bot, ChoosenProduct))
        await interaction.response.defer()