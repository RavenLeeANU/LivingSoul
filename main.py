import _thread
import configparser
import asyncio
from liveapp import Application
live_config_path = 'live-config.ini'
sensitive_dict_path = 'sensitive_words.txt'

live_config = {}






if __name__ == '__main__':
    # 直播间建连
    app = Application(live_config_path)
    asyncio.run(app.launch())



