import datetime
import logging
import mimetypes
import time
import glob
import os
import random
import string
import uuid
import re

from storage import get_storage
import filetype
import timeout_decorator
from flask import Flask, jsonify, request, Response, send_file, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wand.exceptions import MissingDelegateError
from wand.image import Image
from werkzeug.middleware.proxy_fix import ProxyFix

import settings

level = logging.INFO
if os.getenv("DEBUG", "0") == "1":
    level = logging.DEBUG

logging.basicConfig(
    level=level, format="%(asctime)s | %(levelname)-8s %(name)-13s > %(message)s"
)

logger = logging.getLogger(__name__)

logger.info("imgpush is starting...")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

logger.info("-" * 40)

storage = get_storage()
logger.info("Using storage: %s" % storage.__class__.__name__)
logger.info(storage)

logger.info("-" * 40)

CORS(app, origins=settings.ALLOWED_ORIGINS)
app.config["MAX_CONTENT_LENGTH"] = settings.MAX_SIZE_MB * 1024 * 1024
limiter = Limiter(get_remote_address, app=app, default_limits=[])

logger.info("imgpush is listening on port 5000!")

app.use_x_sendfile = True


@app.after_request
def after_request(resp):
    x_sendfile = resp.headers.get("X-Sendfile")
    if x_sendfile:
        resp.headers["X-Accel-Redirect"] = "/nginx/" + x_sendfile
        del resp.headers["X-Sendfile"]
    resp.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    return resp


class InvalidSize(Exception):
    pass


class CollisionError(Exception):
    pass


class InvalidFileTypeError(Exception):
    pass


def _get_size_from_string(size):
    try:
        size = int(size)
        if len(settings.VALID_SIZES) and size not in settings.VALID_SIZES:
            raise InvalidSize
    except ValueError:
        size = ""
    return size


def _clear_imagemagick_temp_files():
    """
    A bit of a hacky solution to prevent exhausting the cache ImageMagick uses on disk.
    It works by checking for imagemagick cache files under /tmp/
    and removes those that are older than settings.MAX_TMP_FILE_AGE in seconds.
    """
    imagemagick_temp_files = glob.glob("/tmp/magick-*")
    for filepath in imagemagick_temp_files:
        modified = datetime.datetime.strptime(
            time.ctime(os.path.getmtime(filepath)),
            "%a %b %d %H:%M:%S %Y",
        )
        diff = datetime.datetime.now() - modified
        seconds = diff.seconds
        if seconds > settings.MAX_TMP_FILE_AGE:
            os.remove(filepath)


def _get_random_filename():
    random_string = _generate_random_filename()
    if settings.NAME_STRATEGY == "randomstr":
        file_exists = len(glob.glob(f"{settings.FILES_DIR}/{random_string}.*")) > 0
        if file_exists:
            return _get_random_filename()
    return random_string


def _generate_random_filename():
    if settings.NAME_STRATEGY == "uuidv4":
        return str(uuid.uuid4())
    if settings.NAME_STRATEGY == "randomstr":
        return "".join(
            random.choices(
                string.ascii_lowercase + string.digits + string.ascii_uppercase, k=5
            )
        )


def _resize_image(path, width, height):
    with Image(filename=path) as src:
        img = src.clone()

    current_aspect_ratio = img.width / img.height

    if not width:
        width = int(current_aspect_ratio * height)

    if not height:
        height = int(width / current_aspect_ratio)

    desired_aspect_ratio = width / height

    # Crop the image to fit the desired AR
    if desired_aspect_ratio > current_aspect_ratio:
        newheight = int(img.width / desired_aspect_ratio)
        img.crop(
            0,
            int((img.height / 2) - (newheight / 2)),
            width=img.width,
            height=newheight,
        )
    else:
        newwidth = int(img.height * desired_aspect_ratio)
        img.crop(
            int((img.width / 2) - (newwidth / 2)),
            0,
            width=newwidth,
            height=img.height,
        )

    @timeout_decorator.timeout(settings.RESIZE_TIMEOUT)
    def resize(img, width, height):
        img.sample(width, height)

    try:
        resize(img, width, height)
    except timeout_decorator.TimeoutError:
        pass

    return img


@app.route("/liveness", methods=["GET"])
def liveness():
    return Response(status=200)


@app.route("/", methods=["POST"])
@limiter.limit(
    "".join(
        [
            f"{settings.MAX_UPLOADS_PER_DAY}/day;",
            f"{settings.MAX_UPLOADS_PER_HOUR}/hour;",
            f"{settings.MAX_UPLOADS_PER_MINUTE}/minute",
        ]
    )
)
def upload_file():
    _clear_imagemagick_temp_files()

    if "file" not in request.files:
        return jsonify(error="File is missing!"), 400

    file = request.files["file"]

    # Saving the file to a temporary location
    random_string = _get_random_filename()
    tmp_filepath = os.path.join("/tmp/", random_string)
    file.save(tmp_filepath)
    file.seek(0)

    file_type = filetype.guess(tmp_filepath)
    if file_type is None:
        return jsonify(error="File type could not be determined!"), 400

    output_type = settings.OUTPUT_TYPE or file_type.extension
    output_filename = os.path.basename(tmp_filepath) + f".{output_type}"

    error = None

    try:
        if file_type.mime not in settings.ALLOWED_MIME_FILE_TYPES:
            raise InvalidFileTypeError
        if storage.exists(output_filename):
            raise CollisionError
        if file_type.mime not in settings.RESIZABLE_MIME_FILE_TYPES:
            # We need a BufferedReader to be able to save the file to the storage provider
            with open(tmp_filepath, "rb") as file:
                storage.save(file, output_filename)
            os.remove(tmp_filepath)
        else:
            converted_file_path = f"{tmp_filepath}.{output_type}"

            with Image(filename=tmp_filepath) as img:
                img.strip()
                if output_type not in ["gif"]:
                    with img.sequence[0] as first_frame:
                        with Image(image=first_frame) as first_frame_img:
                            with first_frame_img.convert(output_type) as converted:
                                converted.save(filename=converted_file_path)
                else:
                    with img.convert(output_type) as converted:
                        converted.save(filename=converted_file_path)

            with open(converted_file_path, "rb") as converted_file:
                storage.save(converted_file, output_filename)
            # After saving the converted file on the storage provider, we can delete the temporary file from the filesystem
            os.remove(converted_file_path)

    except (MissingDelegateError, InvalidFileTypeError):
        error = "Invalid Filetype"
    finally:
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)

    if error:
        return jsonify(error=error), 400

    return jsonify(filename=output_filename)


@app.route("/<string:filename>", methods=["DELETE"])
@limiter.exempt
def delete_image(filename):
    # check the name looks like a filename and
    # need some more protection
    if (filename) and (re.match("^[\w\d-]+\.[\w\d]+$", filename)):
        storage.delete(filename)
    return Response(status=200)


@app.route("/<string:filename>")
@limiter.exempt
def get_file(filename):
    if not storage.exists(filename):
        return jsonify(error="File not found!"), 404

    file_type = mimetypes.guess_type(filename)
    mime_type = file_type[0]

    if file_type is None:
        response = jsonify(error="File type could not be determined!"), 500
        return response

    width = request.args.get("w", "")
    height = request.args.get("h", "")

    # If the file type is resizable and the user is asking for a resized version
    # we first check if it is cached before downloading the file
    if mime_type in settings.RESIZABLE_MIME_FILE_TYPES and (width or height):
        try:
            width = _get_size_from_string(width)
            height = _get_size_from_string(height)
        except InvalidSize:
            return (
                jsonify(error=f"size value must be one of {settings.VALID_SIZES}"),
                400,
            )

        response = get_or_create_resized_image(filename, width, height)
        apply_cache(response)
        return response

    # If the file type is not resizable, or the user is not asking for a resized version
    # We serve the file directly
    tmp_filepath, delete_temporary_file = storage.get(filename)

    response = send_file(tmp_filepath)
    delete_temporary_file()

    apply_cache(response)
    return response


def apply_cache(response):
    response.headers["Cache-Control"] = f"public, max-age={60*60}"
    response.headers["Expires"] = f"{60*60}"


def get_or_create_resized_image(filename, width, height):
    filename_without_extension, extension_with_dot = os.path.splitext(filename)
    extension = extension_with_dot[1:]  # remove the dot from the extension
    dimensions = f"{width}x{height}"
    resized_filename = f"{filename_without_extension}_{dimensions}.{extension}"

    resized_path = os.path.join(settings.CACHE_DIR, resized_filename)

    # If the resized version is cached, we return it
    if os.path.isfile(resized_path) and (width or height):
        return send_from_directory(settings.CACHE_DIR, resized_filename)
    # If the resized version is not cached, we generate it and return it
    else:
        tmp_filepath, delete_temporary_file = storage.get(filename)

        resized_image = _resize_image(tmp_filepath, width, height)
        resized_image.strip()

        resized_image.save(filename=resized_path)
        resized_image.close()

        delete_temporary_file()
        return send_file(resized_path)


@app.route("/metrics", methods=["GET"])
def metrics():
    return storage.get_metrics()

@app.route("/info", methods=["GET"])
def info():
    return jsonify({
        "application": {
            "name": "imgpush",
            "version": "0.2.0"
        },
        "storage": {
            "type": storage.__class__.__name__,
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
