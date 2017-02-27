from flask import Flask
from flask import json
from google.cloud import storage
from google.cloud.storage import Blob
from PIL import Image, ImageFilter, ImageEnhance, ImageMath
import os
import random
import string
import time
import mysql.connector
import requests

__author__ = "Injenia Srl"
__credits__ = "Fausto Fusaro"
__version__ = "0.1.0b"
__email__ = "fausto.fusaro@injenia.it"

config = {
    'user': 'intech',
    'password': 'intech2017',
    'host': '127.0.0.1',
    'database': 'intech',
}

destination_bucket = 'injenia-ricerca'

app = Flask(__name__)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
    Create a random string
    :param size: length of the generated string
    :param chars: set of chars to pick from
    :return: a new random string
    """
    return ''.join(random.choice(chars) for _ in range(size))


def am_i_ok():
    """
    A dummy check of instance health. If there is a file alarm.txt the instance is unhealthy!
    :return: a boolean True if it is ok, False otherwise
    """
    if os.path.isfile("alarm.txt"):
        return False
    return True


@app.route("/")
def manipulate():

    # initialize execution timer
    start_time = time.time()

    response_obj = None

    if am_i_ok():
        # MySQL initialization
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # instance metadata
        worker = 'someone'
        try:
            req = requests.get(
                "http://metadata/computeMetadata/v1/instance/name",
                headers={'Metadata-Flavor': 'Google'})
            if req.status_code < 299:
                worker = req.text
            else:
                print("Worker name unrecognized")
        except:
            print("Worker name unrecognized")
            worker = 'unrecognized'

        try:
            # seek my job
            job_etag = id_generator()
            mysql_set_job = "UPDATE jobs SET status=2, worker=%s, etag=%s, id = @selected_job := id " \
                            "WHERE status in (0, 3) LIMIT 1"
            cursor.execute(mysql_set_job, (worker, job_etag))
            cnx.commit()

            mysql_get_job = "SELECT id, image_bucket, image_path, status, worker, etag " \
                            "FROM jobs WHERE id = @selected_job"
            cursor.execute(mysql_get_job)

            job_id = None
            job_bucket = None
            job_image = None
            for (jid, image_bucket, image_path, status, worker, etag) in cursor:
                print("DEBUG: jid=%s, image_bucket=%s, image_path=%s, status=%s, worker=%s, etag=%s" %
                      (jid, image_bucket, image_path, status, worker, etag))
                if etag == job_etag:
                    # I have a job!
                    job_id = jid
                    job_bucket = image_bucket
                    job_image = image_path

                    print('Ready to execute the job %s: %s/%s' % (job_id, job_bucket, job_image))
                else:
                    # I don't have a job :(
                    print('All jobs are completed')
                break

            if job_id is None:
                print('There aren\'t jobs. Closing the communication :( bye')
                cursor.close()
                cnx.close()
                response_obj = app.response_class(
                    response=json.dumps({
                        'status': 'I\'m jobless... I have no tasks'
                    }),
                    status=404,
                    mimetype='application/json'
                )
                return response_obj

            # initialize GCS client and source image
            client = storage.Client()
            source_bucket = client.get_bucket(job_bucket)
            blob = Blob(job_image, source_bucket)
            dl_file_name = "dl_%s.jpg" % id_generator()
            with open(dl_file_name, 'wb') as file_obj:
                blob.download_to_file(file_obj)

            # process source image
            im1 = Image.open(dl_file_name)
            im2 = im1.filter(ImageFilter.EDGE_ENHANCE_MORE)
            enhancer = ImageEnhance.Sharpness(im2)
            im3 = enhancer.enhance(2.0)
            out = ImageMath.eval("convert(a, 'L')", a=im3)

            # save new image
            res_file_name = "%s_%s.png" % (job_image, id_generator())
            out.save(res_file_name)

            # upload image to my GCS bucket
            dest_bucket = client.get_bucket(destination_bucket)
            blob = Blob("restults/%s" % res_file_name, dest_bucket)
            with open(res_file_name, 'rb') as my_file:
                blob.upload_from_file(my_file)

            # cleaning stuffs
            os.remove(dl_file_name)
            os.remove(res_file_name)

            # a polite response
            response_body = {
                'seconds': (time.time() - start_time),
                'job': {
                    'id': job_id,
                    'image_bucket': job_bucket,
                    'image_path': job_image,
                    'etag': job_etag,
                    'worker': worker
                }
            }
            response_obj = app.response_class(
                response=json.dumps(response_body),
                status=200,
                mimetype='application/json'
            )
        except:
            print("Runtime error")
            # a ugly response
            response_obj = app.response_class(
                response=json.dumps({
                    'seconds': (time.time() - start_time),
                    'status': 'runtime error'
                }),
                status=500,
                mimetype='application/json'
            )

            # write a file for the health check
            with open("alarm.txt", 'w') as file_obj:
                file_obj.write("this is an error!")

        try:
            # closing connections
            cursor.close()
            cnx.close()
        except:
            pass
    else:
        # ops, something is wrong
        response_obj = app.response_class(
            response=json.dumps({
                'seconds': (time.time() - start_time),
                'status': 'the instance is corrupted!'
            }),
            status=500,
            mimetype='application/json'
        )

    return response_obj


@app.route("/healthcheck")
def health_check():
    response_obj = None

    if am_i_ok():
        response_obj = app.response_class(
            response=json.dumps({
                'status': 'ok'
            }),
            status=200,
            mimetype='application/json'
        )
    else:
        response_obj = app.response_class(
            response=json.dumps({
                'status': 'something wrong!'
            }),
            status=500,
            mimetype='application/json'
        )

    return response_obj


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
