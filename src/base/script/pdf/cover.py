data = [[{"inspect_name": "abc", "inspect_value": "22.2", "inspect_status": "1"}],
        [{"inspect_name": "abc", "inspect_value": "22.2", "inspect_status": "1"}]]


def cover():
    result = [[{
        "value": "表头",
        "background": "#A1C4E7",
        "alignment": 1,
        "size": 3,
        "bold": True
    }], [{
        "value": "第一列",
        "alignment": 1,
        "bold": True
    }, {
        "value": "第二列",
        "alignment": 1,
        "bold": True
    }, {
        "value": "第三列",
        "alignment": 1,
        "bold": True
    }]]
    for row in data:
        for item in row:
            items = []
            for key, value in item.items():
                items.append({
                    "value": value,
                    "alignment": 1,
                    "color": "#E55765" if value == "1" else "#1CD66C",
                    "bold": True
                })
            result.append(items)

    return result
