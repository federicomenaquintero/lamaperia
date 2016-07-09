import os
import json
import unittest
from unittest.mock import patch
import config

def question (string, default=None):
    """
    If question ends with '?' make a yes/no question
    else return the user given value
    """
    if string.endswith ('?'):
        answ = input (string + ' [Y/n] ').lower ()
        if answ:
            return answ.startswith ('y')
        else:
            return default == 'y' or default == None
    else:
        if default:
            answ = input ('{} [{}]'.format (string, default))
        else:
            answ = input (string + ' ')
        return answ if answ else default

def config_wizard ():
    """
    Ensures the existence of .mkmaprc
    """
    if question ('Use TileStache?'):
        data = {
            'provider'        : 'TileStache',
            'tilestache_host' : question ('tilestache host:', '127.0.0.1'),
            'tilestache_port' : question ('tilestache port:', '8080'),
        }
    else:
        data = {
            'provider'            : 'Mapbox',
            'mapbox_access_token' : question ('mapbox access token:', 'pk.eyJ1IjoiZmVkZXJpY29tZW5hcXVpbnRlcm8iLCJhIjoiUEZBcTFXQSJ9.o19HFGnk0t3FgitV7wMZfQ'),
            'mapbox_username'     : question ('mapbox username:', 'federicomenaquintero'),
            'mapbox_style_id'     : question ('mapbox style id:', 'cil44s8ep000c9jm18x074iwv'),
        }

    json.dump (data, config.config_open_configuration_file_for_writing ())

    return data

#================ Tests =============

class TestWizard (unittest.TestCase):

    @patch ('builtins.input', return_value='')
    def test_question_default (self, mock):
        self.assertTrue (question ('q?'))

    @patch ('builtins.input', return_value='')
    def test_question_default_no (self, mock):
        self.assertTrue (not question ('q?', 'n'))

    @patch ('builtins.input', return_value='n')
    def test_question_no (self, mock):
        self.assertTrue (not question ('q?'))

    @patch ('builtins.input', return_value='foo')
    def test_question_string (self, mock):
        self.assertEqual (question ('q:', 'var'), 'foo')

    @patch ('builtins.input', return_value='')
    def test_question_string_withdefault (self, mock):
        self.assertEqual (question ('q:', 'var'), 'var')
