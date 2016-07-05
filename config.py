import os
import json
from gi.repository import GLib

def config_get_configuration_path ():
    return os.path.join (GLib.get_user_config_dir (), "lamaperia")

def config_get_configuration_filename ():
    return os.path.join (config_get_configuration_path (), "config.json")

def config_open_configuration_file_for_writing ():
    os.makedirs (config_get_configuration_path ())
    return open (config_get_configuration_filename (), 'w')

def config_load ():
    f = open (config_get_configuration_filename ())
    return json.load (f)
