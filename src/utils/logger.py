import logging
from colorama import Fore, Style, init

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    format_str = "%(asctime)s - %(color)s%(levelname)s%(reset)s - %(message)s"
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        log_msg = self.format_str % {
            'asctime': self.formatTime(record, "%d:%H:%M:%S"),
            'levelname': f"{{ {record.levelname:5s} }}",
            'message': record.getMessage(),
            'color': log_color,
            'reset': Style.RESET_ALL,
        }
        return log_msg

def setup_logger():
    logger = logging.getLogger('discord_bot')
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)

    formatter = ColoredFormatter()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('bot.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger