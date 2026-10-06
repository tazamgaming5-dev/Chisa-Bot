import os
import discord
from google import genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN belum ditemukan.")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY belum ditemukan.")

# Gemini
client_ai = genai.Client(api_key=GEMINI_API_KEY)

# 1 memory untuk setiap server
chat_sessions = {}

# Discord
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f"Bot login sebagai {bot.user}")
    print("Chisa siap digunakan!")


@bot.event
async def on_message(message):

    # Abaikan pesan dari bot
    if message.author.bot:
        return

    # Bot hanya merespons kalau di-mention
    if bot.user not in message.mentions:
        return

    # Ambil isi pesan tanpa mention bot
    prompt = message.content.replace(
        f"<@{bot.user.id}>", ""
    ).strip()

    if not prompt:
        await message.channel.send(
            "Iya? Ada yang mau kamu tanyakan? 😭"
        )
        return

    # =========================
    # MEMORY PER SERVER
    # =========================

    if message.guild:
        memory_id = message.guild.id
    else:
        # Kalau DM, gunakan channel sebagai memory
        memory_id = message.channel.id

    try:

        # Buat memory baru kalau server belum punya
        if memory_id not in chat_sessions:

            chat_sessions[memory_id] = client_ai.chats.create(
                model="gemini-3.1-flash-lite"
            )

            print(
                f"Memory baru dibuat: {memory_id}"
            )

        # Ambil memory server
        chat = chat_sessions[memory_id]

        # Tampilkan status typing
        async with message.channel.typing():

            response = chat.send_message(
                message=prompt
            )

            answer = getattr(response, "text", None)

            if not answer:
                answer = "Gemini tidak memberikan jawaban."

            # Discord maksimal 2000 karakter per pesan
            if len(answer) <= 2000:

                await message.channel.send(answer)

            else:

                for i in range(0, len(answer), 2000):
                    await message.channel.send(
                        answer[i:i + 2000]
                    )

    except Exception as e:

        print("ERROR:", repr(e))

        await message.channel.send(
            "Maaf, aku lagi mengalami error 😭"
        )


bot.run(DISCORD_TOKEN)