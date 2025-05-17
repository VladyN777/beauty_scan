
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
import torch
import torchvision.transforms as transforms
from PIL import Image

app = FastAPI()

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Симуляция проверки оплаты
user_paid = set()

# Классы заболеваний
skin_classes = ["acne", "eczema", "psoriasis", "fungus", "healthy", "rosacea"]

# Модель ResNet34
model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet34', pretrained=True)
model.fc = torch.nn.Linear(model.fc.in_features, len(skin_classes))
model.eval()

# Преобразования изображения
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def predict_skin_disease(image_path):
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.nn.functional.softmax(outputs[0], dim=0)
        top3 = torch.topk(probs, 3)
        predictions = [(skin_classes[i], float(probs[i])) for i in top3.indices]
    return predictions

@app.post("/api/predict")
async def predict(file: UploadFile = File(...), request: Request = None):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user_ip = request.client.host if request else "anon"

    if user_ip not in user_paid:
        os.remove(file_location)
        return JSONResponse(content={"status": "needs_payment"})

    predictions = predict_skin_disease(file_location)
    diagnosis = predictions[0][0]
    os.remove(file_location)

    recommendations = [
        "Use gentle cleanser twice a day",
        "Avoid oily foods",
        "Consider using zinc-based cream"
    ]

    return JSONResponse(content={
        "status": "ok",
        "prediction": diagnosis,
        "top3": predictions,
        "recommendations": recommendations
    })

@app.get("/create-checkout-session")
def start_payment(request: Request):
    user_ip = request.client.host
    user_paid.add(user_ip)
    return RedirectResponse(url="/success")

@app.get("/success")
def payment_success():
    return JSONResponse(content={"message": "Оплата прошла. Вы можете получить результат."})

@app.get("/cancel")
def payment_cancel():
    return JSONResponse(content={"message": "Оплата отменена. Попробуйте снова."})
