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
import uuid
from cogs.Buttons.Buttons import *
from cogs.Modals.modals import *

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


class PayPalTutorialButton(discord.ui.View):
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
            title=f"{emoji_money} Paid {emoji_money}",
            description=(
                f"Thank you for enhancing the purchasing process. \n\n{emoji_hanzo} **Please, provide the transaction screenshot.** {emoji_hanzo}\n\n{emoji_hanzo} ** ATTENTION ** {emoji_hanzo}\n```Ensure that the screenshot clearly indicates that you have made the payment using the \"Friends and Family\" option.```"
            ),
            color=default_color
        )
        embed.set_image(url=ticket_paypal_transaction_link)
        await interaction.response.send_message(embed=embed, view=PaidOrNotPaid2(self.selected_product, self.selected_sub, self.payment_total, self.payment_method, self.invoiceID, interaction.user.id, self.bot))

    @discord.ui.button(label="Referal 💸", style = discord.ButtonStyle.red, custom_id="referal")  
    async def Referal(self, interaction: discord.Interaction, button: discord.ui.Button):
            referal_gui = ReferalModal(self.selected_product, self.selected_sub, self.payment_total, self.payment_method, self.invoiceMessage, self.invoiceID, self.bot)
            await interaction.response.send_modal(referal_gui)

class CryptoPaidTutorial(discord.ui.View):
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
            title=f"{emoji_money} Paid {emoji_money}",
            description=(
                f"Thank you for enhancing the purchasing process. \n\n{emoji_hanzo} **Please, provide the transaction screenshot.** {emoji_hanzo}"
            ),
            color=default_color
        )
        await interaction.response.send_message(embed=embed, view=PaidOrNotPaid2(self.selected_product, self.selected_sub, self.payment_total, self.payment_method, self.invoiceID, interaction.user.id, self.bot))

    @discord.ui.button(label="Referal 💸", style = discord.ButtonStyle.red, custom_id="referal")  
    async def Referal(self, interaction: discord.Interaction, button: discord.ui.Button):
            referal_gui = ReferalModal(self.selected_product, self.selected_sub, self.payment_total, self.payment_method, self.invoiceMessage, self.invoiceID, self.bot)
            await interaction.response.send_modal(referal_gui)

class LtcOrBtc(discord.ui.View):
    def __init__(self, selected_product, selected_sub, payment_total, payment_method, invoiceID, invoce_id_message, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.selected_product = selected_product
        self.payment_total = payment_total
        self.selected_sub = selected_sub
        self.payment_method = payment_method
        self.invoiceID = invoiceID
        self.invoceID_message = invoce_id_message

    @discord.ui.select(
        custom_id="Payment Method",
        placeholder="Chose the payment method",
        options=[
            discord.SelectOption(
                label="Litecoin",
                emoji=emoji_crypto,
                value="Litecoin"
            ),
            discord.SelectOption(
                label="Bitcoin",
                emoji=emoji_crypto,
                value="Bitcoin"
            ),
            discord.SelectOption(
                label="Ethereum",
                emoji=emoji_crypto,
                value="Ethereum"
            )
        ]
    )

    async def callback(self, interaction, select):
        PaymentMethod = interaction.data['values'][0]

        embed = discord.Embed(
            title=f"{emoji_money2} Purchase {emoji_money2}",
            description=(
                f"Thank you for answering at the questions. Wait for a staffer. \n\n{emoji_hanzo} **Product Choosen** {emoji_hanzo}\n```{self.selected_product}```\n{emoji_hanzo} **Subscription Duration** {emoji_hanzo}\n```{self.selected_sub}```\n{emoji_hanzo} **Payment Method** {emoji_hanzo}\n```{self.payment_method}```\n{emoji_hanzo} **Crypto Chosen** {emoji_hanzo}\n```{PaymentMethod}```"
            ),
            color=default_color
        )

        embedCryptoBitcoin = discord.Embed(
            title=f"{emoji_crypto} Crypto {emoji_crypto}",
            description=(
                f"Attention! To pay with Crypto, use only this address unless instructed otherwise by the owner.\n\n{emoji_hanzo} **Crypto Address** {emoji_hanzo}\n```{bitcoin_address}```\n{emoji_money} **Total Payment** {emoji_money}\n```${self.payment_total}```\n{emoji_hanzo} **invoice ID** {emoji_hanzo}\n```{self.invoiceID}```"
            ),
            color=default_color
        )

        embedCryptoLitecoin = discord.Embed(
            title=f"{emoji_crypto} Crypto {emoji_crypto}",
            description=(
                f"Attention! To pay with Crypto, use only this address unless instructed otherwise by the owner.\n\n{emoji_hanzo} **Litecoin Address** {emoji_hanzo}\n```{litecoin_address}```\n{emoji_money} **Total Payment** {emoji_money}\n```${self.payment_total}```\n{emoji_hanzo} **invoice ID** {emoji_hanzo}\n```{self.invoiceID}```"
            ),
            color=default_color
        )

        embedinvoices = discord.Embed(
            title=f"{emoji_info} New invoice {emoji_info}",
            description=(
                f"A new fresh invoice ID has been generated.\n\n{emoji_info} **User ID** {emoji_info}\n```{interaction.user.id}```\n{emoji_info} **invoice ID** {emoji_info}\n```{self.invoiceID}```\n{emoji_info} **Referal Used** {emoji_info}\n```NONE```\n{emoji_info} **Payment Method** {emoji_info}\n```{self.payment_method}```\n{emoji_info} **Crypto Chosen** {emoji_info}\n```{PaymentMethod}```"
            ),
            color=default_color
        )

        embedCryptoEthereum = discord.Embed(
            title=f"{emoji_crypto} Crypto {emoji_crypto}",
            description=(
                f"Attention! To pay with Crypto, use only this address unless instructed otherwise by the owner.\n\n{emoji_hanzo} **Ethereum Address** {emoji_hanzo}\n```{Ethereum_address}```\n{emoji_hanzo} **Total Payment** {emoji_hanzo}\n```${self.payment_total}```\n{emoji_hanzo} **invoice ID** {emoji_hanzo}\n```{self.invoiceID}```"
            ),
            color=default_color
        )

        await self.invoceID_message.edit(embed=embedinvoices)
        await interaction.message.edit(embed=embed, view=None)
        
        if PaymentMethod == "Litecoin":
            await interaction.response.send_message(embed=embedCryptoLitecoin, view=CryptoPaidTutorial(self.selected_product, self.selected_sub, self.payment_total, PaymentMethod, self.invoiceID, self.invoceID_message, self.bot))
        elif PaymentMethod == "Bitcoin":
            await interaction.response.send_message(embed=embedCryptoBitcoin, view=CryptoPaidTutorial(self.selected_product, self.selected_sub, self.payment_total, PaymentMethod, self.invoiceID, self.invoceID_message, self.bot))
        elif PaymentMethod == "Ethereum":
            await interaction.response.send_message(embed=embedCryptoEthereum, view=CryptoPaidTutorial(self.selected_product, self.selected_sub, self.payment_total, PaymentMethod, self.invoiceID, self.invoceID_message, self.bot))



class PaymentMethodSelectable(discord.ui.View):
    def __init__(self, bot, selected_product, selected_sub, payment_total):
        self.bot = bot
        super().__init__(timeout=None)
        self.selected_product = selected_product
        self.selected_sub = selected_sub
        self.payment_total = payment_total

    @discord.ui.select(
        custom_id="Payment Method",
        placeholder="Chose the payment method",
        options=[
            discord.SelectOption(
                label="PayPal",
                emoji=emoji_paypal,
                value="PayPal"
            ),
            discord.SelectOption(
                label="Crypto",
                emoji=emoji_crypto,
                value="Crypto"
            ),
            discord.SelectOption(
                label="Credit/Debit Card",
                emoji=emoji_card,
                value="Card"
            ),
            discord.SelectOption(
                label="CashApp",
                emoji=emoji_cashapp,
                value="CashApp"
            ),
            discord.SelectOption(
                label="Venmo",
                emoji=emoji_venmo,
                value="Venmo"
            ),
            discord.SelectOption(
                label="Binance Giftcards",
                emoji=emoji_card,
                value="Binance"
            )
        ]
    )

    async def callback(self, interaction, select):
        PaymentMethod = interaction.data['values'][0]

        channelLogs = interaction.guild.get_channel(ticket_logs)
        channel = self.bot.get_channel(interaction.channel.id)
        topic = interaction.channel.topic
        parts = topic.split(" | ")
        ticket_creator = int(parts[1])


        embed = discord.Embed(
            title=f"{emoji_money2} Purchase {emoji_money2}",
            description=(
                f"Thank you for answering at the questions. Wait for a staffer. \n\n{emoji_hanzo} **Product Choosen** {emoji_hanzo}\n```{self.selected_product}```\n{emoji_hanzo} **Subscription Duration** {emoji_hanzo}\n```{self.selected_sub}```\n{emoji_hanzo} **Payment Method** {emoji_hanzo}\n```{PaymentMethod}```"
            ),
            color=default_color
        )

        invoice_id = str(uuid.uuid4())

        embedPayPal = discord.Embed(
            title=f"{emoji_paypal} PayPal {emoji_paypal}",
            description=(
                f"Pay attention to the fact that unless instructed otherwise by the owner, only this email address should be used for PayPal transactions.\n\n"
                f"{emoji_hanzo} **PayPal Email** {emoji_hanzo}\n```{paypal_email}```\n"
                f"{emoji_hanzo} **Total Payment ** {emoji_hanzo}\n```${self.payment_total}```\n"
                f"{emoji_hanzo} **Invoice ID** {emoji_hanzo}\n```{invoice_id}```\n"
                f"{emoji_hanzo} **Best Practice** {emoji_hanzo}\n```- Send money as Family & Friendly \n- Set the invoice ID as payment description```"
            ),
            color=default_color
        )

        embedinvoices = discord.Embed(
            title=f"{emoji_info} New invoice {emoji_info}",
            description=(
                f"A new fresh invoice ID has been generated.\n\n{emoji_info} **User ID** {emoji_info}\n```{interaction.user.id}```\n{emoji_info} **invoice ID** {emoji_info}\n```{invoice_id}```\n{emoji_info} **Referal Used** {emoji_info}\n```NONE```\n{emoji_info} **Payment Method** {emoji_info}\n```{PaymentMethod}```"
            ),
            color=default_color
        )

        embedForCrypto = discord.Embed(
            title=f"{emoji_money2} Purchase {emoji_money2}",
            description=(
                f"Please, choose the Crypto to pay with. \n\n{emoji_hanzo} **Product Choosen** {emoji_hanzo}\n```{self.selected_product}```\n{emoji_hanzo} **Subscription Duration** {emoji_hanzo}\n```{self.selected_sub}```\n{emoji_hanzo} **Payment Method** {emoji_hanzo}\n```{PaymentMethod}```\n{emoji_hanzo} Payment Method {emoji_hanzo}\nClick below to choose the Crypto you prefer\n\n"
            ),
            color=default_color
        )

        embedExchanger = discord.Embed(
            title=f"{emoji_info} Exchanger {emoji_info}",
            description=(
                f"To continue with your payment, **you need** an *exchanger*. __Wait for one.__\n\n{emoji_hanzo} **Payment Method:** {emoji_hanzo}\n```{PaymentMethod}```\n{emoji_hanzo} **Payment Total:** {emoji_hanzo}\n```${self.payment_total}```"
            ),
            color=default_color
        )

        message = await channelLogs.send(embed=embedinvoices)

        conn = sqlite3.connect("interactions.db")
        cursor = conn.cursor()

        embedPayPal.set_image(url=ticket_paypal_ff_link)
        if PaymentMethod == "PayPal":        
            await interaction.message.edit(embed=embed, view=None)   
            await interaction.response.send_message(embed=embedPayPal, view=PayPalTutorialButton(self.selected_product, self.selected_sub, self.payment_total, PaymentMethod, invoice_id, message, self.bot))
        elif PaymentMethod == "Crypto":
            await interaction.message.edit(embed=embedForCrypto, view=LtcOrBtc(self.selected_product, self.selected_sub, self.payment_total, PaymentMethod, invoice_id, message, self.bot))
            await interaction.response.defer()
        elif PaymentMethod == "Card":
            await interaction.message.edit(embed=embed, view=None)
            product_link = ""

            if self.selected_product == "Private Fortnite Cheats":
                product_link = hanzo_fn_link
            elif self.selected_product == "Permanent HWID Spoofer":
                product_link = permanent_spoofer_link
                

            embedCreditCart = discord.Embed(
                title=f"{emoji_card} Credit/Debit Card {emoji_card}",
                description=(
                    f"\nAttention! To pay with Credit/Debit Cards, you must pay through the website.\n\n{emoji_hanzo} **Product** {emoji_hanzo}\n```{self.selected_product}```\n{emoji_hanzo} **Total Payment** {emoji_hanzo}\n```${self.payment_total}```\n{emoji_hanzo} **Direct Link:** {emoji_hanzo}\n{product_link}\n"
                ),
                color=default_color
            )      
            await interaction.response.send_message(embed=embedCreditCart, view=CryptoPaidTutorial(self.selected_product, self.selected_sub, self.payment_total, PaymentMethod, invoice_id, message, self.bot))
        else:     
            role_permission = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                embed_links=True,
            )

            existing_overwrites = channel.overwrites
            existing_overwrites[interaction.guild.get_role(exchanger_role_id)] = role_permission
            await channel.edit(overwrites=existing_overwrites)
            await interaction.message.edit(embed=embed, view=None)  
            await interaction.response.send_message(embed=embedExchanger)
            
        cursor.execute('''
            INSERT INTO invoices (
                selected_product, selected_sub, payment_total, payment_method, invoice_id, paid, channel_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.selected_product, self.selected_sub, self.payment_total, PaymentMethod, invoice_id, False, interaction.channel.id))
        conn.commit()
        conn.close()