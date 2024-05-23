from dataclasses import dataclass


@dataclass
class KafkaAgcTelemetry:
    """
    Kafka接收遥测数据实体类
    """
    versionId: int  # 版本号
    dataId: int  # 数据编号
    agcId: int  # agc编码
    stationId: int  # 电场场站编码
    dataTime: int  # 时间
    dynamoPressureP: float  # AGC控制对象发电机对象有功功率
    pressureLower: float  # 当前风速下风场机组可调有功下限
    pressureUpper: float  # 当前风速下风场机组可调有功上限
    commandPressureP: float  # 有功功率调节指令
    commandReturn: float  # AGC指令返回值
    colobjPressureP: float  # AGC控制对象有功功率