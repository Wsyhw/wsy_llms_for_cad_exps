import json

with open("/home/hj2/wsy/deepcad/generate_data_wsy/alpaca_data.json", "r", encoding="utf-8") as f:
    content = json.load(f)
    print(len(content))
