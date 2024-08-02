from typing import Union

from src.tools.config import Config
from src.tools.utils.request import get_api
from src.tools.basic.msg import PROMPT
from src.tools.basic.data_server import server_mapping

token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
bot_name = Config.bot_basic.bot_name_argument

async def serendipity_(server: str = None, name: str = None, group_id: str = None):  # 奇遇 <服务器> <ID>
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    final_url = f"{Config.jx3.api.url}/view/luck/adventure?token={token}&nickname={bot_name}&ticket={ticket}&server={server}&name={name}&chrome=1"
    data = await get_api(final_url)
    return data["data"]["url"]


# 近期奇遇 <服务器> [奇遇]
async def statistical_(server: str = None, serendipity: Union[str, None] = None, group_id: str = None):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    if serendipity is None:
        final_url = f"{Config.jx3.api.url}/view/luck/collect?token={token}&nickname={bot_name}&server={server}&chrome=1"
    else:
        final_url = f"{Config.jx3.api.url}/view/luck/statistical?token={token}&nickname={bot_name}&ticket={ticket}&server={server}&name={serendipity}&chrome=1"
    data = await get_api(final_url)
    return data["data"]["url"]


async def global_serendipity(name: str = None):  # 全服奇遇 [奇遇]
    if name is not None:
        final_url = f"{Config.jx3.api.url}/view/luck/server/adventure?name={name}&token={token}&nickname={bot_name}&chrome=1"
    data = await get_api(final_url)
    return data["data"]["url"]


async def global_statistical(name: str = None):  # 全服统计 [奇遇]
    if name is not None:
        final_url = f"{Config.jx3.api.url}/view/luck/server/statistical?name={name}&token={token}&nickname={bot_name}"
    data = await get_api(final_url)
    return data["data"]["url"]

async def get_preposition(name: str = None):
    url = "https://inkar-suki.codethink.cn/serendipity"
    data = await get_api(url)
    flag = False
    for i in data:
        if i["name"] == name:
            id = i["id"]
            flag = True
    if not flag:
        return False
    final_url = "https://jx3box.com/adventure/" + str(id)
    return f"【{name}】魔盒攻略：\n{final_url}"