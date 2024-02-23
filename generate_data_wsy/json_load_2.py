import json 
import os  
from tqdm import tqdm
def read_json(pth=r"/home/hj2/wsy/deepcad/data/cad_json/0000/00000007.json"):
    with open(pth, "r") as json_file:
        data_now = json.load(json_file)
        
    return data_now


if __name__  == "__main__":
    L_GOOD_JSON = 5050
    data_all_dir_pth = r"/home/hj2/wsy/deepcad/data/cad_json"
    dir_name_list = sorted(os.listdir(data_all_dir_pth))
    for dir_name in dir_name_list:
        pth_dir_now = os.path.join(data_all_dir_pth, dir_name)
        json_names = sorted(os.listdir(pth_dir_now))
        num_good_jsons = 0
        for json_name in tqdm(json_names):
            if json_name.endswith(".json"):
                json_pth_now = os.path.join(pth_dir_now, json_name)
                data_json_now = read_json(pth=json_pth_now)
                data_str_json = str(data_json_now)
                l_json = len(data_str_json)
                
                if l_json <= L_GOOD_JSON:
                    num_good_jsons += 1
                    # print(l_json)
    print(num_good_jsons)
        







