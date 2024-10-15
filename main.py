import os

from dotenv import load_dotenv

from config import Config
from controller import Controller
from drivers.console.console import Console
from drivers.waveshare.waveshare import Waveshare

load_dotenv()

host = os.getenv('HOST')
if host is None:
    raise ValueError('HOST environment variable not set')
try:
    port = int(os.getenv('PORT'))
except ValueError:
    port = 8006
ssl = os.getenv('SSL') == 'true'
token = os.getenv('TOKEN')
if token is None:
    raise ValueError('TOKEN environment variable not set')
driver = os.getenv('DRIVER')
if driver is None:
    raise ValueError('DRIVER environment variable not set')
model = os.getenv('MODEL')
if driver == 'waveshare' and model is None:
    raise ValueError('MODEL is not set')

conf = Config(host, token, port, ssl, driver, model)

controller = Controller(conf)
match driver:
    case "waveshare":
        display = Waveshare(controller, model)
    case _:
        display = Console(controller)

controller.set_display(display=display)
display.initialize()