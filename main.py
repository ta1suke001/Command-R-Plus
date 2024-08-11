import asyncio
import os
from src.bot.bot import ChatBot
from src.utils.config import load_config
from src.utils.logger import setup_logger

logger = setup_logger()

async def main():
    config = load_config()
    bot = ChatBot(config)
    
    try:
        await bot.start(config['DISCORD_TOKEN'])
    except Exception as e:
        logger.critical(f"Bot起動中に致命的なエラーが発生しました: {e}")
    finally:
        logger.info("Bot has been shut down.")

if __name__ == "__main__":
    os.makedirs("audio", exist_ok=True)
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"メインループでエラーが発生しました: {e}")