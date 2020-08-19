import os
import json
import cfg
from copy import deepcopy

default_config = {"main_font_size": 11,
                  "title_font_size": 20,
                  "is_autoinput_last": False,
                  "autoinput_text": "",
                  "autoinput_last": "",
                  "is_autoreload": False,
                  "autoreload_timeout": 600}

config = None


def load_config():
    print("Loading config file from", cfg.CONFIG_LOCATION)
    try:
        return json.load(open(cfg.CONFIG_LOCATION))
    except json.decoder.JSONDecodeError:
        print("Your config file is corrupted")
        return reset_config()


def reset_config():
    print("Defaulting config")
    return deepcopy(default_config)


def save_config():
    location = cfg.CONFIG_LOCATION
    print("Saving config file to", location)
    dirlocation = os.path.dirname(location)
    if not os.path.exists(dirlocation):
        os.makedirs(dirlocation)
    json.dump(config, open(location, 'w'))


if os.path.exists(cfg.CONFIG_LOCATION):
    config = load_config()
else:
    config = reset_config()


save_config()
