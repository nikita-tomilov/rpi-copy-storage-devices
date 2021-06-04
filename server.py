#!/usr/bin/env python3
import base64
import io
from pathlib import Path

from PIL import Image
from flask import Flask, send_from_directory, send_file, redirect
from flask import render_template

import copier
from copier import show_devices

app = Flask(__name__, template_folder="./template/")


def b64encode(str):
    return base64.b64encode(str.encode('utf-8')).decode('utf-8').replace("/", ",")


def base64decode(str):
    return base64.b64decode(str.replace(",", "/").encode('utf-8')).decode('utf-8')


@app.route('/')
def show_list():
    devices = show_devices()
    devices_to_show = []
    for device in devices:
        if "mount" in device:
            link = b64encode(device["mount"])
            device_data_with_link = {"name": device["name"], "size": device["size"], "mount": device["mount"],
                                     "link": link}
        else:
            device_data_with_link = {"name": device["name"], "size": device["size"]}
        devices_to_show.append(device_data_with_link)
    return render_template('index.html', devices_count=len(devices_to_show), devices=devices_to_show,
                           last_executed_command=copier.last_executed_command,
                           last_executed_command_response=copier.last_executed_command_response,
                           last_executed_command_errcode=copier.last_executed_command_errcode)


@app.route('/ls/<encpath>')
def show_ls(encpath):
    path = base64decode(encpath)
    folders, files = copier.ls(path)
    folders_to_show = []
    files_to_show = []
    for folder in folders:
        folder_ext = {"name": folder, "link": "/ls/" + b64encode(path + "/" + folder)}
        folders_to_show.append(folder_ext)
    for file in files:
        file_url = "/download/" + b64encode(path + "/" + file) + "/" + file
        if file.lower().endswith("jpg"):
            thumb_url = "/thumbnail/" + b64encode(path + "/" + file)
            file_ext = {"name": file, "link": file_url, "thumbnail": thumb_url}
        else:
            file_ext = {"name": file, "link": file_url}
        files_to_show.append(file_ext)
    up_link = "/ls/" + b64encode(str(Path(path).parent.absolute()))
    return render_template('file.html', path=path, folders_count=len(folders), folders=folders_to_show,
                           files_count=len(files), files=files_to_show, up_link=up_link)


@app.route('/thumbnail/<encpath>')
def thumbnail(encpath):
    source_path = base64decode(encpath)
    filename = source_path.split("/")[-1]

    img = Image.open(source_path)
    basewidth = 128
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img.thumbnail((basewidth, hsize), Image.ANTIALIAS)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, "JPEG")
    img_byte_arr = img_byte_arr.getvalue()
    return send_file(io.BytesIO(img_byte_arr), attachment_filename=filename, mimetype='image/jpg')


@app.route('/static/<file>')
def static_file(file):
    # vulnerability here, do not use this on servers
    return send_from_directory("./template/", file)


@app.route('/mount/<dev>')
def do_mount(dev):
    copier.mount(dev)
    return redirect("/", code=302)


@app.route('/unmount/<dev>')
def do_unmount(dev):
    copier.unmount(dev)
    return redirect("/", code=302)


@app.route('/download/<encpath>/<rawfilename>')
def download(encpath, rawfilename):
    path = base64decode(encpath)
    filename = path.split("/")[-1]
    if filename != rawfilename:
        return "error: provided mixed filenames " + filename + " and " + rawfilename
    root_dir = str(Path(path).parent.absolute())
    # vulnerability here, do not use this on servers
    return send_from_directory(root_dir, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
