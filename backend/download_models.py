import os
import requests
from tqdm import tqdm

MODEL_URLS = {
    "generator": "https://hanlab18.mit.edu/projects/anycost-gan/files/generator_anycost-ffhq-config-f.pt",
    "encoder": "https://hanlab18.mit.edu/projects/anycost-gan/files/encoder_anycost-ffhq-config-f.pt",
    "boundaries": "https://hanlab18.mit.edu/projects/anycost-gan/files/boundaries_anycost-ffhq-config-f.pt"
}

def download_file(url, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    
    print(f"Downloading {filepath}")
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
    
    with open(filepath, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    
    progress_bar.close()

def download_models():
    for name, url in MODEL_URLS.items():
        filepath = f"../models/{name}.pt"
        if not os.path.exists(filepath):
            download_file(url, filepath)
        else:
            print(f"{filepath} already exists")

if __name__ == "__main__":
    download_models()