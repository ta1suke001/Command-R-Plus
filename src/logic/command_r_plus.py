import cohere
from src.utils.logger import setup_logger

logger = setup_logger()

class CommandRPlus:
    def __init__(self, api_key, system_prompt):
        self.client = cohere.AsyncClient(api_key)
        self.conversations = {}
        self.system_prompt = system_prompt

    async def chat(self, message, conversation_id):
        chat_history = self.conversations.get(conversation_id, [])
        
        try:
            response = await self.client.chat(
                chat_history=[{"role": "SYSTEM", "message": self.system_prompt}] + chat_history,
                message=message,
            )
            
            if response:
                ai_message = response.text
                chat_history.append({"role": "USER", "message": message})
                chat_history.append({"role": "CHATBOT", "message": ai_message})
                self.conversations[conversation_id] = chat_history
                logger.info(f"User: {conversation_id} received a response")
                return ai_message
            else:
                return "応答の生成中にエラーが発生しました。"
        except Exception as e:
            logger.error(f"Cohere APIとの通信中にエラーが発生しました: {e}")
            return "エラーが発生しました。もう一度お試しください。"

    def reset_conversation(self, conversation_id):
        self.conversations.pop(conversation_id, None)
        logger.info(f"Conversation reset for user: {conversation_id}")

    def update_system_prompt(self, new_prompt):
        self.system_prompt = new_prompt
        logger.info("System prompt updated")

    def reset_all_conversations(self):
        self.conversations.clear()
        logger.info("All conversations have been reset")