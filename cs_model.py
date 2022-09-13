import torch
import sys
sys.path.append("..")
from models.experimental import attempt_load

device ='cuda' if torch.cuda.is_available() else 'cpu'
half =device !='cpu'


weights =r'../csgo0823.pt' #到时候更换
imgsz =640
def load_model():
    model = attempt_load(weights, map_location=device)
    if half:
        model.half()  # to FP16
    if device !='cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))

    return model
