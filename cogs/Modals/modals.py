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
from cogs.Buttons.Buttons import *

########## test ###########

class AcceptDeclineReferral2(discord.ui.View):
    def __init__(self, bot, referral, reward):
        self.bot = bot
        super().__init__(timeout=None)
        self.selected_referal = referral
        self.reward = reward

    @discord.ui.button(label="Fufilled ✔", style = discord.ButtonStyle.green, custom_id="Accept")
    async def Accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        guild = self.bot.get_guild(guild_id)
        channel = self.bot.get_channel(emoji_hanzo)
        topic = interaction.channel.topic
        parts = topic.split(" | ")
        ticket_creator = int(parts[1])
        member = interaction.guild.get_member(ticket_creator)
        
        if owner_role_id in [role.id for role in member.roles]:
            with sqlite3.connect('referral.db') as connRF:
                cursorRF = connRF.cursor()
                conn = sqlite3.connect("interactions.db")
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM referrals WHERE channel_id = ?
                ''', (interaction.channel.id,))
                results = cursor.fetchall()             
                if results:
                    row = results[0] 
                    cursorRF.execute('SELECT * FROM referrals WHERE referral_code = ?', (row[8],))
                    cursorRF.execute('SELECT earnings FROM referrals WHERE referral_code = ?', (row[8],))
                    current_earnings = cursorRF.fetchone()[0] 
                    new_earnings = current_earnings + row[9]
                    cursorRF.execute('UPDATE referrals SET earnings = ? WHERE referral_code = ?', (new_earnings, row[8]))

                    connRF.commit()
                    embed = discord.Embed(
                        title=f"{emoji_money2} Earnings Action {emoji_money2}",
                        description=(
                            f"Referral: ```{row[8]}```\nStatus: ```Fufilled```\nUser Earn: ```${row[9]}```"
                        ),
                        color=default_color
                    )

                    embedLog = discord.Embed(
                        title=f"{emoji_money2} Earnings Action {emoji_money2}",
                        description=(
                            f"Referral: ```{row[8]}```\nStatus: ```Fufilled```\nUser Earn: ```${row[9]}```\nUser ID: ```{interaction.user.id}```"
                        ),
                        color=default_color
                    )

                    channel = interaction.guild.get_channel(ticket_logs)
                    await channel.send(embed=embedLog)
                    await channel.send(f"<@{interaction.user.id}>")
                    await interaction.message.delete()
                    await interaction.response.send_message(embed=embed)
                conn.close()   
                connRF.close()
        else:
            await interaction.response.send_message("Please, leave the choice to the owner!", ephemeral=True)

    @discord.ui.button(label="Un-Fufilled ❌", style = discord.ButtonStyle.red, custom_id="Decline")  
    async def Decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = self.bot.get_guild(guild_id)
        channel = self.bot.get_channel(emoji_hanzo)
        topic = interaction.channel.topic
        parts = topic.split(" | ")
        ticket_creator = int(parts[1])
        member = interaction.guild.get_member(ticket_creator)
        
        if owner_role_id in [role.id for role in member.roles]:
            conn = sqlite3.connect("interactions.db")
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM referrals WHERE channel_id = ?
            ''', (interaction.channel.id,))
            results = cursor.fetchall()
            conn.close()
            if results:
                row = results[0] 
                embed = discord.Embed(
                    title=f"{emoji_money2} Earnings Action {emoji_money2}",
                    description=(
                        f"Referral: ```{row[8]}```\nStatus: ```Payment Un-Fufilled```"
                    ),
                    color=default_color
                )
                
                embedLog = discord.Embed(
                    title=f"{emoji_money2} Earnings Action {emoji_money2}",
                    description=(
                        f"Referral: ```{row[8]}```\nStatus: ```Un-Fufilled```\nUser ID: ```{interaction.user.id}```"
                    ),
                    color=default_color
                )

                channel = interaction.guild.get_channel(ticket_logs)
                await channel.send(embed=embedLog)
                await channel.send(f"<@{interaction.user.id}>")
                await interaction.response.send_message(embed=embed)

            else:
                await interaction.response.send_message("Please, leave the choice to the owner!", ephemeral=True)

class PaidOrNotPaid2(discord.ui.View):
    def __init__(self, selected_product, selected_sub, payment_total, payment_method, invoiceID, member, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.selected_product = selected_product
        self.payment_total = payment_total
        self.selected_sub = selected_sub
        self.payment_method = payment_method
        self.invoiceID = invoiceID
        self.member = member


    @discord.ui.button(label="Fulfilled ✔", style=discord.ButtonStyle.green, custom_id="Accept")
    async def Accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        with sqlite3.connect('invoicesID.db') as conninvoices:
            cursorinvoices = conninvoices.cursor()
            member = interaction.guild.get_member(interaction.user.id)

            if owner_role_id in [role.id for role in member.roles]:
                conn = sqlite3.connect("interactions.db")
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM invoices WHERE channel_id = ?
                ''', (interaction.channel.id,))
                results = cursor.fetchall()
                conn.close()

                channel = self.bot.get_channel(interaction.channel.id)
                topic = interaction.channel.topic
                parts = topic.split(" | ")
                ticket_creator = int(parts[1])

                if results:
                    row = results[0] 
                    embedLog = discord.Embed(
                        title=f"{emoji_money2} Paid Product {emoji_money2}",
                        description=(
                            f"Product: ```{row[1]}```\n"
                            f"Product Sub: ```{row[2]}```\n"
                            f"Payment Method: ```{row[4]}```\n"
                            f"Payment Total: ```${row[3]}```\n"
                            f"Invoice ID: ```{row[5]}```\n"
                            f"User ID: ```{ticket_creator}```"
                        ),
                        color=default_color
                    )

                    conn = sqlite3.connect("invoicesID.db")
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO loyalty (discord_id, earnings)
                        VALUES (?, COALESCE((SELECT earnings FROM loyalty WHERE discord_id = ?), 0) + ?)
                    ''', (ticket_creator, ticket_creator, row[3]))
                    conn.commit()
                    conn.close()

                    channel = interaction.guild.get_channel(ticket_logs)

                    cursorinvoices.execute('''
                            INSERT INTO invoices 
                            (invoice_id, user_id, product, product_subscription, payment_method, payment_total, paid, date_and_time)
                            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (row[5], ticket_creator, row[1], row[2],
                            row[4], row[3], "True"))
                    conninvoices.commit()

                    await channel.send(embed=embedLog)
                    await channel.send(f"<@{ticket_creator}>")
                    await interaction.message.delete()
                    await interaction.response.send_message(embed=embedLog)
                else:
                    await interaction.response.send_message("No results found.", ephemeral=True)
            else:
                await interaction.response.send_message("Please, leave the choice to the owner!", ephemeral=True)
        conninvoices.close()

    @discord.ui.button(label="Un-Fufilled ❌", style = discord.ButtonStyle.red, custom_id="Decline")  
    async def Decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        with sqlite3.connect('invoicesID.db') as conninvoices:
            cursorinvoices = conninvoices.cursor()       
            member = interaction.guild.get_member(interaction.user.id)
            
            if owner_role_id in [role.id for role in member.roles]:
                channel = self.bot.get_channel(interaction.channel.id)
                topic = self.channel.topic
                parts = topic.split(" | ")
                ticket_creator = int(parts[1])
                conn = sqlite3.connect("interactions.db")
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM invoices WHERE channel_id = ?
                ''', (interaction.channel.id,))
                results = cursor.fetchall()
                conn.close()

                if results:
                    row = results[0] 
                    embedLog = discord.Embed(
                        title=f"{emoji_money2} Non-Paid Product {emoji_money2}",
                            description=(
                                f"Product: ```{row[1]}```\n"
                                f"Product Sub: ```{row[2]}```\n"
                                f"Payment Method: ```{row[4]}```\n"
                                f"Payment Total: ```${row[3]}```\n"
                                f"Invoice ID: ```{row[5]}```\n"
                                f"User ID: ```{ticket_creator}```"
                            ),
                        color=default_color
                    )

                    cursorinvoices.execute('''
                        INSERT INTO invoices 
                        (invoice_id, user_id, product, product_subscription, payment_method, payment_total, paid, date_and_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (self.invoiceID, interaction.user.id, self.selected_product, self.selected_sub,
                        self.payment_method, self.payment_total, "False"))
                    conninvoices.commit()

                    channel = interaction.guild.get_channel(ticket_logs)
                    await channel.send(embed=embedLog)
                    await channel.send(f"<@{interaction.user.id}>")
                    await interaction.message.delete()
                    await interaction.response.send_message(embed=embedLog)

            else:
                await interaction.response.send_message("Please, leave the choice to the owner!", ephemeral=True)
        conninvoices.close()

class PayPalNoReferral2(discord.ui.View):
    def __init__(self, selected_product, selected_sub, payment_total, payment_method, invoiceID, message, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.selected_product = selected_product
        self.payment_total = payment_total
        self.selected_sub = selected_sub
        self.payment_method = payment_method
        self.invoiceID = invoiceID
        self.invoiceMessage = message

    @discord.ui.button(label="Paid ✔", style = discord.ButtonStyle.green, custom_id="AlreadyPaid")  
    async def AlreadyPaidDef(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"{emoji_money2} Paid {emoji_money2}",
            description=(
                f"Great, thank you for optimizing the purchasing process. \n\n{emoji_hanzo} **Please, provide the transaction screenshot.** {emoji_hanzo}\n\n{emoji_hanzo} ** ATTENTION ** {emoji_hanzo}\n```Ensure that the screenshot clearly indicates that you have made the payment using the \"Friends and Family\" option.```"
            ),
            color=default_color
        )
        embed.set_image(url=ticket_paypal_transaction_link)
        await interaction.response.send_message(embed=embed, view=PaidOrNotPaid2(self.selected_product, self.selected_sub, self.payment_total, self.payment_method, self.invoiceID, interaction.user.id, self.bot))

##################################

class ReferalModal(discord.ui.Modal, title="Referal Redeem"):
    info_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Referal Code",
        required=True,
        placeholder="Insert here the referal code"
    )


    title_value = None
    ticket_mention = None

    def __init__(self, selected_product, selected_sub, payment_total, payment_method, message, invoiceID, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.selected_product = selected_product
        self.payment_total = payment_total
        self.selected_sub = selected_sub
        self.payment_method = payment_method
        self.message = message
        self.invoiceID = invoiceID

    def get_values(self):
        return self.title_value

    async def on_submit(self, interaction: discord.Interaction):
        with sqlite3.connect('referral.db') as connRF:
            cursorRF = connRF.cursor()
            cursorRF.execute('SELECT * FROM referrals WHERE referral_code = ?', (self.info_title.value,))
            connRF.commit()
            referral_data = cursorRF.fetchone()

            if not referral_data:
                embed = discord.Embed(
                    title=f"{emoji_money2} Earnings Action {emoji_money2}",
                    description=(
                        f"Error: ```Invalid Referral Code```"
                    ),
                    color=default_color
                )
                await interaction.response.send_message(embed=embed)
            else:

                conn = sqlite3.connect("interactions.db")
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM invoices WHERE channel_id = ?
                ''', (interaction.channel.id,))
                results = cursor.fetchall()
                conn.close()

                if results:
                    row = results[0] 

                    _, referral_code, earnings = referral_data
                    reward = round(float(row[3]) * (percentage_of_redeem / 100), 2)
                    cursorRF.execute('UPDATE referrals SET earnings = ? WHERE referral_code = ?', (earnings + reward, referral_code))
                    connRF.commit()


                    conn = sqlite3.connect("interactions.db")
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO referrals (
                            selected_product, selected_sub, payment_total, payment_method, invoice_id, paid, channel_id, referral, reward
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (self.selected_product, self.selected_sub, self.payment_total, row[3], row[5], False, interaction.channel.id, self.info_title.value, reward))
                    conn.commit()
                    conn.close()

                    channel = self.bot.get_channel(interaction.channel.id)
                    topic = interaction.channel.topic
                    parts = topic.split(" | ")
                    ticket_creator = int(parts[1])

                    conn = sqlite3.connect("invoicesID.db")
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT * FROM loyalty WHERE discord_id = ?
                    ''', (ticket_creator,))
                    resultsInv = cursor.fetchall()
                    conn.close()
                    
                    embedPayPal = discord.Embed(
                        title=f"{emoji_paypal} PayPal {emoji_paypal}",
                        description=(
                            f"Attention! To pay with PayPal, use only this email unless instructed otherwise by the owner.\n\n"
                            f"{emoji_hanzo} **PayPal Email** {emoji_hanzo}\n```{paypal_email}```\n"
                            f"{emoji_hanzo} **Total Payment ** {emoji_hanzo}\n```${row[3]}```\n"
                            f"{emoji_hanzo} **Invoice ID** {emoji_hanzo}\n```{row[5]}```\n"
                            f"{emoji_hanzo} **Referral** {emoji_hanzo}\n```{self.info_title.value}```\n"
                            f"{emoji_hanzo} **Best Practice** {emoji_hanzo}\n```- Send money as Family & Friendly \n- Set the invoice ID as payment description```"
                        ),
                        color=default_color
                    )

                    embedCrypto = discord.Embed(
                        title=f"{emoji_money2} Purchase {emoji_money2}",
                        description=(
                            f"Thank you for answering at the questions. Wait for a staffer. \n\n"
                            f"{emoji_hanzo} **Product Choosen** {emoji_hanzo}\n```{row[1]}```\n"
                            f"{emoji_hanzo} **Subscription Duration** {emoji_hanzo}\n```{row[2]}```\n"
                            f"{emoji_hanzo} **Payment Method** {emoji_hanzo}\n```Crypto```\n"
                            f"{emoji_hanzo} **Crypto Chosen** {emoji_hanzo}\n```{row[4]}```"
                        ),
                        color=default_color
                    )

                    embedPayPal.set_image(url=ticket_paypal_ff_link)

                    embed = discord.Embed(
                        title=f"{emoji_money} Earnings Action {emoji_money}",
                        description=(
                            f"Referral: ```{referral_code}```\nStatus: ```Redeem Pending```\nUser Earn: ```{reward}$```"
                        ),
                        color=default_color
                    )

                    embedinvoices = discord.Embed(
                        title=f"{emoji_info} New invoice {emoji_info}",
                        description=(
                            f"A new invoice ID has been created.\n\n"
                            f"{emoji_info} **User ID** {emoji_info}\n```{interaction.user.id}```\n"
                            f"{emoji_info} **invoice ID** {emoji_info}\n```{row[5]}```\n"
                            f"{emoji_info} **Referal Used** {emoji_info}\n```{referral_code}```\n"
                            f"{emoji_info} **Payment Method** {emoji_info}\n```{row[4]}```"
                        ),
                        color=default_color
                    )

                    await self.message.edit(embed=embedinvoices)

                    if self.payment_method == "Crypto":
                        await interaction.message.edit(embed=embedCrypto, view=PayPalNoReferral2(self.selected_product, self.selected_sub, self.payment_total, self.payment_method, self.invoiceID, self.message, self.bot))
                    elif self.payment_method == "PayPal":
                        await interaction.message.edit(embed=embedPayPal, view=PayPalNoReferral2(self.selected_product, self.selected_sub, self.payment_total, self.payment_method, self.invoiceID, self.message, self.bot))
                    await interaction.response.send_message(embed=embed, view=AcceptDeclineReferral2(self.bot, self.info_title.value, reward))
        connRF.close()

class MediaModal(discord.ui.Modal, title="Media Information"):
    info_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Channel",
        required=True,
        placeholder="Send channel type (tiktok/youtube/etc)."
    )
    info_desc = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Name/Link",
        required=True,
        placeholder="Send the channel name or link."
    )

    title_value = None
    desc_value = None
    ticket_mention = None

    def __init__(self, ticket_mention, message, bot, **kwargs):
        super().__init__(**kwargs)
        self.ticket_mention = ticket_mention
        self.message = message
        self.bot = bot

    def get_values(self):
        return self.title_value, self.desc_value

    async def on_submit(self, interaction: discord.Interaction):
        self.title_value = self.info_title.value
        self.desc_value = self.info_desc.value
        embed = discord.Embed(
            title=f"{emoji_youtube} Media Info {emoji_youtube}",
            description=(
                f"Platform: ```{self.title_value}```\nName/Link: ```{self.desc_value}```"
            ),
            color=default_color
        )
        await self.message.edit(embed=embed)
        embed = discord.Embed(
            title=f"{emoji_hanzo} Hanzo | Ticket {emoji_hanzo}",
            description=(
                "Your ticket has been successfully created!\n\n"
                f"**See here:** {self.ticket_mention}"
            ),
            color=default_color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class KeyResetModal(discord.ui.Modal, title="Key Reset"):
    info_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Key",
        required=True,
        placeholder="Send us your key to be reset"
    )
    info_desc = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Reason",
        required=True,
        placeholder="Tell us the reason for the key reset"
    )

    def __init__(self, ticket_mention, message, bot, **kwargs):
        super().__init__(**kwargs)
        self.ticket_mention = ticket_mention
        self.message = message
        self.bot = bot

    def get_values(self):
        return self.title_value, self.desc_value

    async def on_submit(self, interaction: discord.Interaction):
        self.title_value = self.info_title.value
        self.desc_value = self.info_desc.value
        embed = discord.Embed(
            title=f"{emoji_key} Key Reset {emoji_key}",
            description=(
                f"Key: ```{self.title_value}```\nReason: ```{self.desc_value}```"
            ),
            color=default_color
        )
        await self.message.edit(embed=embed)
        embed = discord.Embed(
            title=f"{emoji_hanzo} Hanzo | Ticket {emoji_hanzo}",
            description=(
                "Your ticket has been successfully created!\n\n"
                f"**See here:** {self.ticket_mention}"
            ),
            color=default_color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SupportModal(discord.ui.Modal, title="Support Information"):
    info_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Product",
        required=True,
        placeholder="Product where you have the problem."
    )
    info_desc = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Issue",
        required=True,
        placeholder="Explain SHORTLY the issue."
    )

    title_value = None
    desc_value = None
    ticket_mention = None

    def __init__(self, ticket_mention, message, bot, **kwargs):
        super().__init__(**kwargs)
        self.ticket_mention = ticket_mention
        self.message = message
        self.bot = bot

    def get_values(self):
        return self.title_value, self.desc_value

    async def on_submit(self, interaction: discord.Interaction):
        self.title_value = self.info_title.value
        self.desc_value = self.info_desc.value
        embed = discord.Embed(
            title=f"{emoji_support} Issue Info {emoji_support}",
            description=(
                f"Product: ```{self.title_value}```\nIssue: ```{self.desc_value}```"
            ),
            color=default_color
        )
        await self.message.edit(embed=embed)

        embed = discord.Embed(
            title=f"{emoji_hanzo} Hanzo | Ticket {emoji_hanzo}",
            description=(
                "Your ticket has been successfully created!\n\n"
                f"**See here:** {self.ticket_mention}"
            ),
            color=default_color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)