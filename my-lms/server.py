import asyncio
import os
from aiohttp import web
import jinja2
import aiohttp_jinja2
import base64

# Rustici Engine API configuration
ENGINE_TENANT = os.environ.get('ENGINE_TENANT', 'default')
ENGINE_BASE_URL = os.environ.get('ENGINE_BASE_URL', 'http://localhost:8080/RusticiEngine/api/v2')
ENGINE_USERNAME = os.environ.get('ENGINE_USERNAME', 'your_username')
ENGINE_PASSWORD = os.environ.get('ENGINE_PASSWORD', 'your_password')

async def get_auth_token():
    credentials = base64.b64encode(f"{ENGINE_USERNAME}:{ENGINE_PASSWORD}".encode()).decode()
    return f"Basic {credentials}"

async def get_token(request):
    return web.json_response({'token': await get_auth_token()})

async def handle(request):
    context = {
        'ENGINE_TENANT': ENGINE_TENANT,
        'ENGINE_BASE_URL': ENGINE_BASE_URL
    }
    response = aiohttp_jinja2.render_template("index.html", request, context)
    return response

async def main():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./templates"))
    app.add_routes([
        web.get("/", handle),
        web.get("/token", get_token)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print(f"Serving on http://localhost:8080")
    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
