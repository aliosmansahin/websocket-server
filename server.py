import websockets
import asyncio
import os
import http
import signal
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

def health_check(connection, request):
    if(request.path == "/healthz"):
        return connection.respond(http.HTTPStatus.OK, "OK\n")

async def main():
    try:
        loop = asyncio.get_event_loop()
        stop = loop.create_future()
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

        async with websockets.serve(echo, "", PORT, process_request=health_check):
            print(f"Python WebSocket Sunucusu {ip}:{PORT} adresinde çalışıyor...")
            await stop
    except websockets.exceptions.WebSocketException:
        print(f"websocket hatası")


print(f"Python WebSocket Sunucusu {ip}:{PORT} adresinde başlatılıyor...")
asyncio.run(main())
