import configparser
from bliveclient import BLiveRoom


class Application:
    def __init__(self, path):
        self.config_path = path
        self.openai_key = ''
        self.openai_api_base = ''
        self.room_id = ''
        self.room_client = {}

    def init_config(self):
        con = configparser.ConfigParser()
        con.read(self.config_path, encoding='utf-8')
        live_config = dict(con.items('live'))

        self.room_id = live_config["room_id"]
        self.openai_key = live_config["secret_key"]
        self.openai_api_base = live_config["openai_api_base"]
        # print(live_config)


    async def blive_connect(self):
        self.room_client = BLiveRoom(self.room_id)
        await self.room_client.launch()


    async def launch(self):
        print("启动直播服务...")
        # 读取配置信息
        self.init_config()
        # 启动本地直播环境
        await self.blive_connect()
        # 检查GPT链接



        # 启动EasyVTuber

        # 执行循环操作