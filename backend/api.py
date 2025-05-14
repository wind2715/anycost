import os
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
from models.anycost_gan import Generator
from models.encoder import ResNet50Encoder
from models.dynamic_channel import set_uniform_channel_ratio, reset_generator

class AnyCoastAPI:
    def __init__(self, device='cuda'):
        self.device = device
        self.models_dir = '../models'
        
        # Tải model
        self.load_models()
        
        # Transform cho ảnh đầu vào
        self.transform = transforms.Compose([
            transforms.Resize(1024),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])
    
    def load_models(self):
        # Tải generator
        resolution = 1024
        channel_multiplier = 2
        
        generator_path = os.path.join(self.models_dir, 'generator.pt')
        self.generator = Generator(resolution, channel_multiplier=channel_multiplier).to(self.device)
        self.generator.load_state_dict(torch.load(generator_path, map_location=self.device))
        self.generator.eval()
        
        # Tải encoder
        encoder_path = os.path.join(self.models_dir, 'encoder.pt')
        n_style = 18
        style_dim = 512
        self.encoder = ResNet50Encoder(n_style=n_style, style_dim=style_dim).to(self.device)
        self.encoder.load_state_dict(torch.load(encoder_path, map_location=self.device))
        self.encoder.eval()
        
        # Tải boundaries
        boundaries_path = os.path.join(self.models_dir, 'boundaries.pt')
        self.boundaries = torch.load(boundaries_path, map_location=self.device)
    
    def encode_image(self, img_path):
        img = Image.open(img_path).convert('RGB')
        img = self.transform(img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            latent_code = self.encoder(img)
        
        return latent_code
    
    def generate_from_latent(self, latent_code, channel_ratio=1.0, target_res=1024):
        with torch.no_grad():
            if channel_ratio < 1.0:
                set_uniform_channel_ratio(self.generator, channel_ratio)
            
            if target_res < 1024:
                self.generator.target_res = target_res
            
            fake_img, _ = self.generator(latent_code, noise=None, randomize_noise=False, input_is_style=True)
            reset_generator(self.generator)
            
            # Chuyển đổi thành ảnh
            img = (fake_img.clamp(-1, 1) + 1) / 2
            img = img.detach().cpu().squeeze(0).permute(1, 2, 0).numpy()
            img = (img * 255).astype(np.uint8)
        
        return Image.fromarray(img)
    
    def edit_image(self, latent_code, direction_name, strength=1.0):
        if direction_name not in self.boundaries:
            raise ValueError(f"Direction {direction_name} not found")
        
        edit_direction = self.boundaries[direction_name].to(self.device)
        edited_latent = latent_code.clone()
        
        # Áp dụng cho 12 style đầu tiên
        edited_latent[:, :12] = edited_latent[:, :12] + edit_direction * strength
        
        return edited_latent
    
    def get_available_directions(self):
        return list(self.boundaries.keys())