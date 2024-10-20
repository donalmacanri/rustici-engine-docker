import asyncio
from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = f"Hello, {name}"
    return web.Response(text=text)

async def main():
    app = web.Application()
    app.add_routes([web.get('/', handle),
                    web.get('/{name}', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print(f"Serving on http://localhost:8080")
    await asyncio.Event().wait()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
