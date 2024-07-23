from fastapi import FastAPI
from starlette.responses import FileResponse

from utils.ECP.stationar import export_stories_function
from utils.L2.create_diaries import create_diaries_function

app = FastAPI()


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
