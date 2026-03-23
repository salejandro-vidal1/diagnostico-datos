import asyncio
from fastapi import FastAPI, WebSocket
from collections import Counter
import redis.asyncio as redis
from hypercorn.asyncio import serve
from hypercorn.config import Config
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse

r = redis.Redis(host="redis", port=6379, decode_responses=True)

word_counter = Counter()

clients = set()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Word Frequency</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h2>Palabras frecuentes en métodos y funciones de Java o Python en repositorios GitHub</h2>
        <div id="graph"></div>
        <script>
            let ws = new WebSocket("ws://localhost:8000/ws");
            let data = [{ x: [], y: [], type: 'bar' }];
            Plotly.newPlot('graph', data);

            ws.onmessage = function(event) {
                let freq = JSON.parse(event.data);
                data[0].x = Object.keys(freq);
                data[0].y = Object.values(freq);
                Plotly.react('graph', data);
            };
        </script>
    </body>
</html>
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(redis_listener())
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except:
        clients.remove(websocket)

async def redis_listener():
    while True:
        _, word = await r.blpop("word_queue")
        word_counter[word] += 1
        for ws in list(clients):
            try:
                await ws.send_json(word_counter)
            except:
                clients.remove(ws)

async def main():
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    await serve(app, config)

if __name__ == "__main__":
    asyncio.run(main())
