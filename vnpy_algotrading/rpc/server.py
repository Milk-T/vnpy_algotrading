import fastapi
from vnpy.rpc import RpcClient
from vnpy_webtrader import rpc_handler
from vnpy.trader.engine import MainEngine
from vnpy.event import EventEngine

from ..engine import (
    APP_NAME,
)


class AlgoRpcServer:
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine
        self.algo_engine: AlgoEngine = main_engine.get_engine(APP_NAME)

        self.algo_engine.init_engine()

    @rpc_handler("algo_get_algo_template")
    def get_algo_template(self):
        return [t for t in self.algo_engine.get_algo_template()]

    @rpc_handler("algo_start_algo")
    def start_algo(self):
        self.algo_engine.start_algo()



class AlgoWebAPI(fastapi.APIRouter):
    def __init__(self, client: RpcClient) -> None:
        super().__init__(prefix=f"/{APP_NAME}")
        self.client = client

        self.register_routes()

    def register_routes(self):
        self.add_api_route("/ping", self.ping)
        self.add_api_route("/get_algo_template", self.get_algo_template)

    def ping(self):
        return f"{APP_NAME}: pong"

    def get_algo_template(self):
        return self.client.algo_get_algo_template()