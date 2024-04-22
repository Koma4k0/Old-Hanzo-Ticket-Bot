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
from cogs.Selectables.StaffRating import *

class AcceptDeclineReferral(discord.ui.View):
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
                conn.close()                
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

class PaidOrNotPaid(discord.ui.View):
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

class PayPalNoReferral(discord.ui.View):
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
        await interaction.response.send_message(embed=embed, view=PaidOrNotPaid(self.selected_product, self.selected_sub, self.payment_total, self.payment_method, self.invoiceID, interaction.user.id, self.bot))

class CloseButton(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label=f"Close 🎫", style = discord.ButtonStyle.green, custom_id="close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button,):
        with sqlite3.connect('user.db') as conn:
            cur = conn.cursor()
            guild = self.bot.get_guild(guild_id)
            topic = interaction.channel.topic
            transcript_channel = interaction.guild.get_channel(transcripts_channel)
            parts = topic.split(" | ")
            ticket_creator_id = int(parts[1])
            ticket_creator = guild.get_member(int(parts[1]))
            cur = conn.cursor()
            member_name = interaction.user.name
            ticket_name = member_name

            military_time: bool = True
            transcript = await chat_exporter.export(
                interaction.channel,
                limit=200,
                tz_info=timezone_set,
                military_time=military_time,
                bot=self.bot,
            )       
            if transcript is None:
                return
            
            cur.execute('''
                    SELECT * FROM ticket WHERE channel_id = ?
                ''', (interaction.channel.id,))
            resultsVoc = cur.fetchall()

            if resultsVoc:
                row = resultsVoc[0]
                rowVocal = row[5]

                if rowVocal is not None:
                    vocal_chat = interaction.guild.get_channel(rowVocal)
                    
                    if vocal_chat is not None:
                        await vocal_chat.delete()

            cur.execute("DELETE FROM ticket WHERE discord_id=?", (ticket_creator_id,))
            conn.commit()

            transcript_file = discord.File(
                io.BytesIO(transcript.encode()),
                filename=f"transcript-{interaction.channel.name}.html")
            transcript_file2 = discord.File(
                io.BytesIO(transcript.encode()),
                filename=f"transcript-{interaction.channel.name}.html")
            

            embed = discord.Embed(
                title=f"{emoji_hanzo} Hanzo | Ticket Closed {emoji_hanzo}",
                description=(
                    f"Thank you for using our ticketing system. This ticket is now closed.\n\n"
                    f"**Opened By**: {ticket_creator.mention}\n"
                    f"**Closed By**: {interaction.user.mention}\n\n"
                ),
                color=default_color
            )

            transcript_info = discord.Embed(
                title=f"{emoji_hanzo} Hanzo | Ticket Closed {emoji_hanzo}",
                description=(
                    f"This ticket is now closed, signifying the conclusion of its journey.\n\n"
                    f"***Ticket Opened By***: {ticket_creator.mention}\n"
                    f"***Ticket Name***: {interaction.channel.name}\n"
                    f"***Closed By***: {interaction.user.mention}\n\n"
                    f"Thanks for your communication in this ticket. If you have more questions or need further help, reach out to us again. Appreciate you choosing our support services!"
                ),
                color=default_color 
            )

            await interaction.response.send_message(embed=embed)
            transcript_info_log = discord.Embed(
                title=f"{emoji_hanzo} Hanzo | Ticket Closed {emoji_hanzo}",
                description=(
                    f"This ticket is now closed, signifying the conclusion of its journey.\n\n"
                    f"**Ticket Opened By**: {ticket_creator.mention}\n"
                    f"**Ticket Name**: {interaction.channel.name}\n"
                    f"**Closed By**: {interaction.user.mention}\n\n"
                ),
                color=default_color 
            ) 
            if any(role.id == staff_team_id for role in interaction.user.roles): 
                connStaff = sqlite3.connect('staffstats.db')
                curStaff = connStaff.cursor()

                curStaff.execute("SELECT * FROM staffer WHERE discord_id=?", (interaction.user.id,))
                staffer_row = curStaff.fetchone()

                try:           
                    await ticket_creator.send(embed=transcript_info, file=transcript_file, view=StaffRating(self.bot, interaction.user.id))
                except:
                    transcript_info.add_field(name="Error", value="Can't send transcript to user. Error: DM's privacy.", inline=True)


                if not staffer_row:
                    curStaff.execute("INSERT INTO staffer (discord_id, tickets_managed) VALUES (?, 1)", (interaction.user.id,))
                else:
                    curStaff.execute("UPDATE staffer SET tickets_managed = tickets_managed + 1 WHERE discord_id=?", (interaction.user.id,))
                connStaff.commit()
                connStaff.close()
            else:
                try:           
                    await ticket_creator.send(embed=transcript_info, file=transcript_file)
                except:
                    transcript_info_log.add_field(name="Error", value="Can't send transcript to user. Error: DM's privacy.", inline=True)

            await transcript_channel.send(embed=transcript_info_log, file=transcript_file2)
            await asyncio.sleep(3)
            await interaction.channel.delete(reason="Ticket deleted")

        conn.close()
