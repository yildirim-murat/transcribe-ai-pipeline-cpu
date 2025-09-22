import os
import time
import soundfile as sf
import gc
from fastapi import FastAPI, File, UploadFile
from transformers import pipeline

device = "cpu"

print(f"🔧 Whisper pipeline başlatılıyor... (device={device})")

pipe = pipeline(
    task="automatic-speech-recognition",
    model="openai/whisper-large-v3", 
    chunk_length_s=30,
    batch_size=1,
    device=-1
)

pipe.model.config.forced_decoder_ids = pipe.tokenizer.get_decoder_prompt_ids(
    language="turkish", task="transcribe"
)

app = FastAPI(title="Whisper ASR API", version="1.0.0")


@app.post("/upload_transcribe")
async def upload_transcribe(file: UploadFile = File(...)):
    start_time = time.time()

    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    audio_info = sf.info(temp_path)
    call_duration = audio_info.frames / audio_info.samplerate

    res = pipe(temp_path)
    total_time = time.time() - start_time

    os.remove(temp_path)

    gc.collect()

    return {
        "method": "transformers-pipeline",
        "device": device,
        "transcript": res["text"],
        "call_duration_seconds": round(call_duration, 2),
        "processing_time_seconds": round(total_time, 2)
    }