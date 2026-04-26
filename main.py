import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "¡Bot Ticket Chile está activo 24/7! 🎫"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Conectado como {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Se han sincronizado {len(synced)} comandos.")
    except Exception as e:
        print(e)

@bot.tree.command(name="setup_tickets", description="Configura el sistema de tickets")
async def setup_tickets(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Soporte de Chile RP",
        description="Haz clic en el botón de abajo para abrir un ticket de asistencia.",
        color=discord.Color.blue()
    )
    view = discord.ui.View()
    button = discord.ui.Button(label="Abrir Ticket", style=discord.ButtonStyle.primary, custom_id="ticket_btn")
    view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view)

keep_alive()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)