import websockets
import asyncio
import os
import socket

ip = socket.gethostbyname(socket.gethostname())
PORT = int(os.getenv("PORT", 3000))

async def echo(websocket):
    print(f"Yeni bağlantı kuruldu: {websocket.remote_address}")
    try: 
        while True:
            message = await websocket.recv()
            print(f"Gelen mesaj: {message}")
            
            await websocket.send(f"Sunucudan yanıt: {message}")
    except websockets.exceptions.ConnectionClosed:
        print(f"Bağlantı kapatıldı: {websocket.remote_address}")


async def StartServer():
    server = await websockets.serve(echo, ip, PORT)
    print(f"Python WebSocket Sunucusu {ip}:{PORT} adresinde çalışıyor...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(StartServer())
