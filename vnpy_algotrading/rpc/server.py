import fastapi
from pydantic import BaseModel
from vnpy.rpc import RpcClient
from vnpy_webtrader import rpc_handler
from vnpy.trader.engine import MainEngine
from vnpy.event import EventEngine
from ..engine import (
    AlgoEngine,
    AlgoTemplate,
    APP_NAME,
    EVENT_ALGO_LOG,
    EVENT_ALGO_UPDATE,
    AlgoStatus,
    Direction,
    Offset,
)


class StartAlgoModel(BaseModel):
    template_name: str
    vt_symbol: str
    direction: str
    offset: str
    price: float
    volume: float
    interval: int
    time: int


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
        return self.algo_engine.get_algo_template()

    @rpc_handler("algo_start_algo")
    def start_algo(self, algo_data: StartAlgoModel):
        templates: List[AlgoTemplate] = self.algo_engine.get_algo_template()
        algo_template: AlgoTemplate = templates[algo_data.template_name]
        setting: dict = algo_template.default_setting
        setting.update(
            {
                "vt_symbol": algo_data.vt_symbol,
                "direction": algo_data.direction,
                "offset": algo_data.offset,
                "price": algo_data.price,
                "volume": algo_data.volume,
            }
        )

        self.algo_engine.start_algo(
            template_name=algo_data.template_name,
            vt_symbol=setting.pop("vt_symbol"),
            direction=Direction(setting.pop("direction")),
            offset=Offset(setting.pop("offset")),
            price=setting.pop("price"),
            volume=setting.pop("volume"),
            setting=setting,
        )

    @rpc_handler("algo_stop_all")
    def stop_all(self):
        self.algo_engine.stop_all()


class AlgoWebAPI(fastapi.APIRouter):
    def __init__(self, client: RpcClient) -> None:
        super().__init__(prefix=f"/{APP_NAME}")
        self.client = client

        self.register_routes()

    def register_routes(self):
        self.add_api_route("/ping", self.ping)
        self.add_api_route("/get_algo_template", self.get_algo_template)
        self.add_api_route("/start_algo", self.start_algo, methods=["POST"])
        self.add_api_route("/stop_all", self.stop_all, methods=["POST"])

    def ping(self):
        return f"{APP_NAME}: pong"

    def get_algo_template(self):
        templates = self.client.algo_get_algo_template() or {}
        return {
            "data": {
                "algo_template": [
                    {
                        "template_name": t.__name__,
                        "default_setting": t.default_setting,
                    }
                    for t in templates.values()
                ]
            },
            "error": None,
            "code": 0,
        }

    def start_algo(self, algo_data: StartAlgoModel):
        self.client.algo_start_algo(algo_data)
        return {
            "code": 0,
            "error": None,
        }

    def stop_all(self):
        self.client.algo_stop_all()
        return {
            "code": 0,
            "error": None,
        }
