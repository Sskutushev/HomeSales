import google.generativeai as genai
from src.config import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    async def generate_post_content(self, listing_data: dict) -> str:
        prompt = f"""
Напиши короткий, интригующий и продающий пост для Telegram-канала о продаже квартиры.
Объем - не более 500 символов.

Основа для поста - данные о квартире:
- ЖК: {listing_data.get("complex_name", "")}
- Район: {listing_data.get("district", "")}
- Комнат: {listing_data.get("rooms", "")}
- Площадь: {listing_data.get("area", "")} м²
- Цена: {listing_data.get("price", "")} ₽
- Описание от застройщика: {listing_data.get("description", "")}

Твоя задача:
1. Использовать маркетинговые, привлекающие внимание слова.
2. Сделать акцент на любых скидках, акциях или спецпредложениях, если они упоминаются в описании.
3. Текст должен быть живым и интригующим.
4. Обязательно используй эмодзи, чтобы сделать пост визуально привлекательным.
5. В конце добавь призыв к действию, например "Узнайте больше!" или "Забронируйте просмотр!".
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating content with Gemini API: {e}")
            return ""