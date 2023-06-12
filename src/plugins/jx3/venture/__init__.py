from src.tools.dep.bot import *
from .api import *

jx3_cmd_serendipity = on_command("jx3_serendipity", aliases={"奇遇"}, priority=5)


@jx3_cmd_serendipity.handle()
async def jx3_serendipity(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取个人奇遇记录：

    Example：-奇遇 幽月轮 哭包猫@唯我独尊
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        return await jx3_cmd_serendipity.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await serendipity_(server, id, group_id=event.group_id)
    if type(data) == type([]):
        return await jx3_cmd_serendipity.finish(data[0])
    else:
        return await jx3_cmd_serendipity.finish(ms.image(data))

jx3_cmd_statistical = on_command("jx3_lstatistical", aliases={"近期奇遇"}, priority=5)


@jx3_cmd_statistical.handle()
async def jx3_lstatistical(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取某服务器最近出奇遇的人的列表：

    Example：-近期奇遇 幽月轮 阴阳两界
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        return await jx3_cmd_statistical.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    data = await statistical_(server, serendipity=name, group_id=event.group_id)
    if type(data) == type([]):
        return await jx3_cmd_statistical.finish(data[0])
    else:
        return await jx3_cmd_statistical.finish(ms.image(data))

jx3_cmd_gserendipity = on_command("jx3_gserendipity", aliases={"全服奇遇"}, priority=5)


@jx3_cmd_gserendipity.handle()
async def jx3_gserendipity(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取全服最近某奇遇的触发列表，按触发顺序：

    Example：-全服奇遇 阴阳两界
    '''
    arg = args.extract_plain_text()
    if arg == "":
        return await jx3_cmd_gserendipity.finish("唔，缺少奇遇名称，没有办法找哦~")
    data = await global_serendipity(arg)
    if type(data) == type([]):
        return await jx3_cmd_gserendipity.finish(data[0])
    else:
        return await jx3_cmd_gserendipity.finish(ms.image(data))

jx3_cmd_gstatistical = on_command("jx3_gstatistical", aliases={"全服统计"}, priority=5)


@jx3_cmd_gstatistical.handle()
async def jx3_gstatistical(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取各服奇遇的触发者，统计图表：

    Example：-全服统计 阴阳两界
    '''
    arg = args.extract_plain_text()
    if arg == "":
        return await jx3_cmd_gstatistical.finish("唔，缺少奇遇名称，没有办法找哦~")
    data = await global_statistical(arg)
    if type(data) == type([]):
        return await jx3_cmd_gstatistical.finish(data[0])
    else:
        return await jx3_cmd_gstatistical.finish(ms.image(data))