import openai
import json
import time
import os
from tqdm import tqdm
import pandas as pd

openai.api_key = "sk-rESXz6QCZoIEI9iS3jvHmlkZboyHaD4InPXWxjE5iB03vUtn"
openai.api_base = "https://api.chatanywhere.com.cn/v1"

BACKGROUND = """你是一个专业的 CAD 建模需求提供专家。
我将给你一段用 json 描述的某个 CAD 模型的建模步骤，你需要根据这个建模过程，用清晰、简洁的自然语言提供给我一段这个模型的需求描述。
注意：生成的回复直接给出描述，不要加上 '根据提供的 json 文件，这个 CAD 模型的建模需求描述如下：'
"""


def read_json(pth=r"/home/hj2/wsy/deepcad/data/cad_json/0000/00000007.json"):
    with open(pth, "r") as json_file:
        data_now = json.load(json_file)
    return data_now


def predict(params, bk=BACKGROUND):
    prompt, query = params
    prompt = prompt.format(query)
    # 请求返回结果
    # model：调用的模型名称，是一个字符串，用最新模型直接设置成 gpt-3.5-turbo
    # messages：请求的文本内容，是一个列表，列表里每个元素类型是字典
    # role:system：设置 gpt 人设。
    # role:assistant：表示 gpt。
    # role:user：表示用户。
    retry_count = 1
    retry_interval = 1
    for _ in range(retry_count):
        try:
            response = openai.ChatCompletion.create(
                # model="gpt-4",
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": bk},
                          {"role": "user", "content": prompt}],
                temperature=0
            )
            # 抽出 gpt 答复的内容
            msg = response.choices[0].message["content"].strip()
            return query, msg,

        except openai.error.RateLimitError as e:
            print("超出 openai api 调用频率：", e)
            print('重新请求....')
            retry_count += 1
            retry_interval *= 2  # 指数退避策略，每次重试后加倍重试间隔时间
            time.sleep(retry_interval)


        except TimeoutError:
            print("任务执行超时：", query)
            print('重新请求....')
            retry_count += 1
            retry_interval *= 2  # 指数退避策略，每次重试后加倍重试间隔时间
            time.sleep(retry_interval)

        except Exception as e:
            print("任务执行出错：", e)
            print('重新请求....')
            retry_count += 1
            retry_interval *= 2  # 指数退避策略，每次重试后加倍重试间隔时间
            time.sleep(retry_interval)

    return query, 'api 请求失败'


def generate_prompts_cad(pth_dir_all=r"/home/hj2/wsy/deepcad/data/cad_json", bk=BACKGROUND):
    prompt = """请根据以下 json 文件生成相应的建模描述:{}"""
    L_GOOD_JSON = 5050
    index_for_save = []
    name_for_save = []
    pth_for_save = []
    prompt_simple = []
    prompt_simple_step = []
    prompt_all_step = []
    dir_name_list = sorted(os.listdir(pth_dir_all))
    for dir_name in dir_name_list:
        pth_dir_now = os.path.join(pth_dir_all, dir_name)
        json_names = sorted(os.listdir(pth_dir_now))
        num_good_jsons = 1
        for json_name in tqdm(json_names):
            if json_name.endswith(".json"):
                json_num = int(json_name.replace(".json", ""))
                if json_num <= 6674:
                    continue
                json_pth_now = os.path.join(pth_dir_now, json_name)
                data_json_now = read_json(pth=json_pth_now)
                data_str_json = str(data_json_now)
                l_json = len(data_str_json)
                if l_json <= L_GOOD_JSON:
                    param_now = [prompt, data_json_now]
                    start_time = time.time()
                    num_not_return = 0
                    response = "api 请求失败"
                    while response == "api 请求失败":
                        if num_not_return >= 3:
                            return index_for_save, name_for_save, pth_for_save, prompt_simple, prompt_simple_step, prompt_all_step
                        question, response = predict(params=param_now, bk=bk)
                        num_not_return += 1
                    index_for_save.append(num_good_jsons)
                    name_for_save.append(json_name)
                    pth_for_save.append(json_pth_now)
                    prompt_simple.append(" ")
                    prompt_simple_step.append(" ")
                    prompt_all_step.append(response)
                    print(json_num, ": \n", response)
                    end_time = time.time()
                    num_good_jsons += 1
    return index_for_save, name_for_save, pth_for_save, prompt_simple, prompt_simple_step, prompt_all_step


if __name__ == "__main__":
    prompt_pth = r'/home/hj2/wsy/deepcad/generate_data_wsy/prompt_for_cad_generate_simple_1126.txt'
    with open(prompt_pth, 'r') as f:
        prompt_cad_background = f.read()
        print(prompt_cad_background, type(prompt_cad_background), len(prompt_cad_background))
        print("============================================================")
    data_all_dir_pth = r"/home/hj2/wsy/deepcad/data/cad_json"
    # prompt = """请根据以下 json 文件生成相应的建模描述:{}"""
    # json_pth_test = r"/home/hj2/wsy/deepcad/data/cad_json/0000/00000007.json"
    # data_json_test = read_json(pth=json_pth_test)
    # param_test = [prompt, data_json_test]
    # start_time = time.time()
    # question, response = predict(params=param_test, bk=prompt_cad_background)
    # print(response)
    # end_time = time.time()ß
    # total_run_time = round(end_time-start_time, 3)
    # print('Total_run_time_1_data: {} s'.format(total_run_time))
    index_for_save, name_for_save, pth_for_save, \
        prompt_simple, prompt_simple_step, prompt_all_step = generate_prompts_cad(pth_dir_all=data_all_dir_pth,
                                                                                  bk=prompt_cad_background)
    data_for_csv = {
        "index": index_for_save,
        "data_name": name_for_save,
        "data_pth": pth_for_save,
        "generated_prompt_simple": prompt_simple,
        "generated_prompt_with_step": prompt_simple_step,
        "generated_prompt_with_step_all": prompt_all_step
    }

    df = pd.DataFrame(data_for_csv)
    df.to_csv('/home/hj2/wsy/deepcad/generate_data_wsy/data_simple_prompt_1209_1102.csv', index=False)
