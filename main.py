from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import uuid
import imageio_ffmpeg as ffmpeg

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://video-clip-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process-video")
async def process_video(
    file: UploadFile = File(None),
    youtube_url: str = Form(None)
):
    video_id = str(uuid.uuid4())

    input_path = f"{UPLOAD_DIR}/{video_id}.mp4"
    output_path = f"{OUTPUT_DIR}/{video_id}.mp4"

    # Handle upload
    if file:
        print("FILE RECEIVED:", file.filename)
        with open(input_path, "wb") as f:
            f.write(await file.read())
    else:
        print("NO FILE RECEIVED")
        return []

    ffmpeg_path = ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg_path,
        "-i", input_path,
        "-t", "30",
        "-vf", "scale=1080:1920",
        "-y",
        output_path
    ]

    subprocess.run(command)

    if not os.path.exists(output_path):
        output_path = input_path

    return [
        {
            "title": "Sample Clip",
            "video_url": f"https://video-backend-mjx4.onrender.com/outputs/{video_id}.mp4",
            "duration": "30s",
            "score": 90
        }
    ]
