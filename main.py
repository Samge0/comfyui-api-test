import json
import time
import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import urllib.request
import urllib.parse
import pandas as pd
from PIL import Image
from io import BytesIO

from datetime import datetime

from utils import u_file, u_gif, u_random

# define a function to send prompt messages to the server queue
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode("utf-8")
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

# define a function to retrieve images
def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

# define a function to retrieve history records
def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

# define a function to retrieve images which involves listening to web socket messages
def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)["prompt_id"]
    # print("prompt")
    # print(prompt)
    print("prompt_id: {}".format(prompt_id))
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    print("execution completed")
                    break 
        else:
            continue  # preview as binary data

    history = get_history(prompt_id)[prompt_id]
    print(history)
    for o in history["outputs"]:
        for node_id in history["outputs"]:
            node_output = history["outputs"][node_id]
            # image branch
            if "images" in node_output:
                images_output = []
                for image in node_output["images"]:
                    image_data = get_image(image["filename"], image["subfolder"], image["type"])
                    images_output.append(image_data)
                output_images[node_id] = images_output
            # video branch
            if "videos" in node_output:
                videos_output = []
                for video in node_output["videos"]:
                    video_data = get_image(video["filename"], video["subfolder"], video["type"])
                    videos_output.append(video_data)
                output_images[node_id] = videos_output

    print("image acquisition completed")
    print(output_images)
    return output_images

# parsing workflow and obtaining images
def parse_worflow(ws, prompt, seed, workflowfile):
    workflowfile = workflowfile
    with open(workflowfile, "r", encoding="utf-8") as workflow_api_txt2gif_file:
        prompt_data = json.load(workflow_api_txt2gif_file)
        # set text prompts
        prompt_data["18"]["inputs"]["text"] = prompt
        # set random seeds
        prompt_data["3"]["inputs"]["seed"] = seed
        prompt_data["17"]["inputs"]["seed"] = seed

        return get_images(ws, prompt_data)

# generate images and display them
def generate_clip(prompt, seed, workflowfile, idx):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = parse_worflow(ws, prompt, seed, workflowfile)

    for node_id in images:
        
        # get the current time and format it in YYYYMMDDHHMMSS format, 
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
        for image_data in images[node_id]:
            
            # [optional] you can choose to set different timestamps for different images
            # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # use formatted timestamps in file names
            save_path = "{}/{}_{}_{}".format(WORKING_DIR, idx, seed, timestamp)

            print("save_path: "+save_path)
            with Image.open(BytesIO(image_data)) as img:
                if img.is_animated:
                    if NEED_GIF:
                        u_gif.save_gif(img, save_path + ".gif")
                    else:
                        with open(save_path + ".webp", "wb") as binary_file:
                            binary_file.write(image_data)
                else:
                    img.convert('RGBA').save(save_path + ".png", 'PNG')

            print("{} DONE!!!".format(save_path))


# Example of reading from a CSV file
def read_prompts_from_csv(csv_file_path):
    df = pd.read_csv(csv_file_path)
    return df["prompt"].tolist()


# calling api to generate webp
def call_api(prompts):
    cache_file_idx = ".cache/idx.txt"
    last_record_idx = int(u_file.read(cache_file_idx) or 0)
    idx = last_record_idx
    for i in range(len(prompts)):
        if i < last_record_idx:
            continue
        prompt = prompts[i]
        seed = u_random.generate_random_number(15)
        print(i, " - processing: ", prompt, " - random seed: ", seed)
        generate_clip(prompt, seed, workflowfile, idx)
        idx += 1
        u_file.save(str(idx), cache_file_idx)
        break
    
    # execution completed reset
    u_file.save(str(0), cache_file_idx)



# Execute the main function
if __name__ == "__main__":
    
    # is it continuously generated in a loop
    NEED_LOOP = False
    
    # is output dynamic images in gif format. the default is webp format
    NEED_GIF = False
    
    # save directory for output images
    WORKING_DIR = ".cache/output"
    u_file.makedirs(WORKING_DIR)
    
    # comfyui workflowfile
    workflowfile = "workflow_api.json"
    
    # api address
    COMFYUI_ENDPOINT = "127.0.0.1:8188"
    server_address = COMFYUI_ENDPOINT
    
    # generate a unique client id
    client_id = str(uuid.uuid4())

    # reading the prompt list
    csv_file_path = "prompt.csv"
    prompts = read_prompts_from_csv(csv_file_path)
    
    while True:
        call_api(prompts)
        if not NEED_LOOP:
            break
        time.sleep(2)
        
    print("all done!")
    