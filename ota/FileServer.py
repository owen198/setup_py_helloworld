#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask, jsonify, request, send_file
import subprocess

app = Flask(__name__)

STATUS_CODE = "statuscode"
ALLOWED_EXTENSIONS = ['pkl', 'bat']

PATH_ROOT = "/root/afs-sdk/"
PATH_OTA = PATH_ROOT + "ota/"
PATH_MODEL = PATH_OTA + "model/"
NAME_PACK = "model.zip"
NAME_MODEL = "model.pkl"
NAME_BATCH = "model.bat"
CMD_OTA = PATH_OTA + "otapackager-cli"

@app.route('/pack', methods=['GET'])
def pack():
    try:
        # clean pervious package
        clean_pervious(PATH_MODEL, ".zip")
        clean_pervious(PATH_OTA, ".zip")
        clean_pervious(PATH_ROOT, ".zip")

        # chech if bat and pkl file exist or not
        if not os.path.isfile(PATH_MODEL + NAME_BATCH):
            return jsonify({STATUS_CODE:211}), 200
        if not os.path.isfile(PATH_MODEL + NAME_MODEL):
            return jsonify({STATUS_CODE:212}), 200

        # pack both pkl and bat
        # cannot setup equal input(-i) and dest(-d), therefore setup -d as PATH_OTA
        # will need move output file
        subprocess.call([CMD_OTA, 
                                 "-i", PATH_MODEL, 
                                 "-d", PATH_OTA,
                                 "-b", NAME_BATCH])

        # move file from PATH_OTA to PATH_MODEL
        test = os.listdir(PATH_OTA)
        for item in test:
            if item.endswith(".zip"):
                # remove ramdon number in file name
                #subprocess.call(["mv", PATH_OTA+item, PATH_MODEL+NAME_PACK])
                subprocess.call(["mv", PATH_OTA+item, PATH_MODEL+item])

        return jsonify({STATUS_CODE:200}), 200
    #except Exception, e: 
    #     print e
    #     return jsonify({STATUS_CODE:500}), 500
    except:
        return jsonify({STATUS_CODE:500}), 500


@app.route('/download', methods=['GET'])
def download():
    try:
        # if model.zip exists, return file to client
        if os.path.isfile(PATH_MODEL+NAME_PACK):
            return send_file(PATH_MODEL+NAME_PACK, attachment_filename=NAME_PACK)
        else:
            # file does not exists
            return jsonify({STATUS_CODE:211}), 400
    except:
        return jsonify({STATUS_CODE:500}), 500
    finally:
        clean_pervious(PATH_MODEL, ".zip")


@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        #file_path = request.form['file_path'] 
        file_path = PATH_MODEL

        # if file extension is allowable, clean pervious files and upload to PATH_MODEL 
        if file and allowed_file(file.filename):

            #clean pervious files
            clean_pervious(PATH_MODEL, file.filename.rsplit('.', 1)[1])
            #clean_pervious(PATH_MODEL, ".bat")

	    filename = os.path.join(file_path, file.filename)
            file.save(filename)

            return jsonify({STATUS_CODE:200}), 200
        else:
            return jsonify({STATUS_CODE:213}), 200
    except ValueError:
        return jsonify({STATUS_CODE:211}), 400
    except IOError:
        return jsonify({STATUS_CODE:212}), 400
    #except Exception, e: print e
    except :
	return jsonify({STATUS_CODE:500}), 500

def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def clean_pervious(dir_name=PATH_ROOT, extensions=".just_give_one"):
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(extensions):
            os.remove(os.path.join(dir_name, item))
    


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
