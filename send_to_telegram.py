import asyncio
from pyrogram import Client

bot_token = '6554914797:AAE1_FqgZh16eNsFZcJ_BgL51-ccwIHEJJQ'
chat_id = '-1001938941284'


async def main():
    async with Client("my_account", chat_id, bot_token) as app:
        await app.send_video('test', 'newv/الحرب العالمية الأولى باختصار.mp4')


asyncio.run(main())