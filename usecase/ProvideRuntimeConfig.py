from model.ExecutionConfig import ExecutionConfig
from model.RuntimeConfig import RuntimeConfig
from network import PerformanceServerClient


def request_runtime_config_for(execution_config: ExecutionConfig) -> RuntimeConfig:
    symbols = [
        {
            "name": s.equity_name,
            "broker": s.broker_name,
            "type": s.type.value
        } for s in execution_config.symbols
    ]
    time_intervals = [t.value for t in execution_config.intervals]
    payload = {
        "strategy": execution_config.strategy.to_json(),
        "symbols": symbols,
        "timeIntervals": time_intervals
    }
    raw_config = PerformanceServerClient.request_runtime_config(payload)
    return RuntimeConfig.from_mongo_server_response(raw_config)


