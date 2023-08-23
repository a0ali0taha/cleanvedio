import asyncio
from pyrogram import Client

bot_token = '6554914797:AAE1_FqgZh16eNsFZcJ_BgL51-ccwIHEJJQ'
chat_id = -1001938941284

# 29646632
# eae5d7f69ecf16e96c6bd9f14aaa4f97
async def main():
    async with Client("my_account", api_id=29646632, api_hash='eae5d7f69ecf16e96c6bd9f14aaa4f97',bot_token=bot_token) as app:
        await app.send_video(chat_id=chat_id,video='final/الحرب العالمية الأولى باختصار.mp4',caption='caption')
        # await app.send_message(chat_id=chat_id,text='test')


# asyncio.run(main())