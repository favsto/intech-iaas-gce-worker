from flask import Flask
from google.cloud import storage
from google.cloud.storage import Blob
from PIL import Image, ImageFilter, ImageEnhance, ImageMath
import os
import random
import string
# from scipy import signal
# from numpy import asarray
import time

app = Flask(__name__)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@app.route("/")
def hello():
    start_time = time.time()
    source_image_name = 'lion-wild-africa-african.jpg'
    client = storage.Client()
    # lion-wild-africa-african.jpg
    bucket = client.get_bucket('injenia-ricerca')
    # encryption_key = 'c7f32af42e45e85b9848a6a14dd2a8f6'
    blob = Blob(source_image_name, bucket)
    dl_file_name = "dl_%s.jpg" % id_generator()
    with open(dl_file_name, 'wb') as file_obj:
        blob.download_to_file(file_obj)
    im1 = Image.open(dl_file_name)
    im2 = im1.filter(ImageFilter.EDGE_ENHANCE_MORE)
    enhancer = ImageEnhance.Sharpness(im2)
    im3 = enhancer.enhance(2.0)
    # out = ImageMath.eval("min(convert(a, 'L'), convert(b, 'L'))", a=im1, b=im3)
    out = ImageMath.eval("convert(a, 'L')", a=im3)
    # cor = signal.correlate2d (asarray(im1.convert('1')), asarray(im3.convert('1')))
    res_file_name = "res_%s_%s.png" % (source_image_name, id_generator())
    out.save(res_file_name)
    blob = Blob(res_file_name, bucket)
    with open(res_file_name, 'rb') as my_file:
        blob.upload_from_file(my_file)
    os.remove(dl_file_name)
    os.remove(res_file_name)
    return "Execution time: %s seconds" % (time.time() - start_time)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
