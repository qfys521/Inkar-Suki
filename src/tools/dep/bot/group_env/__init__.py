from __future__ import annotations
from sgtpyutils.database import filebase_database
from src.tools.utils import *


class GroupConfigInfo:
    name: str
    description: str
    default: any
    infos: dict[str, GroupConfigInfo]

    def __init__(self, name: str, description: str = None, default: any = None, infos: dict[str, GroupConfigInfo] = None) -> None:
        self.name = name
        self.description = description
        self.default = default
        self.infos = infos


groupConfigAuth: dict[str, GroupConfigInfo] = {
    'start': GroupConfigInfo('首次使用', default=DateTime('2024-01-08').timestamp()),
    'uses': GroupConfigInfo('使用记录', '记录每个授权区间', default=[]),
    'allow_server': GroupConfigInfo('可绑区服', '若无内容，则可任意绑定', default=[]),
    'allow_bot': GroupConfigInfo('可绑机器人', '若无内容，则可任意绑定', default=[]),
}

groupConfigInfos: dict[str, GroupConfigInfo] = {
    'auth': GroupConfigInfo('授权', default={}, infos=groupConfigAuth),
    'server': GroupConfigInfo('当前绑定服务器'),
    'bot': GroupConfigInfo('当前机器人'),
}


class GroupConfig:
    def __init__(self, group_id: str, config: str = 'jx3group') -> None:
        self.group_id = group_id
        self.config = config

        p = bot_path.get_group_config(group_id, config)
        self.value = filebase_database.Database(p).value

    def mgr_property(self, keys: list[str], new_val: any = Ellipsis) -> any:
        if isinstance(keys, str):
            keys = keys.split('.')  # 转为属性组
        data = self.value
        root = groupConfigInfos
        return self.enter_property(data, root, keys, new_val)

    def enter_property(self, data: dict, option: dict[str, GroupConfigInfo], keys: list[str], new_val: any = Ellipsis):
        cur = keys[0]
        keys = keys[1:]

        assert cur in option, f'配置项{cur}不存在'
        cur_opt = option.get(cur)

        cur_data = data.get(cur)
        if cur_data is None:
            cur_data = cur_opt.default

        if len(keys):
            assert cur_data is not None, 'data无下一级属性'
            assert isinstance(cur_data, dict), 'data非属性集合'
            next_options = cur_opt.infos
            assert next_options is not None, 'options无下一级属性'
            assert isinstance(next_options, dict), 'options非属性集合'
            return self.enter_property(cur_data, next_options, keys, new_val)

        if not new_val is Ellipsis:
            # 更新属性
            data[cur] = new_val
        return cur_data