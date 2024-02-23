import pandas as pd
import json
# data = {'index': [0, 1, 2], 'name': ['Tom', 'Jerry', 'Alice'], 'age': [25, 26, 24], 'sex': ['M', 'M', 'F']}

# df = pd.DataFrame(data)

# df.to_csv('/home/hj2/wsy/deepcad/generate_data_wsy/data.csv', index=False)


# pth_csv = r"llm_1/Llama2-Chinese/data/dev_sft.csv"

# csv_data = pd.read_csv(pth_csv)
# for index, row in csv_data.iterrows():
#     print(row["text"])
#     print("\n===========================\n")
def read_json(pth=r"/home/hj2/wsy/deepcad/data/cad_json/0000/00000007.json"):
    with open(pth, "r") as json_file:
        data_now = json.load(json_file)
    return data_now
str_text_prompt = """<s>Human: {}</s><s>Assistant: {}</s>"""
text_input = "给定一段CAD建模描述, 请帮我生成相应的建模代码. \
建模描述: 创建一个半径11.488mm，高25.4mm的圆柱体"
json_pth = r"/home/hj2/wsy/deepcad/data/cad_json/0000/00000392.json"
data_json_now = read_json(pth=json_pth)
data_str_json = str(data_json_now)
prompt_final = str_text_prompt.format(text_input, data_str_json)
print(prompt_final)
