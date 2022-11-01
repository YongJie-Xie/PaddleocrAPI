import argparse
import base64
import os
import sys
import textwrap

from mugwort import Logger

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

log = Logger('PaddleocrAPI', Logger.INFO)
log.info('PaddleocrAPI is starting, please wait...')

parser = argparse.ArgumentParser(
    description='This is a project that wraps Paddleocr by FastAPI.',
    formatter_class=argparse.RawTextHelpFormatter,
    epilog=r'''
  PaddleocrAPI Helper

    Tips: Params det/rec/cls are optional, default True.

    # Exp1. post single image in base64 in body (Supported)
    response = requests.post(url, data=image_base64)
    print(json.dumps(response.json()))

    # Exp2. post multiple image in binary in form body
    response = requests.post(
        url,
        params={'rec': False, 'cls': False},
        files={'file': image_binary},
    )
    print(json.dumps(response.json()))

    # Exp3. post multiple image in base64 in form body
    response = requests.post(
        url,
        params={'det': False, 'cls': False},
        data={'example': image_base64},
    )
    print(json.dumps(response.json()))

    # Exp4. post multiple image in base64 in json body
    response = requests.post(
        url,
        params={'det': False, 'rec': False, 'cls': False},
        json={'example': image_base64.decode()}
    )
    print(json.dumps(response.json()))
''')
parser.add_argument('--host', type=str, help='listen host')
parser.add_argument('--port', type=int, help='listen port')
parser.add_argument('--lang', type=str, help='language code')
parser.add_argument('--model-dir', type=str, help=r'model folder')
parser.set_defaults(host='127.0.0.1', port=8000, lang='en')
params = parser.parse_args()

# init model dir
abs_model_dir = os.path.join(os.path.expanduser('~'), '.paddleocr')
if params.model_dir:
    os.makedirs(params.model_dir, exist_ok=True)
    if os.path.isdir(params.model_dir):
        abs_model_dir = os.path.abspath(params.model_dir)
log.info('PaddleocrAPI model dir: %s', abs_model_dir)

try:
    from fastapi import FastAPI, Request
    from fastapi.datastructures import StarletteUploadFile
    from paddleocr import PaddleOCR

    app = FastAPI(openapi_url=None)
    ocr = PaddleOCR(
        lang=params.lang,
        show_log=False,
        det_model_dir=os.path.join(abs_model_dir, 'whl', 'det'),
        rec_model_dir=os.path.join(abs_model_dir, 'whl', 'rec'),
        cls_model_dir=os.path.join(abs_model_dir, 'whl', 'cls'),
    )
except ImportError as exc:
    log.exception(exc)
    sys.exit(1)


@app.on_event('startup')
async def print_startup_config():
    log.info(
        textwrap.dedent('''
            PaddleocrAPI has been started
              Endpoint: POST http://%s:%d/ocr
              Language: %s
        ''').strip(),
        params.host,
        params.port,
        params.lang
    )


async def ocr_executor(
        img: bytes,
        det: bool = True, rec: bool = True, cls: bool = True,
) -> str:
    res = ocr.ocr(img, det=det, rec=rec, cls=cls)
    log.info(
        'size: %d, det: %s, rec: %s, cls: %s, result: %s',
        len(img), det, rec, cls, res
    )
    return res


@app.post('/ocr')
async def ocr_endpoint(
        *, request: Request,
        det: bool = True, rec: bool = True, cls: bool = True,
):
    if 'content-type' in request.headers:
        content_type = request.headers.get('content-type').lower()
        log.info('Request ContentType: %s', content_type)

        images = {}
        if content_type.startswith('multipart/form-data'):
            data = await request.form()
            for key, image in data.items():  # type: str, StarletteUploadFile
                images[key] = await image.read()
        elif content_type == 'application/x-www-form-urlencoded':
            data = await request.form()
            for key, image in data.items():  # type: str, str
                images[key] = base64.b64decode(image)
        elif content_type == 'application/json':
            data = await request.json()
            for key, image in data.items():  # type: str, str
                images[key] = base64.b64decode(image)
        else:
            log.warning('Unsupported Content-Type: %s', type(content_type))

        for key, image_raw in images.items():  # type: str, bytes
            try:
                images[key] = await ocr_executor(image_raw, det, rec, cls)
            except Exception as e:
                log.exception(e)
                images[key] = None

        return images if images else None
    else:
        body = await request.body()

        if body:
            try:
                image_raw = base64.b64decode(body)
                return await ocr_executor(image_raw, det, rec, cls)
            except Exception as e:
                log.exception(e)

        return None


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app,
        host=params.host,
        port=params.port,
        log_level='error',
        access_log=False,
    )
