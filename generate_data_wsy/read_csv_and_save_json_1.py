import pandas as pd
import os 
from tqdm import tqdm
import json
import random 
# pth_one_file = r"/home/hj2/wsy/deepcad/generate_data_wsy/data_simple_prompt_1127_1032.csv"

# csv_data = pd.read_csv(pth_one_file)
# for index, row in csv_data.iterrows():
#     data_now = row["generated_prompt_with_step_all"]
#     json_pth = row["data_pth"]
#     print(data_now,json_pth, type(data_now))
TXT_FOR_CAD_BK = [
    "给定一段 CAD 建模描述，请帮我生成相应的建模代码。",
    "请根据所给的 CAD 建模描述生成对应的 CAD 代码。",
    "我会给你一段 CAD 建模的描述，请帮我生成一个对应的 CAD 模型。",
    "你是一个 CAD 建模专家，请根据我给你的建模描述生成对应"
]

def read_json(pth=r"/home/hj2/wsy/deepcad/data/cad_json/0000/00000007.json"):
    with open(pth, "r") as json_file:
        data_now = json.load(json_file)
    return data_now

def save_instruct(pth_csv=r""):
    list_data_now = []
    csv_data_now = pd.read_csv(pth_csv)
    str_text_prompt = """<s>Human: {}</s><s>Assistant: {}</s>"""
    text_input = """{}建模描述：{}"""
    for index, row in tqdm(csv_data_now.iterrows()):
        
        prompt_gen = row["generated_prompt_with_step_all"]
        json_pth = row["data_pth"]
        # print(prompt_gen)
        index_num = random.randint(0, 3)
        prompt_input = text_input.format(TXT_FOR_CAD_BK[index_num], prompt_gen)
        # print(prompt_input)
        data_json_now = read_json(pth=json_pth)
        data_str_json = str(data_json_now)
        prompt_final = str_text_prompt.format(prompt_input, data_str_json)
        # print(prompt_final)
        # print("\n=====================\n")
        # print("\n=====================\n")
        list_data_now.append(prompt_final)
        # print(data_now,json_pth, type(data_now))
    return list_data_now

if __name__ == "__main__":
    pth_data_dir = r"/home/hj2/wsy/deepcad/generate_data_wsy"
    file_names = os.listdir(pth_data_dir)
    list_all = []
    for file_name in file_names:
        str_names = file_name.split("_")
        print(str_names)
        if file_name.endswith(".csv") and ("simple" in str_names) and ("1102.csv" in str_names):
            csv_pth_used_now = os.path.join(pth_data_dir, file_name)
            print("now dealing with the file: {}\n".format(file_name))
            list_this_csv = save_instruct(pth_csv=csv_pth_used_now)
            list_all.extend(list_this_csv)
    print(len(list_all))
    data_for_csv = { 
        "text": list_all
    }
    
    df = pd.DataFrame(data_for_csv)
    df.to_csv('/home/hj2/wsy/deepcad/generate_data_wsy/data_for_sft_15k.csv', index=False)

