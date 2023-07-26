from diffusers import StableDiffusionPipeline
from PIL import Image


model_id = "CompVis/stable-diffusion-v1-5"
device = "cuda"


pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to(device)

def generate_img(prompt):
    return pipe(prompt).images[0]
