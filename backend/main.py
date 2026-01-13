
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import shutil
import os
import uuid
import json

from crypto import PlayfairCipher, RailFenceCipher
from stego import embed_message, extract_message
from analyses import calculate_snr, LearningModule

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class EncryptionConfig(BaseModel):
    playfair_key: str
    railfence_key: int

class EmbedRequest(BaseModel):
    message: str
    playfair_key: str
    railfence_key: int
    bits_per_sample: int

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1]
    if extension.lower() != "wav":
        raise HTTPException(status_code=400, detail="Only WAV files supported")
    
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.wav")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_id": file_id, "filename": file.filename, "size": os.path.getsize(file_path)}

@app.post("/embed")
async def embed(
    file_id: str = Form(...),
    message: str = Form(...),
    playfair_key: str = Form(...),
    railfence_key: int = Form(...),
    bits_per_sample: int = Form(...)
):
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}.wav")
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    # 1. Encrypt
    pf = PlayfairCipher(playfair_key)
    encrypted_stage1 = pf.encrypt(message)
    
    rf = RailFenceCipher(railfence_key)
    final_ciphertext = rf.encrypt(encrypted_stage1)
    
    # 2. Embed
    output_filename = f"{file_id}_watermarked.wav"
    output_path = os.path.join(UPLOAD_DIR, output_filename)
    
    try:
        bits_embedded = embed_message(input_path, output_path, final_ciphertext, bits_per_sample)
    except Exception as e:
        lm = LearningModule()
        lm.record_attempt(file_id, os.path.getsize(input_path), bits_per_sample, False)
        raise HTTPException(status_code=400, detail=str(e))
        
    # 3. Analyze
    snr = calculate_snr(input_path, output_path)
    
    # 4. Record Success
    lm = LearningModule()
    lm.record_attempt(file_id, os.path.getsize(input_path), bits_per_sample, True, snr)
    
    return {
        "status": "success",
        "output_file": output_filename,
        "encrypted_message": final_ciphertext,
        "snr": snr,
        "bits_embedded": bits_embedded
    }

@app.get("/download/{filename}")
async def download(filename: str):
    from fastapi.responses import FileResponse
    path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404)

@app.post("/extract")
async def extract(
    file: UploadFile = File(...),
    playfair_key: str = Form(...),
    railfence_key: int = Form(...),
    bits_per_sample: int = Form(...)
):
    # Save temp
    temp_id = str(uuid.uuid4())
    temp_path = os.path.join(UPLOAD_DIR, f"extract_{temp_id}.wav")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Extract Ciphertext
        extracted_cipher = extract_message(temp_path, bits_per_sample)
        
        # Decrypt
        rf = RailFenceCipher(railfence_key)
        stage1 = rf.decrypt(extracted_cipher)
        
        pf = PlayfairCipher(playfair_key)
        plaintext = pf.decrypt(stage1)
        
        return {
            "success": True, 
            "extracted_ciphertext": extracted_cipher,
            "decrypted_message": plaintext
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/suggest")
def suggest(size: int):
    lm = LearningModule()
    return {"recommended_bits": lm.suggest_bits(size)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
