import appdirs
import os

import urllib.request
import zipfile
import io
import shutil
import json
import hashlib
import textwrap

# from mockupgen.helpers import _b, _r, _g, _c, _m, _input_bool 
from .helpers import _b, _r, _g, _c, _m, _input_bool

TEMPLATES_URL = 'https://drive.rohanmenon.com/index.php/s/DFpB66WMxKp3YHy/download'
TEMPLATES_SHA256 = 'e0b5b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b'
TEMPLATES_SIZE = '127 MB'


def _app_template_dir():
    # Get the app data directory
    return os.path.join(appdirs.user_data_dir('mockupgen', 'mockupgen_testing'), 'templates')


def _download_templates():
    # Download the templates from the repo
    url = TEMPLATES_URL
    print()
    print(_b('Downloading ' + url))
    try:
        with urllib.request.urlopen(url) as response:
            hash = hashlib.sha256(response.read()).hexdigest()
            # if hash != EXPECTED_TEMPLATES_SHA256:
            #     print(_r('Hash mismatch'))
            #     exit(1)
            with zipfile.ZipFile(io.BytesIO(response.read())) as z:
                z.extractall(_app_template_dir())
                print(_g('Templates installed'))
    except Exception as e:
        print(e)
        print(_r('Failed to install templates'))
        exit(1)

def reset_templates():
    # Delete the template folder
    template_folder = _app_template_dir()
    if os.path.isdir(template_folder):
        shutil.rmtree(template_folder)
    print(_b('Reset template directory'))

def get_template_dir():
    template_dir = _app_template_dir()

    # Check if the folder has info.json
    if not os.path.isfile(template_dir + os.sep + 'info.json'):
        download_message = textwrap.dedent(f"""
        mockupgen does not come with any templates installed. You can install 
        the default templates, or you can specify your own template directory
        with the --custom-template-dir option.
        
        This will take about {TEMPLATES_SIZE} of space.
        """)
        print(download_message)
        decision = _input_bool(_m('Run first time setup and install default templates? (y/n): '))
        if decision:
            if not os.path.isdir(template_dir):
                os.makedirs(template_dir)
            _download_templates()
        else:
            exit(0)

    # Load the mockup info
    try:
        with open(template_dir + os.sep + 'info.json') as _:
            pass
    except Exception:
        print(_r('Template directory missing "info.json"'))
        print(_r('Consider resetting templates with --reset-templates'))

    return template_dir
