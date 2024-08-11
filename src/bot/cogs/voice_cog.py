import discord
from discord.ext import commands
from src.logic.elevenlabs import ElevenLabsService
from src.utils.logger import setup_logger

logger = setup_logger()

class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.elevenlabs = ElevenLabsService(bot.config['ELEVENLABS_API_KEY'])

    @discord.app_commands.command(name="join", description="ボイスチャンネルに参加します")
    async def join(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
            return

        if not interaction.user.voice:
            await interaction.response.send_message("あなたはボイスチャンネルに接続していません。", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        if interaction.guild.voice_client:
            if interaction.guild.voice_client.channel == voice_channel:
                await interaction.response.send_message("既にそのボイスチャンネルに参加しています。", ephemeral=True)
            else:
                await interaction.guild.voice_client.move_to(voice_channel)
                await interaction.response.send_message(f"{voice_channel.name}に移動しました。", ephemeral=True)
        else:
            await voice_channel.connect()
            await interaction.response.send_message(f"{voice_channel.name}に参加しました。", ephemeral=True)
        
        logger.info(f"Joined voice channel: {voice_channel.name} in guild: {interaction.guild.name}")

    @discord.app_commands.command(name="leave", description="ボイスチャンネルから退出します")
    async def leave(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
            return

        if not interaction.guild.voice_client:
            await interaction.response.send_message("ボットはボイスチャンネルに接続していません。", ephemeral=True)
            return

        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("ボイスチャンネルから退出しました。", ephemeral=True)
        logger.info(f"Left voice channel in guild: {interaction.guild.name}")

    async def text_to_speech(self, interaction: discord.Interaction, text: str):
        if not interaction.guild or not interaction.guild.voice_client:
            logger.info("ボットはボイスチャンネルに接続していないため、読み上げをスキップします。")
            return

        try:
            audio_file = await self.elevenlabs.generate_speech(text)
            if not audio_file:
                logger.error("音声ファイルの生成に失敗しました。")
                return

            source = discord.FFmpegPCMAudio(audio_file)
            interaction.guild.voice_client.play(source, after=lambda e: self.cleanup_audio_file(audio_file, e))
        except Exception as e:
            logger.error(f"音声の再生中にエラーが発生しました: {e}")
            self.elevenlabs.cleanup_audio_file(audio_file)

    def cleanup_audio_file(self, file_path, error):
        if error:
            logger.error(f"再生エラー: {error}")
        self.elevenlabs.cleanup_audio_file(file_path)

async def setup(bot):
    await bot.add_cog(VoiceCog(bot))