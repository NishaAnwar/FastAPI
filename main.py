from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os
import shutil
import subprocess
import uuid

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running!"}

@app.post("/stylize")
async def stylize_image(file: UploadFile = File(...)):
    # Create unique ID
    unique_id = str(uuid.uuid4())
    extension = os.path.splitext(file.filename)[-1]
    filename = f"{unique_id}{extension}"

    # Paths
    input_dir = "inputs/imgs"
    output_dir = "output/results"
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)

    # Ensure directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run the ONNX script
    subprocess.run([
        "python", "deploy/test_by_onnx.py",
        "-i", input_dir,
        "-o", output_dir,
        "-m", "deploy/AnimeGANv3_Hayao_36.onnx"
    ])

    # Return the generated image
    if os.path.exists(output_path):
        return FileResponse(output_path, media_type="image/jpeg", filename="stylized.jpg")
    else:
        return {"error": "Stylized image not found."}
