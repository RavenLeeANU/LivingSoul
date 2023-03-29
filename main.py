import _thread
import configparser
import asyncio
from liveapp import Application
import time
live_config_path = 'liveconfig.ini'

if __name__ == '__main__':
    # 启动
    app = Application(live_config_path)
    app.launch()