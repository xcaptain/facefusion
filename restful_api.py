from typing import Any
from fastapi import FastAPI, UploadFile
import os
import asyncio
import base64

app = FastAPI()

@app.post("/faceswap")
async def handle_faceswap(source_file: UploadFile, target_file: UploadFile) -> Any:
    # save files to filesystem
    source_file_path = f"uploads/{source_file.filename}"
    target_file_path = f"uploads/{target_file.filename}"
    output_file_path = f"uploads/output-{target_file.filename}"

    os.makedirs("uploads", exist_ok=True)

    # 保存源文件
    with open(source_file_path, "wb") as f:
        f.write(await source_file.read())

    # 保存目标文件
    with open(target_file_path, "wb") as f:
        f.write(await target_file.read())

    # execute a python command
    # python facefusion.py headless-run 
    # --processors face_swapper --face-mask-types box --face-swapper-model inswapper_128
    command = [
        "python", "facefusion.py", "headless-run", 
        "-processors", "face_swapper", "--face-mask-types", "box", "--face-swapper-model", "inswapper_128"
        "-s", source_file_path, 
        "-t", target_file_path, 
        "-o", output_file_path
    ]
    # subprocess.run(command, capture_output=True, text=True)
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()

    # check output_file_path exists
    if os.path.exists(output_file_path):
        print('executed successful')
        # read file content into base64
        with open(output_file_path, "rb") as f:
            output_file_base64 = base64.b64encode(f.read()).decode('utf-8')
            os.remove(source_file_path)
            os.remove(target_file_path)
            os.remove(output_file_path)
            return {
                'output_file_base64': output_file_base64
            }
    else:
        print('error, check again')
        os.remove(source_file_path)
        os.remove(target_file_path)
        return {"status": "failed"}
    

@app.get("/")
async def handle_root() -> Any:
    return {"status": "OK"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
