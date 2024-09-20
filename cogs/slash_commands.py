import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import os
from dotenv import load_dotenv
import requests
import json

import completion
import rag
import io
from PyPDF2 import PdfReader
import openai
import subprocess
import re

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a chave da API da OpenAI do arquivo .env
openai.api_key = os.getenv('OPENAI_API_KEY')


try:
    ANNOUNCE_CHANNEL_ID = int(os.getenv('ANNOUNCE_CHANNEL_ID'))
    BACKGROUNDS_CHANNEL_ID = int(os.getenv('BACKGROUNDS_CHANNEL_ID'))
    BUILDS_CHANNEL_ID = int(os.getenv('BUILDS_CHANNEL_ID'))
    MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
    
except TypeError:
    raise ValueError("One or more environment variables are missing or not set correctly.")

class ConfirmButton(View):
    def __init__(self, user, embed, target_channel, moderation_channel, bot, title_type, files):
        super().__init__(timeout=60) 
        self.user = user
        self.embed = embed
        self.target_channel = target_channel
        self.moderation_channel = moderation_channel
        self.bot = bot
        self.title_type = title_type
        self.files = files

    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode confirmar isso.", ephemeral=True)
            return

        await interaction.response.send_message("A sua publicação foi confirmada e publicada!", ephemeral=True)
        await self.target_channel.send(embed=self.embed)
        
        if self.files:
            await self.target_channel.send(files=[await file.to_file() for file in self.files])

        await self.moderation_channel.send(f"{self.user.display_name} ({self.user.id}) postou um {self.title_type}.")
        
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode cancelar essa mensagem.", ephemeral=True)
            return
        
        await interaction.response.send_message("Sua publicação foi cancelada.", ephemeral=True)
        self.stop()

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.announce, guild=discord.Object(id=MAIN_GUILD_ID))
        self.bot.tree.add_command(self.trajetoai, guild=discord.Object(id=MAIN_GUILD_ID))
        #self.bot.tree.add_command(self.build, guild=discord.Object(id=MAIN_GUILD_ID))

    @app_commands.command(name="anuncio", description="Envia um anúncio RP no #anuncios-roleplay")
    async def announce(self, interaction: discord.Interaction):
        await interaction.response.send_message("Olhe seu privado para continuarmos o anuncio.", ephemeral=True)
        await self.send_dm(interaction.user, ANNOUNCE_CHANNEL_ID, "anúncio", "o anúncio", "anúncio", "seu anúncio")

    @app_commands.command(name="trajetoai", description="Utilizando RAG & Chat Completion!")
    async def trajetoai(self, interaction: discord.Interaction):
        await interaction.response.send_message("Olhe seu privado para continuarmos com RAG & Chat Completion...", ephemeral=True)
        await self.send_dm(interaction.user, BACKGROUNDS_CHANNEL_ID, "trajetoai", "a história do seu personagem", "personagem", "seu background")

    async def send_dm(self, user: discord.User, channel_id: int, title_type: str, description_prompt: str, title_prompt: str, success_message: str):
        def check(m):
            return m.author == user and isinstance(m.channel, discord.DMChannel)
        
        try:
            restart = True
            while restart == True:
                dm_channel = await user.create_dm()

                await dm_channel.send(f"GenAI: O que gostaria de Otimizar do Trajeto? Exemplos:\n\nPreveja o tempo de entrega com base em parâmetros específicos - local de partida (ex: CD1),  destino da entrega (ex: Local A), a distância e condições de tráfego (Baixo, Médio ou Alto).\nOu então:\nEncontre as 3 melhores rotas partindo de um local específico - Local de Partida - CD2, e Destino de Entrega - Local C.")
                question = await self.bot.wait_for('message', check=check)
                question = question.content

                resposta_ai = completion.start_Completion(question)
                resposta_ai = re.sub(r'```json|```', '', resposta_ai).strip()
                resposta_ai = json.loads(resposta_ai)
                
                await dm_channel.send(f"GenAI: {resposta_ai}")
                
                arquivo = resposta_ai.get("arquivo")
                parametros = resposta_ai.get("parametros", {})
                
                if arquivo == "prever_tempo_especifico.py":
                    # Preparar parâmetros para o script
                    local_partida = parametros.get("local_partida")
                    destino_entrega = parametros.get("destino_entrega")
                    distancia = parametros.get("distancia")
                    condicoes_transito = parametros.get("condicoes_transito")

                    import prever_tempo_especifico
                    
                    result = prever_tempo_especifico.prever_tempo_estimado(local_partida=local_partida, destino_entrega=destino_entrega, distancia=distancia, condicoes_trafego=condicoes_transito)

                elif arquivo == "encontrar_menores_tempos.py":
                    import encontrar_menores_tempos
                    
                    local_partida = parametros.get("local_partida")
                    destino_entrega = parametros.get("destino_entrega")
                    result = encontrar_menores_tempos.encontrar_menor_tempo(local_partida=local_partida, destino_entrega=destino_entrega)
                
                await dm_channel.send(f"GenAI: Resposta do Modelo - {result} \n\n\nGenAI: Deseja fazer mais perguntas? Yes / No")
                restart_confirm = await self.bot.wait_for('message', check=check)
                
                if restart_confirm == "No":
                    restart = False
                        
                
        except Exception as e:
            await dm_channel.send(f"Ocorreu um erro: {e}")

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))