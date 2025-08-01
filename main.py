from bot import Bot

import os, hmac, hashlib, asyncio
from fastapi import FastAPI, Request, Header, HTTPException
from helper_func import add_vip_user
from bot import app as bot_client  # instance Pyrogram Client

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

api = FastAPI()

@api.post("/trakteer-webhook")
async def trakteer_webhook(request: Request, x_trakta_signature: str = Header(None)):
    body = await request.body()
    sig = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, x_trakta_signature or ""):
        raise HTTPException(400, "Invalid signature")
    data = await request.json()
    tid = data.get("data", {}).get("telegram_id")
    if not tid:
        return {"status": "ignored"}
    await add_vip_user(int(tid))
    asyncio.create_task(bot_client.send_message(int(tid),
        "✅ Pembayaran terverifikasi! Kamu sekarang menjadi VIP 🎉"))
    return {"status":"ok"}

if __name__ == "__main__":
    import uvicorn
    bot_client.start()
    uvicorn.run(api, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


Bot().run()
