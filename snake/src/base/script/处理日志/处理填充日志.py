import re

def process_log_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        log = file.read()

    # 提取SQL模板
    sql_template_pattern = re.compile(r"Preparing: (.+)")
    sql_template_match = sql_template_pattern.search(log)
    sql_template = sql_template_match.group(1) if sql_template_match else None

    # 如果没有找到SQL模板，输出提示信息并返回
    if sql_template is None:
        print("日志中未找到SQL模板。")
        return

    # 提取参数
    parameters_pattern = re.compile(r"Parameters: (.+)")
    parameters_match = parameters_pattern.search(log)
    parameters = parameters_match.group(1).split(", ") if parameters_match else []

    # 解析参数值
    parsed_parameters = []
    for param in parameters:
        value, param_type = param.rsplit("(", 1)
        value = value.strip()
        param_type = param_type.rstrip(")")
        if param_type in ["String", "Timestamp", "LocalDateTime"]:
            parsed_parameters.append(f"'{value}'")
        elif param_type in ["Long", "BigDecimal", "Integer"]:
            parsed_parameters.append(value)

    # 填充参数到SQL模板中
    for param in parsed_parameters:
        sql_template = sql_template.replace("?", param, 1)

    # 输出完整的SQL
    print(sql_template)

# 指定日志文件路径
log_file_path = 'log.log'
process_log_file(log_file_path)
