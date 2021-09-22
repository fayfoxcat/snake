import json

import requests as requests

url = "https://statistis.mcmgsa.com/m_event/mobile/event"
data = json.dumps(
    'channel_code=web&event_name=get_download_url&user_identifier=1630421467694_0.9234560734&download_type=Android&app_code=apple')

# 测试网关限流
for i in range(99):
    result = requests.post(url, data)
    print(result.status_code)
