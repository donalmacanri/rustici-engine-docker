import asyncio
import os
from aiohttp import web
import jinja2
import aiohttp_jinja2
import zipfile
import shutil

# Simulated database of courses
courses = [
    {"id": 1, "title": "Introduction to Python", "description": "Learn the basics of Python programming"},
    {"id": 2, "title": "Web Development with JavaScript", "description": "Master web development using JavaScript"},
]

async def handle(request):
    context = {"courses": courses}
    response = aiohttp_jinja2.render_template("index.html", request, context)
    return response

async def upload_scorm(request):
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename
    size = 0
    with open(os.path.join('uploads', filename), 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
    
    # Process the SCORM package (simplified for this example)
    course_id = len(courses) + 1
    course_title = os.path.splitext(filename)[0]
    courses.append({"id": course_id, "title": course_title, "description": "Newly uploaded SCORM course"})
    
    return web.Response(text=f"File '{filename}' uploaded successfully. Size: {size} bytes")

async def launch_course(request):
    course_id = int(request.match_info['id'])
    course = next((c for c in courses if c['id'] == course_id), None)
    if course:
        return web.Response(text=f"Launching course: {course['title']}")
    return web.Response(text="Course not found", status=404)

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
