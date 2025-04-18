from dataclasses import dataclass


@dataclass
class KafkaAgcTelemetry:
    """
    Kafka接收遥测数据实体类
    """
    devId: str  # nplcId 编码
    dataId: int  # 数据编号
    dataTime: int  # 时间
    lower: float  # 当前风速下风场机组可调有功下限
    upper: float  # 当前风速下风场机组可调有功上限
    gen: float  # AGC控制对象有功功率
    pulse: float  # 有功功率调节指令
    version: int  # 版本号
