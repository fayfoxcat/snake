from elasticsearch import Elasticsearch, helpers


es_config = {
    'url': ['http://172.18.37.193:22030'],
    'basic_auth': ('elastic', 'wiscom123')
}

es = Elasticsearch(es_config.get('url'), basic_auth=es_config.get('basic_auth'))

index_name = 'index_filerecord_202403'
scroll_time = '1m'
query = {
    "_source": False,
    "query": {
        "match_all": {}
    }
}

# 初始化滚动查询
response = es.search(index=index_name, body=query, scroll=scroll_time)
scroll_id = response['_scroll_id']
hits = response['hits']['hits']

# 收集所有以 _copy 结尾的 _id
ids_to_delete = [hit['_id'] for hit in hits if hit['_id'].endswith('_copy')]

while len(hits) > 0:
    response = es.scroll(scroll_id=scroll_id, scroll=scroll_time)
    scroll_id = response['_scroll_id']
    hits = response['hits']['hits']
    ids_to_delete.extend([hit['_id'] for hit in hits if hit['_id'].endswith('_copy')])

# 构建批量删除请求
actions = [
    { "_op_type": "delete", "_index": index_name, "_id": _id }
    for _id in ids_to_delete
]

# 批量删除文档
helpers.bulk(es, actions)
