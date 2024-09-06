# 在线DPS计算器 by 唐宋
# https://github.com/LynTss/jx3dps-online

from typing import Optional, Union, Literal, List, Any
from pydantic import BaseModel, Field

from src.tools.basic.server import server_mapping, Zone_mapping
from src.tools.basic.prompts import PROMPT
from src.tools.utils.time import get_current_time
from src.tools.utils.request import post_url
from src.tools.config import Config

from src.plugins.jx3.bind import get_player_local_data
from src.plugins.jx3.detail.detail import get_tuilan_data
from src.plugins.jx3.attributes.api import get_personal_kf, enchant_mapping

import json
import pydantic

inkarsuki_offical_token = Config.hidden.offcial_token

async def get_tuilan_raw_data(server: str, uid: str) -> dict:
    param = {
        "zone": Zone_mapping(server),
        "server": server,
        "game_role_id": uid
    }
    equip_data = await get_tuilan_data("https://m.pvp.xoyo.com/mine/equip/get-role-equip", param)
    return equip_data

async def get_local_data(server: Optional[str], name: str, group_id: Optional[str] = "") -> Union[dict, Literal[False]]:
    server = server_mapping(server, group_id)
    if not server:
        return False
    result = await get_player_local_data(role_name=name, server_name=server)
    if result.format_jx3api()["code"] != 200:
        return False
    return result.format_jx3api()["data"]

def server_required(func):
    def wrapper(self, *args, **kwargs):
        if not isinstance(self.server, str):
            return False
        return func(self, *args, **kwargs)
    return wrapper

def is_empty(value):
    if value is None:
        return True
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value == 0
    if isinstance(value, str):
        return value == ""
    if isinstance(value, list):
        if not value:
            return True
        return is_empty(value[0])
    if isinstance(value, dict):
        if not value:
            return True
        return all(is_empty(v) for v in value.values())
    return False

def check_key_empty(dictionary, key):
    if key not in dictionary:
        return True
    return is_empty(dictionary[key])

class ModifyType(BaseModel):
    name: str = ""
    max: str = ""
    min: str = ""
    desc: str = ""
    percent: bool = False

class FiveStone(BaseModel):
    name: str = ""
    level: str = ""
    max: str = ""
    min: str = ""
    icon: str = ""
    kind: str = ""
    subKind: str = ""
    desc: str = ""
    percent: bool = False

class _EquipType(BaseModel):
    Desc: str = ""
    EquipUsage: str = ""
    Icon: str = ""

class ColorStoneAttributes(BaseModel):
    max: str = ""
    min: str = ""
    desc: str = ""
    percent: bool = False

class ColorStone(BaseModel):
    id: str = ""
    name: str = ""
    class_name: str = Field("", alias="class")
    level: str = ""
    icon: str = ""
    kind: str = ""
    subKind: str = ""
    attribute: List[ColorStoneAttributes] = []

class PermanentEnchantAttributesDetail(BaseModel):
    desc: str = ""

class PermanentEnchantAttributes(BaseModel):
    max: str = ""
    min: str = ""
    attrib: List[PermanentEnchantAttributesDetail] = []

class PermanentEnchant(BaseModel):
    id: str = ""
    name: str = ""
    level: str = ""
    icon: str = ""
    attributes: List[PermanentEnchantAttributes] = []

class CommonEnchant(BaseModel):
    id: str = ""
    name: str = ""
    icon: str = ""
    desc: str = ""

class Equip(BaseModel):
    name: str = ""
    class_name: str = Field("", alias="class")
    icon: str = ""
    kind: str = ""
    subKind: str = ""
    quality: str = ""
    strengthLevel: str = ""
    maxStrengthLevel: str = ""
    color: str = ""
    desc: str = ""
    source: str = ""
    modifyType: List[ModifyType] = []
    fiveStone: List[FiveStone] = []
    EquipType: _EquipType = _EquipType()
    ID: str = ""
    UID: str = ""
    permanentEnchant: List[PermanentEnchant] = []
    commonEnchant: CommonEnchant = CommonEnchant()
    colorStone: ColorStone = ColorStone() # type: ignore

class JX3PlayerAttributes:
    def __init__(self, server: Optional[str], name: str, group_id: Optional[str] = "", tl_data: dict = {}):
        self.server = server_mapping(server, group_id)
        self.name = name
        self.tl_data: Optional[dict] = tl_data
        self.role_data: Optional[dict] = None

    @staticmethod
    async def get_kungfu(kungfu_id: str) -> Union[str, Literal[False]]:
        result = await get_personal_kf(kungfu_id)
        return result if result else False

    @staticmethod
    def convert_to_dict(obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            if pydantic.VERSION.startswith("1"):
                return obj.dict(by_alias=True)  # Pydantic v1
            else:
                return obj.model_dump(by_alias=True)  # Pydantic v2
        elif isinstance(obj, list):
            return [JX3PlayerAttributes.convert_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: JX3PlayerAttributes.convert_to_dict(v) for k, v in obj.items()}
        return obj

    @staticmethod
    def sort_equipments(equip_list: list) -> list:
        order = {
            "项链": 4,
            "腰坠": 3,
            "戒指": 2
        }

        def get_priority(item):
            sub_kind = item.get("subKind", "")
            return order.get(sub_kind, 0)

        weapons = [item for item in equip_list if item.get("kind") == "武器" and item.get("subKind") != "投掷囊"]
        pouches = [item for item in equip_list if item.get("class") == "投掷"]
        
        other_gears = [item for item in equip_list if item.get("kind") != "武器" and item.get("class") != "投掷"]
        
        last_four_gear_sorted = sorted(other_gears, key=lambda x: get_priority(x), reverse=True)
        
        final_last_four = last_four_gear_sorted[-4:]
        final_last_four.sort(key=lambda x: ["项链", "腰坠", "戒指"].index(x.get("subKind", "")) if x.get("subKind") in ["项链", "腰坠", "戒指"] else len(["项链", "腰坠", "戒指"]))
        
        remaining_gears = [item for item in last_four_gear_sorted if item not in final_last_four]
        
        sorted_data = weapons + pouches + remaining_gears + final_last_four
        
        return sorted_data

    async def _fetch_data(self):
        if not isinstance(self.server, str):
            return False
        role_data = await get_local_data(self.server, self.name)
        if not isinstance(role_data, dict):
            return False
        self.role_data = role_data
        return True

    async def analyze_equip_list(self) -> Union[list, Literal[False]]:
        if not self.tl_data:
            if not await self._fetch_data():
                return False
        
        if not isinstance(self.tl_data, dict) or len(self.tl_data["data"]["Equips"]) < 12:
            return False
        
        kungfu_id = self.tl_data["data"]["Kungfu"]["KungfuID"]
        if await self.get_kungfu(kungfu_id) in ["问水诀", "山居剑意"] and len(self.tl_data["data"]["Equips"]) != 13:
            return False

        equips = []
        for equip in self.tl_data["data"]["Equips"]:
            equip_data = Equip(
                name=equip["Name"],
                icon=equip["Icon"]["FileName"],
                kind=equip["Icon"]["Kind"],
                subKind=equip["Icon"]["SubKind"],
                quality=equip["Quality"],
                strengthLevel=equip["StrengthLevel"],
                maxStrengthLevel=equip["MaxEquipBoxStrengthLevel"],
                color=equip["Color"],
                desc=equip["Desc"],
                source="",  # 请问意义是什么？
                EquipType=_EquipType(**equip["EquipType"]),
                ID=equip["ID"],
                UID=equip["UID"],
                fiveStone=[
                    FiveStone(
                        name=item["Name"],
                        level=item["Level"],
                        max=item["Param1Max"],
                        min=item["Param1Min"],
                        icon=item["Icon"]["FileName"],
                        kind=item["Icon"]["Kind"],
                        subKind=item["Icon"]["SubKind"],
                        desc=item["Attrib"]["GeneratedMagic"],
                        percent=False
                    ) for item in equip["FiveStone"]
                ] if equip["Icon"]["SubKind"] != "戒指" else [],
                permanentEnchant=[
                    PermanentEnchant(
                        id=equip["WPermanentEnchant"]["ID"],
                        name=equip["WPermanentEnchant"]["Name"],
                        level=equip["WPermanentEnchant"]["Level"],
                        icon="",
                        attributes=[
                            PermanentEnchantAttributes(
                                max=equip["WPermanentEnchant"]["Attributes"][0]["Attribute1Value1"], 
                                min=equip["WPermanentEnchant"]["Attributes"][0]["Attribute1Value2"],
                                attrib=[
                                    PermanentEnchantAttributesDetail(
                                        desc=equip["WPermanentEnchant"]["Attributes"][0]["Attrib"]["GeneratedMagic"]
                                    )
                                ]
                            )
                        ]
                    )
                ] if "WPermanentEnchant" in equip else self.convert_to_dict(PermanentEnchant()),
                commonEnchant=CommonEnchant(
                    name=str(enchant_mapping(equip["Quality"])) + "·伤·" + "帽衣腰腕鞋"[["帽子", "上衣", "腰带", "护臂", "鞋"].index(equip["Icon"]["SubKind"])]
                ) if equip["Icon"]["SubKind"] in ["帽子", "上衣", "腰带", "护臂", "鞋"] else CommonEnchant(),
                colorStone=ColorStone(
                    id=equip["ColorStone"]["ID"],
                    name=equip["ColorStone"]["Name"],
                    level=equip["ColorStone"]["Level"],
                    icon=equip["ColorStone"]["Icon"]["FileName"],
                    kind=equip["ColorStone"]["Icon"]["Kind"],
                    subKind=equip["ColorStone"]["Icon"]["SubKind"],
                    attribute=[
                        ColorStoneAttributes(
                            max=item["Attribute1Value1"],
                            min=item["Attribute1Value2"],
                            desc=item["Attrib"]["GeneratedMagic"],
                            percent=False
                        ) for item in equip["ColorStone"]["Attributes"]
                    ],
                    **{"class": equip["ColorStone"]["Type"]}
                ) if equip["Icon"]["Kind"] == "武器" and equip["Icon"]["SubKind"] != "投掷囊" else ColorStone(), # type: ignore
                **{"class": equip["DetailType"]}
            )
            equips.append(self.convert_to_dict(equip_data))
        return self.sort_equipments(equips)

    async def get_panel(self) -> Union[dict, Literal[False]]:
        if not self.tl_data:
            if not await self._fetch_data():
                return False
        if isinstance(self.tl_data, dict):
            return {
                "score": self.tl_data["data"]["TotalEquipsScore"],
                "panel": self.tl_data["data"]["PersonalPanel"]
            }
        return False

    async def format_jx3api(self) -> Union[dict, Literal[False]]:
        if not self.role_data:
            if not await self._fetch_data():
                return False
        
        equip_data = await self.analyze_equip_list()
        if equip_data is False:
            return False
        
        role_data = self.role_data
        kungfu_name = await self.get_kungfu(self.tl_data["data"]["Kungfu"]["KungfuID"]) # type: ignore
        panel_data = await self.get_panel()
        for equip in equip_data:
            if equip["permanentEnchant"] == self.convert_to_dict(PermanentEnchant()):
                equip.pop("permanentEnchant")
            if equip["commonEnchant"] == CommonEnchant().__dict__:
                equip.pop("commonEnchant")
        return {
            "code": 200,
            "msg": "success",
            "data": {
                **role_data, # type: ignore
                "kungfuName": kungfu_name,
                "equipList": equip_data,
                "panelList": panel_data
            },
            "time": get_current_time()
        }
    
async def get_calculated_data(server: Optional[str], name: str, group_id: Optional[str] = "", school: str = "") -> Union[dict, Literal[False]]:
    server_ = server_mapping(server, group_id)
    if not isinstance(server_, str):
        return False
    player_info = await get_local_data(server, name, group_id)
    if not player_info:
        return False
    uid = player_info["roleId"]
    instance = JX3PlayerAttributes(
        server = server_,
        name = name,
        group_id = group_id,
        tl_data = await get_tuilan_raw_data(
            server = server_,
            uid = uid
        )
    )
    jx3api_format_data = await instance.format_jx3api()
    if not isinstance(jx3api_format_data, dict):
        return False
    if jx3api_format_data["data"]["kungfuName"] != school:
        return False
    data = await post_url(
        "https://inkar-suki.codethink.cn/calculator",
        headers = {"token": inkarsuki_offical_token},
        json = jx3api_format_data
    )
    print(data)
    return json.loads(data)