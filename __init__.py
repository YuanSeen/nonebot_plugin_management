from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config
from .handle_group_application import group_request,group_increase_notice,group_decrease_notice
from .handle_intendant_application import add_intendant,delete_intendant,list_intendant,check_self
from .handle_banish_application import view_blacklist,clear_blacklist,remove_blacklist,kick

__plugin_meta__ = PluginMetadata(
    name="入群申请管理",
    description="处理入群申请，将申请信息发送到群内",
    usage="插件自动生效，无需手动调用",
    type="application",
    homepage="https://github.com/your-repo/nonebot-plugin-group-management",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

config = get_plugin_config(Config)
