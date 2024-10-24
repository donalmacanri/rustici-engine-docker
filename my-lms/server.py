import asyncio
import os
from aiohttp import web
import jinja2
import aiohttp_jinja2
import base64
from datetime import datetime, timedelta
import aiohttp

# Rustici Engine API configuration
ENGINE_TENANT = os.environ.get('ENGINE_TENANT', 'default')
ENGINE_BASE_URL = os.environ.get('ENGINE_BASE_URL', 'http://localhost:8080/RusticiEngine/api/v2')
ENGINE_USERNAME = os.environ.get('ENGINE_USERNAME', 'your_username')
ENGINE_PASSWORD = os.environ.get('ENGINE_PASSWORD', 'your_password')

async def get_system_token():
    credentials = base64.b64encode(f"{ENGINE_USERNAME}:{ENGINE_PASSWORD}".encode()).decode()
    return f"Basic {credentials}"

async def create_token():
    url = f"{ENGINE_BASE_URL}/appManagement/token"
    headers = {
        "Authorization": await get_system_token(),
        "Content-Type": "application/json"
    }
    data = {
        "id":f"token_{int(datetime.utcnow().timestamp())}",
        "permissions": {
            "scopes": ["read", "write"],
            "tenantName": ENGINE_TENANT
        },
        "expiry": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result['result']
            else:
                print(response)
                raise Exception(f"Failed to create token: {response.status}")

async def get_token(request):
    try:
        token = await create_token()
        return web.json_response({'token': f"Bearer {token}"})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def handle_webhook(request):
    payload = await request.json()
    print("Webhook payload received:", payload)
    return web.Response(status=200)

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
        web.get("/token", get_token),
        web.post("/webhook", handle_webhook)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print(f"Serving on http://localhost:8080")
    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
