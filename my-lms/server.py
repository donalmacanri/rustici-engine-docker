import asyncio
import os
from aiohttp import web, ClientSession
import jinja2
import aiohttp_jinja2
import base64
import json

# Rustici Engine API configuration
ENGINE_TENANT = "default"
ENGINE_BASE_URL = "http://localhost:8080/RusticiEngine/api/v2"
ENGINE_USERNAME = "your_username"
ENGINE_PASSWORD = "your_password"

async def get_auth_token():
    credentials = base64.b64encode(f"{ENGINE_USERNAME}:{ENGINE_PASSWORD}".encode()).decode()
    return f"Basic {credentials}"

async def get_courses():
    async with ClientSession() as session:
        auth_token = await get_auth_token()
        async with session.get(
            f"{ENGINE_BASE_URL}/courses",
            headers={"Authorization": auth_token}
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []

async def handle(request):
    courses = await get_courses()
    context = {"courses": courses}
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

async def launch_course(request):
    course_id = request.match_info['id']
    async with ClientSession() as session:
        auth_token = await get_auth_token()
        async with session.post(
            f"{ENGINE_BASE_URL}/courses/{course_id}/registrations",
            headers={"Authorization": auth_token},
            json={"registrationId": f"reg-{course_id}-{asyncio.get_event_loop().time()}"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                return web.Response(text=f"Course launched. Launch URL: {result['launchLink']}", content_type='text/html')
            else:
                return web.Response(text="Failed to launch course", status=400)

async def main():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./templates"))
    app.add_routes([
        web.get("/", handle),
        web.post("/upload", upload_scorm),
        web.get("/launch/{id}", launch_course)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print(f"Serving on http://localhost:8080")
    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
