import time as sys_time
import random
import asyncio
from typing import Literal
from sgtpyutils.logger import logger
import bot
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message as obMessage
from nonebot.adapters.onebot.v11.event import Anonymous, Sender, Reply
from nonebot.adapters import Message
test_group_id = 11123456

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


class MessageCallback:
    '''
    class for overwrite none-bot message-sender
    '''

    def default_cb_finish(self, msg: str):
        assert False, self.to_warning(f'fail run:{msg}')

    def default_cb_send(self, msg: str):
        assert len(msg) > 10, self.to_warning(f'fail run by message too short:{msg}')

    def __init__(self, cb_finish: callable = None, cb_send: callable = None) -> None:
        self.cb_finish = cb_finish or self.default_cb_finish
        self.cb_send = cb_send or self.default_cb_send
        self.callback_counter = 0
        self.tag = 'default test'

    def check_counter(self):
        assert self.callback_counter, self.to_warning('no answer to tester till test completed')

    async def send(self, msg: str):
        self.callback_counter += 1
        if not self.cb_finish:
            logger.warning(self.to_warning('callback of send not set, but been called.'))
            return
        self.cb_send(msg)

    async def finish(self, msg: str):
        if not self.cb_finish:
            logger.warning(self.to_warning('callback of finish not set, but been called.'))
            return
        self.cb_finish(msg)
    def to_warning(self,warn:str):
        return f'[{self.tag}]{warn}'

class SFGroupMessageEvent(GroupMessageEvent):
    def build_user(self):
        return Sender(user_id=0, nickname='0', sec='男', age=0, card='0', area='0', level='0', role='user', title='0')

    def __init__(self, time: int = None, self_id: int = None, post_type: Literal['message'] = None, sub_type: str = None, user_id: int = None, message_type: Literal['group'] = None, message_id: int = None, message: Message = None, original_message: Message = None, raw_message: str = None, font: int = None, sender: Sender = None, to_me: bool = False, reply: Reply | None = None, group_id: int = None, anonymous: Anonymous | None = None):
        time = time or int(sys_time.time())
        self_id = self_id or '0'
        post_type = post_type or 'message'
        sub_type = sub_type or '0'
        user_id = user_id or '0'
        message_type = message_type or 'group'
        message_id = message_id or random.randrange(int(1e7), int(1e8))
        message = message or 'no message'
        original_message = original_message or message
        raw_message = raw_message or message
        font = font or 1
        sender = sender or self.build_user()
        to_me = to_me or True
        reply = reply or Reply(
            time=time, message_type=message_type, message_id=message_id, real_id=0, sender=sender, message=message)
        group_id = group_id or test_group_id
        group_id = group_id or 0
        super().__init__(time=time, self_id=self_id, post_type=post_type, sub_type=sub_type, user_id=user_id, message_type=message_type, message_id=message_id,
                         message=message, original_message=original_message, raw_message=raw_message, font=font, sender=sender, to_me=to_me, reply=reply, group_id=group_id, anonymous=anonymous)