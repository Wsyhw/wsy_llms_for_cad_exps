import os
import json
import openai
openai.api_key = "sk-qu4vRRWuePbfU188Rp0vyOdNe1w9smF1E9dcjm3dn7FlTs8c"
openai.api_base = "https://api.chatanywhere.com.cn/v1"
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import collections
# from prompts import prompts
BACKGROUND = """
你是一个专业的 CAD 建模需求提供专家。我将给你一段用 json 描述的某个 cad 模型的建模步骤，你需要根据这个建模过程，用清晰、简洁的自然语言提供给我一段这个模型的需求描述。

以下是一个示例：

提供的 json 描述 如下：
{
 "entities": {
  "Fg5Co82E19unP7q_0": {
   "name": "Extrude 1", 
   "type": "ExtrudeFeature", 
   "profiles": [
    {
     "profile": "JGC", 
     "sketch": "FQtakFubjNXh4U6_0"
    }
   ], 
   "extent_two": {
    "distance": {
     "type": "ModelParameter", 
     "role": "AgainstDistance", 
     "name": "none", 
     "value": 0.0
    }, 
    "type": "DistanceExtentDefinition", 
    "taper_angle": {
     "type": "ModelParameter", 
     "role": "Side2TaperAngle", 
     "name": "none", 
     "value": 0.0
    }
   }, 
   "extent_one": {
    "distance": {
     "type": "ModelParameter", 
     "role": "AlongDistance", 
     "name": "none", 
     "value": 0.005
    }, 
    "type": "DistanceExtentDefinition", 
    "taper_angle": {
     "type": "ModelParameter", 
     "role": "TaperAngle", 
     "name": "none", 
     "value": 0.0
    }
   }, 
   "operation": "NewBodyFeatureOperation", 
   "start_extent": {
    "type": "ProfilePlaneStartDefinition"
   }, 
   "extent_type": "OneSideFeatureExtentType"
  }, 
  "FQtakFubjNXh4U6_0": {
   "transform": {
    "origin": {
     "y": 0.0, 
     "x": 0.0, 
     "z": 0.0
    }, 
    "y_axis": {
     "y": 1.0, 
     "x": 0.0, 
     "z": 0.0
    }, 
    "x_axis": {
     "y": 0.0, 
     "x": 1.0, 
     "z": 0.0
    }, 
    "z_axis": {
     "y": 0.0, 
     "x": 0.0, 
     "z": 1.0
    }
   }, 
   "type": "Sketch", 
   "name": "Sketch 1", 
   "profiles": {
    "JGC": {
     "loops": [
      {
       "is_outer": true, 
       "profile_curves": [
        {
         "center_point": {
          "y": -0.00098815, 
          "x": 0.00043049, 
          "z": 0.0
         }, 
         "type": "Circle3D", 
         "radius": 0.039, 
         "curve": "JGB", 
         "normal": {
          "y": 0.0, 
          "x": 0.0, 
          "z": 1.0
         }
        }
       ]
      }
     ], 
     "properties": {}
    }
   }, 
   "reference_plane": {}
  }
 }, 
 "properties": {
  "bounding_box": {
   "max_point": {
    "y": 0.03801185184717178, 
    "x": 0.03943049454689026, 
    "z": 0.005
   }, 
   "type": "BoundingBox3D", 
   "min_point": {
    "y": -0.039988148152828216, 
    "x": -0.03856950545310974, 
    "z": 0.0
   }
  }
 }, 
 "sequence": [
  {
   "index": 0, 
   "type": "Sketch", 
   "entity": "FQtakFubjNXh4U6_0"
  }, 
  {
   "index": 1, 
   "type": "ExtrudeFeature", 
   "entity": "Fg5Co82E19unP7q_0"
  }
 ]
}

这段 json 对应的建模需求为：请创建一个半径为 39mm，高度为 5mm 的圆柱体


后续我将给你其他的 json，请按照上述的对应关系生成相应的建模需求

"""
def predict(params):
    prompt, query = params
    prompt = prompt.format(query[1])

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
                model="gpt-3.5-turbo-16k",
                messages=[{"role": "system", "content": BACKGROUND},
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
            retry_interval *= 2 # 指数退避策略，每次重试后加倍重试间隔时间
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

    return query,'api 请求失败'

def generate_answers(input_data_get=[]):
    start_time = time.time()
    # 多进程并行预测
    # 您可能需要根据自己的需求调整间隔时间。另外，您可以根据需要调整进程池的大小，以获得更好的性能。
    prompt = """{}"""
    # input_data = input_data_get
    # output_data = []
    index_input_data = 10
    save_list = []
    index = 1
    while index_input_data < len(input_data_get):
        if index >= 3:
            break
        input_data_now = input_data_get[: index_input_data]
        index_input_data += 10
    # output_data = collections.defaultdict(int)
        with ProcessPoolExecutor(max_workers=2) as executor:
            ## 同步调用.submit 之后直接.result（一个进程执行完才能下一个进程）
            # output_data = [executor.submit(predict, prompt.format(query)).result() for query in input_data]

            # # 异步调用（多进程并发执行）
            # futures = [executor.submit(predict, prompt.format(query)) for query in input_data]
            # query2res = collections.defaultdict(int)
            # # 同步等待结果（返回顺序和原数据顺序一致）
            # for job in futures:
            #     query, res = job.result(timeout=None)  # 默认 timeout=None，不限时间等待结果
            #     query2res[query] = res
            #
            #     time.sleep(1)  # 为了避免超过 OpenAI API 的速率限制，每次预测之间间隔 1 秒


            # 异步调用（多进程并发执行）
            futures = [executor.submit(predict, (prompt, query)) for query in input_data_now]
            query2res = collections.defaultdict(int) # 因为异步等待结果，返回的顺序是不定的，所以记录一下进程和输入数据的对应
            # 异步等待结果（返回顺序和原数据顺序可能不一致） ，直接 predict 函数里返回结果？
            i = 0
            for job in as_completed(futures):
                query,res = job.result(timeout=None)  # 默认 timeout=None，不限时间等待结果
                query2res[query[0]] = res
                dic_saved_json = {}
                dic_saved_json['instruction'] = "请根据输入的建模需求生成对应的 cad 建模步骤"
                dic_saved_json["input"] = res
                dic_saved_json["output"] = query[1]
                save_list.append(dic_saved_json)
                i += 1
                time.sleep(10)  # 为了避免超过 OpenAI API 的速率限制，每次预测之间间隔 1 秒



        end_time = time.time()
        total_run_time = round(end_time-start_time, 3)
        print('Total_run_time_10_datas: {} s'.format(total_run_time))
        print(query2res)
        index += 1
    return save_list
    

if __name__ == "__main__":
    json_dir_pth = r"/home/hj2/wsy/deepcad/data/cad_json/0000/"
    DATA_JSON_LIST = []
    json_names = os.listdir(json_dir_pth)
    i = 0
    for one_name in json_names:
        # if i >= 1:
        #     break
        list_one_json = []
        path_json_now = os.path.join(json_dir_pth, one_name)
        list_one_json.append(one_name)
        with open(path_json_now, 'r') as fp:
            data = json.load(fp)
            # for key, values in data.items():
            #     print(key)
            # print(len(data["entities"]))
            entities = data["entities"]
            if len(entities) <= 2:
                # print(one_name)
                # print(data)
                # print("=======================")
                list_one_json.append(data)
                DATA_JSON_LIST.append(list_one_json)
        i += 1
    final_saved_list = generate_answers(input_data_get=DATA_JSON_LIST)
    print(len(final_saved_list))
    print(final_saved_list)
    with open('/home/hj2/wsy/deepcad/generate_data_wsy/saved_instruct_data.json', 'w') as file:
        json.dump(final_saved_list, file, indent=4)
