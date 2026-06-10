#!/usr/bin/env python3
# ============================================
# CHERRY BOT - RENDER.COM
# Support HTTPS otomatis dari Render
# ============================================

import os
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================
# KONFIGURASI - Ambil dari Environment Variable
# ============================================
PORT = int(os.environ.get('PORT', 10000))
BIND = "0.0.0.0"
DOMAIN = os.environ.get('DOMAIN', 'cherry-bot.onrender.com')
TOKEN = os.environ.get('DISCORD_TOKEN', '')

# ============================================
# API HANDLER (Sama seperti sebelumnya)
# ============================================
class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/api/servers':
            response = [{"id": "1503908762019172553", "name": "cherry", "member_count": 6}]
        elif self.path.startswith('/api/channels/'):
            response = [
                {"id": "1503908762019172601", "name": "general", "type": 0},
                {"id": "1503908762019172602", "name": "random", "type": 0}
            ]
        else:
            response = {"status": "ok", "message": "Cherry Bot on Render"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/api/send':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            print(f"[📨] Message: {post_data}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[API] {format % args}")

def run_api_server():
    server = HTTPServer((BIND, PORT), APIHandler)
    print(f"[✅] API Server running on port {PORT}")
    server.serve_forever()

# ============================================
# DISCORD BOT (Dengan Fix audioop)
# ============================================
def run_discord_bot():
    # Fix untuk menghindari error audioop di Render
    os.environ["DISCORD_INSTANCE_NO_VOICE"] = "true"  # [citation:6]
    
    import discord
    from discord.ext import commands
    import random
    
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"[🤖] Bot online: {bot.user}")
        await bot.change_presence(activity=discord.Game(name="!help | Cherry"))
    
    @bot.command()
    async def ping(ctx):
        await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    
    @bot.command()
    async def info(ctx):
        embed = discord.Embed(title="🍒 Cherry Bot", color=discord.Color.purple())
        embed.add_field(name="API", value=f"https://{DOMAIN}")
        await ctx.send(embed=embed)
    
    @bot.command()
    async def hello(ctx):
        await ctx.send(random.choice(["Halo! 👋", "Haiii! 🌸", "Selamat datang! 🍒"]))
    
    @bot.command()
    async def dice(ctx):
        await ctx.send(f"🎲 {random.randint(1, 6)}")
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"[❌] Bot error: {e}")

# ============================================
# SIMPLE HTTP SERVER UNTUK KEEP ALIVE
# ============================================
from flask import Flask
from threading import Thread

flask_app = Flask('')

@flask_app.route('/')
def home():
    return '<h1>🍒 Cherry Bot is running!</h1>'

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

# ============================================
# MAIN - JALANKAN SEMUA DI THREAD TERPISAH
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("🍒 CHERRY BOT - RENDER.COM")
    print(f"Port: {PORT}")
    print("="*60)
    
    # Jalankan Flask untuk keep alive [citation:7]
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(1)
    
    # Jalankan API Server
    api_thread = Thread(target=run_api_server, daemon=True)
    api_thread.start()
    time.sleep(1)
    
    # Jalankan Discord Bot
    bot_thread = Thread(target=run_discord_bot, daemon=True)
    bot_thread.start()
    
    print("\n✅ SEMUA LAYANAN BERJALAN!")
    print(f"🌐 HTTPS: https://{DOMAIN}")
    print("="*60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
