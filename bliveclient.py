import blivedm.blivedm as blivedm
import random
from queue import Queue, PriorityQueue
import asyncio
import json
import requests


# 最优先队列、sc、礼物、弹幕队列
topQue = Queue(maxsize=0)
# sc 队列
scQue = PriorityQueue(maxsize=0)
# 舰长队列
guardQue = PriorityQueue(maxsize=0)
# 礼物
giftQue = PriorityQueue(maxsize=5)
# 普通弹幕队列
danmuQue = PriorityQueue(maxsize=10)


class BLiveRoom :
    def __init__(self, config):
        self.room_id = config["room_id"]
        self.handler = MyHandler(self.room_id)
        self.is_finish_living = False
        self.client = blivedm.BLiveClient(self.room_id, ssl=True)


    async def check_is_finish(self):
        while not self.is_finish_living:
            continue

    async def launch(self):
        handler = MyHandler(self.room_id)
        self.client.add_handler(handler)
        self.client.start()
        waiting = asyncio.sleep(float('inf'))
        try:
            await waiting
            self.client.stop()
            await self.client.join()
        except asyncio.CancelledError:
            print('链接被中断')
        finally:
            await self.client.stop_and_close()
        print('直播链接中断')

    async def stop(self):
        try:
            self.client.stop()
            await self.client.join()
        finally:
            await self.client.stop_and_close()

    def process_interaction(self,chat_obj):
        # 从队列获取信息

        if not topQue.empty():
            chat_obj = topQue.get(True, 1)
        elif not guardQue.empty():
            chat_obj = guardQue.get(True, 1)
            chat_obj = chat_obj[1]
        elif not giftQue.empty():
            chat_obj = giftQue.get(True, 1)
            chat_obj = chat_obj[1]
        elif not scQue.empty():
            chat_obj = scQue.get(True, 1)
            chat_obj = chat_obj[1]
        elif not danmuQue.empty():
            chat_obj = danmuQue.get(True, 1)
            chat_obj = chat_obj[1]

        return chat_obj

class MyHandler(blivedm.BaseHandler):

    def __init__(self, room_id):
        super().__init__()
        self.room_id = room_id

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        if message.dm_type == 0:
            # print(f'弹幕：[{client.room_id}] {message.uname}：{message.msg}')
            # 权重计算
            guardLevel = message.privilege_type
            if guardLevel == 0:
                guardLevel = 0
            elif guardLevel == 3:
                guardLevel = 200
            elif guardLevel == 2:
                guardLevel = 2000
            elif guardLevel == 1:
                guardLevel = 20000
            # 舰长权重，勋章id权重*100，lv权重*100
            medalevel = 0
            if message.medal_room_id == self.room_id:
                medalevel = message.medal_level * 100
            rank = (999999 - message.user_level * 100 -
                    guardLevel - medalevel - message.user_level * 10 + random.random())
            if danmuQue.full():
                try:
                    danmuQue.get(True, 1)
                except:
                    print("on_danmuku时，get异常")

            queData = {'name': message.uname, 'type': 'danmu', 'num': 1, 'action': '说',
                       'msg': message.msg.replace('[', '').replace(']', ''), 'price': 0}

            print("前弹幕队列容量：" + str(danmuQue.qsize()))
            print("rank:" + str(rank) + ";name:" + message.uname + ";msg:" +
                  message.msg.replace('[', '').replace(']', ''))
            print(queData)
            try:
                danmuQue.put((rank, queData), True, 2)
            except Exception as e:
                print("ErrorStart-------------------------")
                print(e)
                print("put弹幕队列异常")
                print(queData)
                print("错误" + str(danmuQue.full()))
                print("错误" + str(danmuQue.empty()))
                print("后弹幕队列容量：" + str(danmuQue.qsize()))
                print("ErrorEnd-------------------------")

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        if message.coin_type == 'gold':
            print(f'礼物：：[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
                  f' （{message.coin_type}瓜子x{message.total_coin}）')
            price = message.total_coin / 1000
            if giftQue.full():
                giftQue.get(False, 1)
            if price > 1:
                queData = {"name": message.uname, "type": 'gift', 'num': message.num,
                           'action': message.action, 'msg': message.gift_name, 'price': price}
                giftQue.put((999999 - price + random.random(), queData), True, 1)

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'上舰：：[{client.room_id}] {message.username} 购买{message.gift_name}')
        queData = {"name": message.username, "type": 'guard', 'num': 1,
                   'action': '上', 'msg': '-1', 'price': message.price / 1000}
        guardQue.put((message.guard_level + random.random(), queData))

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        print(
            f'SC：：[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')
        # 名称、类型、数量、动作、消息、价格
        queData = {"name": message.uname, "type": 'sc', 'num': 1,
                   'action': '发送', 'msg': message.message, 'price': message.price}
        scQue.put((999999 - message.price + random.random(), queData))