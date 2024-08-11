import discord
from discord.ext import commands
import json
#import os
from src.logic.command_r_plus import CommandRPlus
from src.utils.logger import setup_logger
from src.utils.config import load_config, save_config

logger = setup_logger()

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = load_config()
        self.command_r_plus = CommandRPlus(
            config['CMD_R_API_KEY'],
            config['SYSTEM_PROMPT']
        )
        self.reading_corrections = self.load_reading_corrections()

    @discord.app_commands.command(name="chat", description="Command-R-Plusと対話します")
    async def chat(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(ephemeral=True)
        
        conversation_id = str(interaction.user.id)
        response = await self.command_r_plus.chat(message, conversation_id)
        
        logger.info(f"User: {interaction.user.name} sent a message")
        await interaction.followup.send(response, ephemeral=True)

        if interaction.guild and interaction.guild.voice_client:
            voice_cog = self.bot.get_cog('VoiceCog')
            if voice_cog:
                corrected_response = self.apply_reading_corrections(response)
                await voice_cog.text_to_speech(interaction, corrected_response)

    @discord.app_commands.command(name="reset", description="会話履歴をリセットします")
    async def reset(self, interaction: discord.Interaction):
        conversation_id = str(interaction.user.id)
        self.command_r_plus.reset_conversation(conversation_id)
        await interaction.response.send_message("会話履歴をリセットしました。", ephemeral=True)

    @discord.app_commands.command(name="update_system_prompt", description="システムプロンプトを更新します")
    async def update_system_prompt(self, interaction: discord.Interaction, prompt: str):
        self.command_r_plus.update_system_prompt(prompt)
        config = load_config()
        config['SYSTEM_PROMPT'] = prompt
        save_config(config)
        self.command_r_plus.reset_all_conversations()
        await interaction.response.send_message("システムプロンプトを更新し、全ての会話履歴をリセットしました。", ephemeral=True)

    @discord.app_commands.command(name="update_system_prompt_file", description="ファイルからシステムプロンプトを更新します")
    async def update_system_prompt_file(self, interaction: discord.Interaction, file: discord.Attachment):
        if not file.filename.endswith('.txt'):
            await interaction.response.send_message("添付ファイルはテキストファイル(.txt)である必要があります。", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        try:
            content = await file.read()
            new_prompt = content.decode('utf-8')
            self.command_r_plus.update_system_prompt(new_prompt)
            config = load_config()
            config['SYSTEM_PROMPT'] = new_prompt
            save_config(config)
            self.command_r_plus.reset_all_conversations()
            await interaction.followup.send("システムプロンプトを更新し、全ての会話履歴をリセットしました。", ephemeral=True)
        except Exception as e:
            logger.error(f"Error updating system prompt from file: {e}")
            await interaction.followup.send("システムプロンプトの更新中にエラーが発生しました。", ephemeral=True)

    @discord.app_commands.command(name="add_reading_correction", description="読み上げの修正を追加します")
    async def add_reading_correction(self, interaction: discord.Interaction, original: str, correction: str):
        self.reading_corrections[original] = correction
        self.save_reading_corrections()
        await interaction.response.send_message(f"読み上げの修正を追加しました: {original} -> {correction}", ephemeral=True)

    def load_reading_corrections(self):
        try:
            with open('data/reading_corrections.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_reading_corrections(self):
        with open('data/reading_corrections.json', 'w', encoding='utf-8') as f:
            json.dump(self.reading_corrections, f, ensure_ascii=False, indent=2)

    def apply_reading_corrections(self, text):
        for original, correction in self.reading_corrections.items():
            text = text.replace(original, correction)
        return text

async def setup(bot):
    await bot.add_cog(ChatCog(bot))