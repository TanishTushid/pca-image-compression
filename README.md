# PCA Image Compressor

A small web app for reducing PNG and JPEG image sizes with Principal Component
Analysis (PCA). Upload an image, choose a target size, review the compressed
preview and quality statistics, then download the result.

## Screenshots

### Image upload and target size

![PCA Image Compressor upload screen](website_image/Screenshot%20%28318%29.png)

### Compressed image preview and results

![PCA Image Compressor results screen](website_image/Screenshot%20%28319%29.png)

## Features

- Accepts JPEG and PNG uploads up to 10 MB.
- Lets you choose a target output size from 0.1 MB to 10 MB.
- Applies PCA to the image's color channels and tries progressively smaller
  resolutions, component counts, and JPEG quality levels to meet the target.
- Shows the compressed image, original and output sizes, and PSNR
  (Peak Signal-to-Noise Ratio).
- Provides the compressed result as a downloadable JPEG.

The requested target is a maximum size, not a guarantee: if none of the
supported resolution and quality settings can meet it, the app returns an
error suggesting a larger target.

## Requirements

- Python
- pip

Python dependencies are listed in `requirements.txt` (including FastAPI,
Uvicorn, Pillow, NumPy, and scikit-learn).

## Run locally

From the project directory, create and activate a virtual environment, install
the dependencies, and start the app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
Alternatively, start the development server directly with:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## API

`POST /api/compress` accepts a multipart form containing:

| Field | Type | Details |
| --- | --- | --- |
| `file` | File | JPEG or PNG image, up to 10 MB |
| `target_mb` | Number | Desired output size, greater than 0 and at most 10 MB |

On success, the response includes a base64 data URL for the JPEG output along
with its dimensions, file sizes, PCA component count, JPEG quality, explained
variance, MSE, and PSNR. Invalid uploads or targets return an error response.

## Project structure

```text
.
├── app/
│   ├── main.py                 # FastAPI routes and page setup
│   ├── pca_processor.py        # PCA compression and JPEG encoding
│   └── templates/
│       ├── index.html          # Web interface
│       └── static/             # CSS and JavaScript
├── website_image/              # README screenshots
├── requirements.txt
└── run.py                      # Local development entry point
```