import discord
from discord.ext import commands
from src.utils.logger import setup_logger

logger = setup_logger()

class ChatBot(commands.Bot):
    def __init__(self, config):
        intents = discord.Intents.all()
        super().__init__(command_prefix='/', intents=intents)
        self.config = config

    async def setup_hook(self):
        await self.load_extension("src.bot.cogs.chat_cog")
        await self.load_extension("src.bot.cogs.voice_cog")
        await self.tree.sync()
        logger.info("Bot is ready!")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f"An error occurred: {error}")
        await ctx.send(f"エラーが発生しました: {error}")

    async def on_error(self, event_method, *args, **kwargs):
        logger.error(f"An error occurred in {event_method}: {args} {kwargs}")

    async def on_application_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        logger.error(f"An application command error occurred: {error}")
        await interaction.response.send_message(f"コマンド実行中にエラーが発生しました: {error}", ephemeral=True)