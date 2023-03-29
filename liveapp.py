import configparser
from bliveclient import BLiveRoom
from chatbot import ChatBot
from ttsclient import TTSClient
import time
import asyncio
import _thread
from queue import Queue, PriorityQueue
from pypinyin import lazy_pinyin
import os
import multiprocessing

from logger import Logger
import datetime
import uuid

class Application:
    def __init__(self, path):
        parser = configparser.ConfigParser()
        parser.read(path, encoding='utf-8')
        self.config = dict(parser.items('LSConfig'))

        self.logger = Logger(config=self.config)
        self.chat_bot = ChatBot(config=self.config)
        self.tts_client = TTSClient(config=self.config)
        self.room_client = BLiveRoom(config=self.config)

        self.context_message = []
        self.temp_message = []  # 最大3条上下文

    def chatting_loop(self):
        print("执行主播反馈")
        while True:
            chat_obj = {"name": '', "type": '', 'num': 0,
                        'action': '', 'msg': '', 'price': 0}
            try:
                result_obj = self.room_client.process_interaction(chat_obj)

            except Exception as e:
                print("-----------ErrorStart--------------")
                print(e)
                print("gpt获取弹幕异常，当前线程：")
                print(chat_obj)
                print("-----------ErrorEnd--------------")
                time.sleep(2)
            # print(chat_obj)
        #time.sleep(2)
        #result_obj = {'name': '沈晓曦', 'type': 'danmu', 'num': 1, 'action': '说', 'msg': '你好', 'price': 0}

            # 过滤队列
            if len(result_obj['name']) > 0:
                self.call_chatbot(result_obj)


    def call_chatbot(self, message):

        if self.config['env'] == 'dev':
            print('gpt当前进程id::' + str(os.getpid()))

        # 用户输入
        user_say = ''
        # 向 tts 写入的数据
        voice_message = ''

        if message['type'] == 'danmu':
            user_say = message['name'] + message['action'] + message['msg']
            voice_message = message['msg']
        elif message['type'] == 'sc':
            user_say = message['name'] + message['action'] + \
                         str(message['price']) + '块钱sc说' + message['msg']
            voice_message = user_say
        elif message['type'] == 'guard':
            guard_type = '舰长'
            if message['price'] > 200:
                guard_type = '提督'
            elif message['price'] > 2000:
                guard_type = '总督'
            user_say = message['name'] + message['action'] + \
                         guard_type + '了,花了' + str(message['price']) + '元'
            voice_message = message['name'] + message['action'] + guard_type + '了'
        elif message['type'] == 'gift':
            user_say = message['name'] + message['action'] + message['msg']
            voice_message = user_say
        else:
            user_say = message['msg']
            voice_message = user_say

        # 生成上下文
        self.temp_message.append({"role": "user", "content": user_say})
        # 上下文最大值
        if len(self.temp_message) > 3:
            del (self.temp_message[0])
        whole_message = self.chat_bot.role_info + self.temp_message

        # 开启 openai 和 tts 进程
        self.rec2tts(message, user_say, whole_message, voice_message)
        # p = multiprocessing.Process(target=self.rec2tts, args=(
        #     message, user_say, whole_message, voice_message))
        # p.start()
        # # join 会阻塞当前 gpt 循环线程，但不会阻塞弹幕线程
        # p.join()
        print("子进程退出")

    def rec2tts(self, msg, send_message, whole_message, voice_message):
        print("进入gtp&&tts进程，向gpt发送::" + send_message)
        self.logger.logger_xls(msg, send_message)
        #response_text = "你好"
        response_text = self.chat_bot.chat(whole_message)

        # 生成发送语音
        self.tts_client.generated_speech(voice_message, 'sendVits.wav')
        # 生成接收语音
        self.tts_client.generated_speech(response_text, 'recVits.wav')

        self.tts_client.playsound('output/sendVits.wav')

        # # 模拟键盘输入
        # p = multiprocessing.Process(
        #     target=write_keyboard_text, args=(responseText,))
        # p.start()
        # time.sleep(0.5)
        # 播放接受
        self.tts_client.playsound('output/recVits.wav')

        # 对话日志
        self.logger.logger_receive(response_text)

    # 监控队列的循环任务

    def launch(self):
        print("启动直播服务...")

        # self.tts_client.generated_speech("我是一个好人", 'sendVits.wav')

        # 直播网络建连
        blive_idx = _thread.start_new_thread(asyncio.get_event_loop(
        ).run_until_complete, (self.room_client.launch(),))

        # 启动本地处理
        core_idx = _thread.start_new_thread(self.chatting_loop(), ())