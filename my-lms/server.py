import asyncio
import base64
import sys
from datetime import datetime, timedelta
import os

import aiohttp
import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import RouteTableDef
import jinja2

# Rustici Engine API configuration
ENGINE_TENANT = os.environ.get("ENGINE_TENANT")
ENGINE_BASE_URL = os.environ.get("ENGINE_BASE_URL")
ENGINE_USERNAME = os.environ.get("ENGINE_USERNAME")
ENGINE_PASSWORD = os.environ.get("ENGINE_PASSWORD")


async def get_system_token():
    credentials = base64.b64encode(
        f"{ENGINE_USERNAME}:{ENGINE_PASSWORD}".encode()
    ).decode()
    return f"Basic {credentials}"


async def create_token():
    url = f"{ENGINE_BASE_URL}/appManagement/token"
    headers = {
        "Authorization": await get_system_token(),
        "Content-Type": "application/json",
    }
    data = {
        "id": f"token_{int(datetime.utcnow().timestamp())}",
        "permissions": {"scopes": ["read", "write"], "tenantName": ENGINE_TENANT},
        "expiry": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result["result"]
            else:
                print(response, flush=True)
                raise Exception(f"Failed to create token: {response.status}")


async def get_subscriptions(session, headers):
    url = f"{ENGINE_BASE_URL}/appManagement/subscriptions"
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            raise Exception(f"Failed to get subscriptions: {response.status}")


async def create_registration_subscription(session, headers):
    # Get the server's public URL from environment variable
    server_url = os.environ.get("MYLMS_SERVER_URL")
    if not server_url:
        raise Exception("MYLMS_SERVER_URL environment variable not set")
    webhook_url = f"{server_url}/webhook"

    subscription_data = {
        "topic": "RegistrationChanged",
        "url": webhook_url,
        "enabled": True,
        "bodyFormat": "Course",
    }

    url = f"{ENGINE_BASE_URL}/appManagement/subscriptions"
    async with session.post(url, headers=headers, json=subscription_data) as response:
        if response.status == 200:
            result = await response.json()
            print(f"Created subscription: {result['result']}", flush=True)
        else:
            raise Exception(f"Failed to create subscription: {response.status}")


async def setup_subscription():
    headers = {
        "Authorization": await get_system_token(),
        "Content-Type": "application/json",
        "engineTenantName": "default",
    }

    async with aiohttp.ClientSession() as session:
        # Check existing subscriptions
        subscriptions = await get_subscriptions(session, headers)

        # Check if we already have a RegistrationChanged subscription
        has_subscription = any(
            sub["definition"]["topic"] == "RegistrationChanged"
            for sub in subscriptions.get("subscriptions", [])
        )

        if not has_subscription:
            await create_registration_subscription(session, headers)


routes = RouteTableDef()


@routes.get("/")
async def index(request):
    context = {"ENGINE_TENANT": ENGINE_TENANT, "ENGINE_BASE_URL": ENGINE_BASE_URL}
    response = aiohttp_jinja2.render_template("index.html", request, context)
    return response


@routes.get("/token")
async def token(request):
    try:
        token = await create_token()
        return web.json_response({"token": f"Bearer {token}"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post("/webhook")
async def webhook(request):
    payload = await request.json()
    print("Webhook payload received:", payload, flush=True)
    return web.Response(status=200)


async def main():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./templates"))
    app.router.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8081)
    # Setup subscription before starting the main server loop
    try:
        await setup_subscription()
        print("Subscription setup complete", flush=True)
    except Exception as e:
        print(f"Failed to setup subscription: {e}", flush=True)

    await site.start()
    print(f"Serving on http://localhost:8081", flush=True)

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
