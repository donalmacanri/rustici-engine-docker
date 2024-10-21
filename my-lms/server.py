import asyncio
from aiohttp import web
import jinja2
import aiohttp_jinja2


async def handle(request):
    name = request.match_info.get("name", "Anonymous")
    context = {"name": name}
    response = aiohttp_jinja2.render_template("index.html", request, context)
    return response


async def main():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./templates"))
    app.add_routes([web.get("/", handle), web.get("/{name}", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print(f"Serving on http://localhost:8080")
    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
