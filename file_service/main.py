from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="File Service", version="1.0.0")

class DirectoryRequest(BaseModel):
    path: str

@app.post("/read_directory")
async def read_directory(request: DirectoryRequest):
    """
    Reads all files from a given directory and returns their content.
    """
    path = request.path
    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    file_contents = {}
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                file_contents[filename] = f.read()

    return file_contents
