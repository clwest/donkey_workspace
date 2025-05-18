import mimetypes
import mimetypes
import pathlib
import shutil
import os
import tempfile
from dotenv import load_dotenv
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
REPLICATE_MODEL = os.getenv(
    "REPLICATE_MODEL", default="codingforentrepreneurs/superme-justin-v1"
)
REPLICATE_MODEL_VERSION = os.getenv(
    "REPLICATE_MODEL_VERSION",
    default="4bc2a39fa73d29cd531c57ad4f56bede13378ce3da2f6f517684b0b61bd192d7",
)

register_heif_opener()

NBS_DIR = pathlib.Path().resolve()
REPO_DIR = NBS_DIR.parent
DATA_DIR = REPO_DIR / "data"
INPUTS_DIR = DATA_DIR / "inputs"
OUTPUTS_DIR = DATA_DIR / "outputs"

image_file_paths = []
""" Create the dataset loading up images. """
for file_path in INPUTS_DIR.glob("*"):
    guessed_type, encoding = mimetypes.guess_type(file_path)
    if "image" not in guessed_type:
        continue
    image_file_paths.append(file_path)

zip_outpath = OUTPUTS_DIR / "images.zip"
zip_outpath.exists()

zip_outpath.with_suffix("")

with tempfile.TemporaryDirectory() as temp_dir:
    for path in image_file_paths:
        shutil.copy(path, temp_dir)
    shutil.make_archive(zip_outpath.with_suffix(""), "zip", temp_dir)


""" Validate the images in zip"""


def perform_is_image(path, require_can_open=True):
    try:
        guessed_type, encoding = mimetypes.guess_type(path)
    except:
        guessed_type = ""
    guessed_image = "image" in guessed_type
    if not guessed_image:
        return False
    if guessed_image and require_can_open:
        try:
            img_ = Image.open(path)
        except:
            return False
    return True


image_file_paths = []

for file_path in INPUTS_DIR.glob("*"):
    is_image = perform_is_image(file_path)
    if not is_image:
        continue
    image_file_paths.append(file_path)

""" Optimize-images"""


def perform_clear_and_optimize_image(image_path, output_path, max_size=(1920, 1920)):
    """
    Removes all metadata from an image (e.g. EXIF data).
    Optimizes the image file size while preserving quality and transparency when needed.
    """
    # Convert to Path objects
    image_path = pathlib.Path(image_path)
    output_path = pathlib.Path(output_path)

    # Open and create clean copy
    original = Image.open(image_path)

    # Determine if image has transparency
    has_transparency = original.mode in ("RGBA", "LA") or (
        original.mode == "P" and "transparency" in original.info
    )

    # Auto-rotate based on EXIF
    original = ImageOps.exif_transpose(original)

    # Resize if larger than max_size while maintaining aspect ratio
    if original.size[0] > max_size[0] or original.size[1] > max_size[1]:
        original.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Convert mode based on transparency
    if has_transparency:
        if original.mode != "RGBA":
            original = original.convert("RGBA")
        best_format = "PNG"
    else:
        if original.mode in ("RGBA", "P", "LA"):
            original = original.convert("RGB")
        best_format = "JPEG"

    # Save with optimized settings
    save_kwargs = {}
    if best_format == "JPEG":
        save_kwargs.update({"quality": 85, "optimize": True, "progressive": True})
        output_path = output_path.with_suffix(".jpg")
    elif best_format == "PNG":
        save_kwargs.update({"optimize": True, "compress_level": 6})
        output_path = output_path.with_suffix(".png")
    print(f"Saving {output_path}")
    original.save(output_path, format=best_format, **save_kwargs)
    return output_path


def perform_is_image(path, require_can_open=True):
    try:
        guessed_type, encoding = mimetypes.guess_type(path)
    except:
        guessed_type = ""
    guessed_image = "image" in guessed_type
    if not guessed_image:
        return False
    if guessed_image and require_can_open:
        try:
            img_ = Image.open(path)
        except:
            return False
    return True


"""Generate Images"""

from replicate.client import Client

replicate_client = Client(api_token=REPLICATE_API_TOKEN)

model = f"{REPLICATE_MODEL}:{REPLICATE_MODEL_VERSION}"
prompt = "a photo of TOK adult man dressed up for a professional photo shoot"

import os

if os.getenv("REPLICATE_API_TOKEN", ""):
    responses = replicate_client.run(
        "stability-ai/some-model-id",
        input={"prompt": prompt},
    )
else:
    print("🚫 Skipping Replicate call — no API key or invalid model version.")
    responses = []

import random

session_id = random.randint(1_000, 40_000)
for i, output in enumerate(responses):
    fname = f"{i}-{session_id}.jpg"
    outpath = GENERATED_DIR / fname
    with open(outpath, "wb") as f:
        f.write(output.read())


"""Generate image with reference"""
reference_image_path = REFERENCES_DIR / "spider-man.webp"
image = open(reference_image_path, "rb")

model = f"{REPLICATE_MODEL}:{REPLICATE_MODEL_VERSION}"
prompt = "a photo of TOK adult man dressed up as spider-man"

responses = replicate_client.run(
    model,
    input={
        "image": image,
        "model": "dev",
        "prompt": prompt,
        "num_outputs": 4,
        "output_format": "jpg",
    },
)
image.close()

import random

session_id = random.randint(1_000, 40_000)
for i, output in enumerate(responses):
    fname = f"{i}-{session_id}.jpg"
    outpath = GENERATED_DIR / fname
    with open(outpath, "wb") as f:
        f.write(output.read())

"""Trigger Background Generation"""
model = f"{REPLICATE_MODEL}:{REPLICATE_MODEL_VERSION}"
prompt = "a photo of TOK adult man dressed up for a sports photo shoot"
num_outputs = 2
output_format = "jpg"

input_args = {
    "prompt": prompt,
    "num_outputs": 2,
    "output_format": "jpg",
}

rep_model = replicate_client.models.get(REPLICATE_MODEL)
rep_version = rep_model.versions.get(REPLICATE_MODEL_VERSION)

pred = replicate_client.predictions.create(version=rep_version, input=input_args)
pred.id
pred.status

pred_id = "dat0d05k01rma0ck9cn8hs27aw"
pred_lookup = replicate_client.predictions.get(pred_id)

import httpx
import random

session_id = random.randint(1_000, 40_000)
with httpx.Client() as client:
    for i, url in enumerate(pred_urls):
        fname = f"{i}-{session_id}.jpg"
        outpath = GENERATED_DIR / fname
        res = client.get(url)
        res.raise_for_status()
        with open(outpath, "wb") as f:
            f.write(res.content)

""" Proxy Genreate Image"""


import httpx


API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")

headers = {"X-API-Key": API_ACCESS_KEY}

endpoint = "http://127.0.0.1:8000/generate"

prompt = "a photo of TOK adult man dressed up for a pro photo shoot"
res = httpx.post(endpoint, json={"prompt": prompt}, headers=headers)
res.status_code, res.json()

"""Test API Rate Limit"""
import httpx


API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")

headers = {"X-API-Key": API_ACCESS_KEY}
endpoint = "http://127.0.0.1:8000/"
res = httpx.get(endpoint, headers=headers)
res.status_code, res.json(), res.headers.get("Retry-After")

API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")

headers = {"X-API-Key": API_ACCESS_KEY}
endpoint = "http://127.0.0.1:8000/processing"
preds_res = httpx.get(endpoint, headers=headers)
preds_json = preds_res.json()
preds_json

API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")

headers = {"X-API-Key": API_ACCESS_KEY}
# endpoint = "http://127.0.0.1:8000/predictions"
recent_url = preds_json[0].get("url")
if not recent_url.startswith("/"):
    recent_url = f"/{recent_url}"
detail_url = f"http://127.0.0.1:8000{recent_url}"
res = httpx.get(detail_url, headers=headers)
res.status_code
res.json()

import pathlib

for obj in preds_json:
    path = obj.get("url")
    endpoint = f"http://127.0.0.1:8000{path}"
    res = httpx.get(endpoint, headers=headers)
    if res.status_code not in range(200, 299):
        continue
    data = res.json()
    print(data)
    # _id = data.get('id')
    # _input = data.get('input') or {}
    # num_outputs = _input.get('num_outputs') or 0
    # _output = data.get('output')
    # if _output is None:
    #     continue
    # print(data)
    # output_names = [pathlib.Path(x) for x in _output]
    # print(num_outputs, output_names)
    # for x, output_path in enumerate(output_names):
    #     suffix = output_path.suffix
    #     print(f"{path}/file/{x}{suffix}")
    # # print(_id, num_outputs, _output)
    # break

"""Save File Outputs"""
NBS_DIR = pathlib.Path().resolve()
REPO_DIR = NBS_DIR.parent
DATA_DIR = REPO_DIR / "data"
GENERATED_DIR = DATA_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True, parents=True)

API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")

headers = {"X-API-Key": API_ACCESS_KEY}
endpoint = "http://127.0.0.1:8000/predictions"
preds_res = httpx.get(endpoint, params={"status": "succeeded"}, headers=headers)
preds_json = preds_res.json()
# preds_json

BASE_URL = "http://127.0.0.1:8000"
for pred in preds_json:
    path = pred.get("url")
    endpoint = f"{BASE_URL}{path}"
    res = httpx.get(endpoint, headers=headers)
    if res.status_code not in range(200, 299):
        continue
    data = res.json()
    files = data.get("files") or None
    if files is None:
        continue
    obj_id = data.get("id")
    with httpx.Client() as client:
        for i, file_path in enumerate(files):
            fname = pathlib.Path(file_path).name
            outpath = GENERATED_DIR / obj_id / fname
            outpath.parent.mkdir(exist_ok=True, parents=True)
            if outpath.exists():
                continue
            url = f"{BASE_URL}{file_path}"
            res = client.get(url, headers=headers)
            res.raise_for_status()
            with open(outpath, "wb") as f:
                f.write(res.content)


"""Tie it together"""

import httpx
import pathlib

NBS_DIR = pathlib.Path().resolve()
REPO_DIR = NBS_DIR.parent
DATA_DIR = REPO_DIR / "data"
GENERATED_DIR = DATA_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True, parents=True)

prompt = input("What is your prompt?\n")
prompt_final = f"a photo of TOK adult man {prompt}"
prompt_final

API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")
BASE_URL = "http://127.0.0.1:8000"

headers = {"X-API-Key": API_ACCESS_KEY}
endpoint = f"{BASE_URL}/generate"
res = httpx.post(endpoint, json={"prompt": prompt_final}, headers=headers)
res.json()

import time


pred_id = res.json().get("id")
pred_detail_endpoint = f"{BASE_URL}/predictions/{pred_id}"
res2 = httpx.get(pred_detail_endpoint, headers=headers)
pred_data = res2.json()
pred_status = pred_data.get("status")

max_attempts = 10
attempts = 0
ready_and_done = pred_status == "succeeded"
while pred_status != "succeeded" and max_attempts > attempts:
    _res = httpx.get(pred_detail_endpoint, headers=headers)
    pred_data = _res.json()
    pred_status = pred_data.get("status")
    print(pred_id, pred_status)
    if pred_status == "succeeded":
        ready_and_done = True
        break
    attempts += 1
    time.sleep(5)


def download_image(url, obj_id):
    fname = pathlib.Path(url).name
    outpath = GENERATED_DIR / obj_id / fname
    outpath.parent.mkdir(exist_ok=True, parents=True)
    if outpath.exists():
        return outpath
    res = httpx.get(url, headers=headers)
    res.raise_for_status()
    with open(outpath, "wb") as f:
        f.write(res.content)
    return outpath


out_paths = []
if ready_and_done:
    files = pred_data.get("files")
    obj_id = pred_data.get("id")
    for file_path in files:
        endpoint = f"{BASE_URL}{file_path}"
        out_path = download_image(endpoint, obj_id)
        if out_path:
            out_paths.append(out_path)
out_paths

from PIL import Image

for path in out_paths:
    img = Image.open(path)
    img.show()
