import asyncio
import os
from aiohttp import web, ClientSession
import jinja2
import aiohttp_jinja2
import base64
import json
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import secrets

# Rustici Engine API configuration
ENGINE_TENANT = os.environ.get('ENGINE_TENANT', 'default')
ENGINE_BASE_URL = os.environ.get('ENGINE_BASE_URL', 'http://localhost:8080/RusticiEngine/api/v2')
ENGINE_USERNAME = os.environ.get('ENGINE_USERNAME', 'your_username')
ENGINE_PASSWORD = os.environ.get('ENGINE_PASSWORD', 'your_password')

async def get_auth_token():
    credentials = base64.b64encode(f"{ENGINE_USERNAME}:{ENGINE_PASSWORD}".encode()).decode()
    return f"Basic {credentials}"

async def get_token(request):
    session = await get_session(request)
    if 'auth_token' not in session:
        session['auth_token'] = await get_auth_token()
    return web.json_response({'token': session['auth_token']})

async def handle(request):
    context = {
        'ENGINE_TENANT': ENGINE_TENANT,
        'ENGINE_BASE_URL': ENGINE_BASE_URL
    }
    response = aiohttp_jinja2.render_template("index.html", request, context)
    return response

async def upload_scorm(request):
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename
    size = 0
    file_path = os.path.join('uploads', filename)
    with open(file_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
    
    # Upload the course to Rustici Engine
    async with ClientSession() as session:
        auth_token = await get_auth_token()
        data = {
            "course": {
                "title": os.path.splitext(filename)[0],
                "xapiActivityId": f"http://example.com/courses/{filename}"
            }
        }
        files = {'file': open(file_path, 'rb')}
        async with session.post(
            f"{ENGINE_BASE_URL}/courses/importJobs?mayCreateNewVersion=true",
            headers={"Authorization": auth_token},
            data={'request': json.dumps(data)},
            files=files
        ) as response:
            if response.status == 200:
                result = await response.json()
                return web.Response(text=f"Course '{filename}' uploaded successfully. Job ID: {result['jobId']}")
            else:
                return web.Response(text=f"Failed to upload course. Status: {response.status}", status=400)

async def main():
    app = web.Application()
    setup(app, EncryptedCookieStorage(secrets.token_bytes(32)))
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./templates"))
    app.add_routes([
        web.get("/", handle),
        web.post("/upload", upload_scorm),
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
