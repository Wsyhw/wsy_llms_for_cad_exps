from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)
import pandas as pd
from tqdm import tqdm
def get_a_small_json_data(pth_csv=r""):
    csv_data_now = pd.read_csv(pth_csv)
    len_min = 1000000
    lens = []
    l_dic = {}
    for index, row in tqdm(csv_data_now.iterrows()):
        data_now = row["text"].split("</s><s>Assistant: ")[1]
        l_now = len(data_now)
        # print(row["text"].split("</s><s>Assistant: ")[1])
        lens.append(l_now)
        l_dic[l_now] = data_now.replace("</s>", "")
    # print(min(lens), max(lens))
    l_test_data = l_dic[min(lens)]
    return l_test_data


if __name__ == "__main__":
    csv_data_pth_1 = r"/home/user/wsy_2024/llms/generate_data_wsy/data_for_sft_small.csv"
    data_for_tk = get_a_small_json_data(pth_csv=csv_data_pth_1)
    print(data_for_tk)
    ckpt_pth = r"/home/user/wsy_2024/llms/Llama2-Chinese/llama2-chinese"
    tokenizer = AutoTokenizer.from_pretrained(ckpt_pth)
    # inputs = tokenizer([data_for_tk], padding=False, truncation=True, return_tensors="pt")
    # print(inputs)
    # data_for_tk = "{'Fhogto1LShMOwqj_0': "
    inputs = tokenizer([data_for_tk], padding=False, truncation=True, return_tensors="pt")
    # print(inputs)
    input_id = inputs["input_ids"].numpy().tolist()
    # print(input_id)
    input_lis = input_id[0]
    for id_detoken in input_lis:
        print(id_detoken, ": ", tokenizer.decode([id_detoken]))
    # print(tokenizer.decode([11117]))
    # model = AutoModelForCausalLM.from_pretrained(ckpt_pth)
    # print(model)
    # print(tokenizer.vocab)
    # outputs = model(**inputs)
    # print(outputs)