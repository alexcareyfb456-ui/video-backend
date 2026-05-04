from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import uuid

app = FastAPI()

# Allow all origins (important)
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

    # Save uploaded video
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Cut first 30 sec + convert to vertical 9:16
    command = [
        "ffmpeg",
        "-i", input_path,
        "-t", "30",
        "-vf", "scale=1080:1920",
        "-y",
        output_path
    ]

    subprocess.run(command)

    return [
        {
            "title": "Sample Clip",
            "video_url": f"/outputs/{video_id}.mp4",
            "duration": "30s",
            "score": 90
        }
    ]
