import os
import shutil

# 源文件夹路径
source_folder = "C:/Users/root/Desktop/所有数据"
# 目标文件夹路径
destination_folder = "C:/Users/root/Desktop/部分数据"
# 指定要移动的文件名列表
files_to_move = ['datasource_config', 'consumed_power_district', 'district_info', 'electric_production_day_district',
                 'electric_production_day_station', 'electric_production_hour_district',
                 'electric_production_hour_station',
                 'electric_production_month_district', 'electric_production_month_station', 'entry_class_info',
                 'entry_info',
                 'holiday_config', 'holiday_type', 'manual_electric_data', 'manual_station_data',
                 'manuals_capacity_data',
                 'manuals_simultaneity_data', 'measured_cft_data', 'measured_power_district',
                 'measured_power_district_k_day',
                 'measured_power_k_day', 'measured_power_peak_record', 'measured_power_station',
                 'measured_power_summary_day',
                 'measured_theory_data', 'multiple_compare_record', 'power_filter_range_config',
                 'power_precision_alarm',
                 'short_term_predict_10t_k_day', 'short_term_predict_district', 'short_term_predict_district_10t',
                 'short_term_predict_district_10t_k_day', 'short_term_predict_station',
                 'short_term_predict_station_10t',
                 'simultaneity_rate_range_config', 'station_info', 'station_info_grid_change_day',
                 'station_info_grid_change_month',
                 'statistics_installed_quantity', 'storage_power_station', 'storage_station', 'sys_role_info',
                 'sys_user_info',
                 'system_operation_log', 'ultra_short_term_predict_10h_k_day', 'ultra_short_term_predict_district',
                 'ultra_short_term_predict_district_10h', 'ultra_short_term_predict_district_10h_k_day',
                 'ultra_short_term_predict_station', 'ultra_short_term_predict_station_10h', 'measured_power_k_hour',
                 'measured_power_district_k_hour', 'simultaneity_rate_k_hour', 'simultaneity_rate_district_k_hour',
                 'simultaneity_rate_k_day', 'simultaneity_rate_district_k_day', 'measured_power_work_k_day',
                 'measured_power_district_work_k_day', 'measured_power_k_week', 'measured_power_district_k_week',
                 'simultaneity_rate_k_week', 'simultaneity_rate_district_k_week', 'measured_power_k_month',
                 'measured_power_district_k_month', 'simultaneity_rate_k_month', 'simultaneity_rate_district_k_month',
                 'measured_power_k_quarter', 'measured_power_district_k_quarter', 'simultaneity_rate_k_quarter',
                 'simultaneity_rate_district_k_quarter', 'measured_power_k_year', 'measured_power_district_k_year',
                 'simultaneity_rate_k_year', 'simultaneity_rate_district_k_year', 'measured_character_district_day',
                 'simultaneity_character_district_day', 'warn_data']

# 确保目标文件夹存在，如果不存在则创建
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# 遍历文件名列表
for file_name in files_to_move:
    file_name = file_name + ".sql"
    # 源文件完整路径
    source_file = os.path.join(source_folder, file_name)
    # 目标文件完整路径
    destination_file = os.path.join(destination_folder, file_name)

    # 检查文件是否存在
    if os.path.exists(source_file):
        # 移动文件
        shutil.copy(source_file, destination_file)
        print(f"文件 {file_name} 已复制到 {destination_folder}")
    else:
        print(f"文件 {file_name} 不存在于源文件夹中。")

print("指定的文件已成功移动。")
