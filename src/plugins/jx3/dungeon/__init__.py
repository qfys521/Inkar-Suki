from src.tools.dep.bot import *
from .api import *
from .xuanjin import *

zones = on_command("jx3_zones", aliases={"副本"}, priority=5)
@zones.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取玩家副本通关记录：

    Example：-副本 幽月轮 哭包猫@唯我独尊
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await zones.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await zones.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        id = arg[0]
    elif len(arg) ==2:
        server = arg[0]
        id = arg[1]
    data = await zone(server, id)
    if type(data) == type([]):
        await zones.finish(data[0])
    else:
        await zones.finish(ms.image(data))
