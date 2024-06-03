from .koromo import *

search_player = on_command("search_player", aliases={"mssp"}, priority=5, force_whitespace=True)

@search_player.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    data = await find_player(args.extract_plain_text())
    await search_player.finish(data)


generate_record = on_command("get_records", aliases={"msgr"}, priority=5, force_whitespace=True)

@generate_record.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    data = await get_records(args.extract_plain_text())
    if type(data) == type([]):
        img = get_content_local(data[0])
        await generate_record.finish(ms.image(img))
    else:
        await generate_record.finish(data)