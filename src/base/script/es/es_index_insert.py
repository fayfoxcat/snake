from elasticsearch import Elasticsearch

month_list = ["202312", "202401"]
# 创建 Elasticsearch 客户端
es = Elasticsearch(hosts=["http://elastic:123456@serve.asac.cc:9200/"])
header = {'Content-Type': 'application/json'}
# 创建流量索引
doc = {
    "settings": {
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 0,
            "sort.field": "collectedTime",
            "sort.order": "desc"
        },
        "index.store.preload": [
            "nvd",
            "dvd"
        ]
    },
    "mappings": {
        "properties": {
            "deviceId": {
                "type": "keyword"
            },
            "devicePortIndex": {
                "type": "keyword"
            },
            "collectedTime": {
                "type": "date"
            },
            "din": {
                "type": "long"
            },
            "dout": {
                "type": "long"
            },
            "dropIn": {
                "type": "long"
            },
            "dropout": {
                "type": "long"
            },
            "ifSpeed": {
                "type": "long"
            }
        }
    }
}
for month in month_list:
    for i in range(1, 51):
        index = 'index_porttraffic_' + str(i) + '_' + month
        res = es.indices.create(index=index, body=doc)
        print(index)

# 创建性能索引
doc1 = {
    "settings": {
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 0,
            "sort.field": "collectedTime",
            "sort.order": "desc"
        },
        "index.store.preload": [
            "nvd",
            "dvd"
        ]
    },
    "mappings": {
        "properties": {
            "deviceId": {
                "type": "long"
            },
            "collectedTime": {
                "type": "date"
            },
            "memory": {
                "type": "integer"
            },
            "cpu": {
                "type": "integer"
            },
            "fan": {
                "type": "integer"
            },
            "temp": {
                "type": "integer"
            },
            "power": {
                "type": "integer"
            },
            "fwConnNum": {
                "type": "integer"
            }
        }
    }
}
for month1 in month_list:
    index = 'index_performance_' + month1
    res2 = es.indices.create(index=index, body=doc1)
    print(index)