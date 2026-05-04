from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import uuid
import imageio_ffmpeg as ffmpeg

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Serve output files
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process-video")
async def process_video(file: UploadFile = File(...)):
    video_id = str(uuid.uuid4())

    input_path = f"{UPLOAD_DIR}/{video_id}.mp4"
    output_path = f"{OUTPUT_DIR}/{video_id}.mp4"

    # Save file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    ffmpeg_path = ffmpeg.get_ffmpeg_exe()

    # Cut first 30 seconds + convert to vertical
    command = [
        ffmpeg_path,
        "-i", input_path,
        "-t", "30",
        "-vf", "scale=1080:1920",
        "-y",
        output_path
    ]

    subprocess.run(command)

    return {
    "clips": [
        {
            "title": "Sample Clip",
            "video_url": f"https://your-app.onrender.com/outputs/{video_id}.mp4",
            "duration": "30s",
            "score": 90
        }
    ]
}
