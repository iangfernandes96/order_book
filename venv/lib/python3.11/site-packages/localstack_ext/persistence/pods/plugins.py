from localstack.runtime import hooks
from localstack_ext import config as ext_config
@hooks.on_infra_start(should_load=ext_config.ACTIVATE_PRO)
def register_public_cloudpods_endpoints():from localstack.services.internal import get_internal_apis as A;from localstack.services.plugins import SERVICE_PLUGINS as B;from.endpoints import PublicPodsResource as C;from.manager import PodStateManager as D;A().add(C(D(B)))