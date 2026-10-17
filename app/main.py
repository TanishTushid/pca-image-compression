import base64
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.pca_processor import compress_image

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/templates/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.post('/api/compress')
async def compress(
    file: UploadFile = File(...),
    target_mb: float = Form(...),
):
    if file.content_type not in ['image/jpeg', 'image/png']:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")
    if not 0 < target_mb <= 10:
        raise HTTPException(status_code=400, detail="Target must be greater than 0 and at most 10 MB.")
    data = await file.read(10 * 1024 * 1024 + 1)  # Read up to 10 MB
    if not data:
        raise HTTPException(status_code=400, detail='The uploaded file is empty.')
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail='The uploaded file exceeds the maximum size of 10 MB.')
    try:
        result = compress_image(data, target_mb)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # log the full exception on the server in a real deployment
        raise HTTPException(status_code=400, detail="An error occurred during image compression.") from e
    encoded = base64.b64encode(result.pop('image_bytes')).decode('utf-8')
    return {
        **result,
        "image_data_url": f"data:image/jpeg;base64,{encoded}",
        "filename": "compressed-image.jpg",
    }

