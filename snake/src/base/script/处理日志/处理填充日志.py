import re

def process_log_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        log = file.read()

    # 提取SQL模板
    sql_template_pattern = re.compile(r"Preparing: (SELECT .+)")
    sql_template_match = sql_template_pattern.search(log)
    sql_template = sql_template_match.group(1) if sql_template_match else None

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
        if param_type == "String" or param_type == "Timestamp":
            parsed_parameters.append(f"'{value}'")
        elif param_type == "Integer":
            parsed_parameters.append(value)

    # 填充参数到SQL模板中
    for param in parsed_parameters:
        sql_template = sql_template.replace("?", param, 1)

    # 输出完整的SQL
    print(sql_template)

# 指定日志文件路径
log_file_path = 'log.log'
process_log_file(log_file_path)
