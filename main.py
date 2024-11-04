import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse

from utils.ECP.stationar import export_stories_function
from utils.L2.create_diaries import create_diaries_function
from utils.settings import UPLOAD_DIRECTORY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (можно указать конкретные домены)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)


@app.get('/')
async def get_main():
    return FileResponse('front/index.html')


@app.get('/styles.css')
async def get_script():
    return FileResponse('front/styles.css')


# @app.get('/script.js')
# async def get_script():
#     return FileResponse('front/scripts.js')


@app.get('/create-diaries')
async def create_diaries_handler():
    await create_diaries_function()
    return {'message': 'Diaries created', 'status': 200}


@app.get('/export-stories')
async def export_stories_handler():
    await export_stories_function()
    return {'message': 'Export stories done', 'status': 200}


@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    print(file.filename)
    # Проверяем тип файла
    if file.content_type not in ["application/vnd.ms-excel",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        raise HTTPException(status_code=400, detail="Неверный формат файла. Загрузите файл Excel.")

    # Путь для сохранения файла
    content = await file.read()
    with open(f"uploaded_files/{file.filename}", "wb") as f:
        f.write(content)

    return JSONResponse(content={"message": "Файл успешно загружен", "filename": file.filename})
