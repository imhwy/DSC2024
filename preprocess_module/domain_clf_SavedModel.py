import re
import string
import torch
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from torch.utils.data import Dataset

# Set device
device = "cuda:0" if torch.cuda.is_available() else "cpu"

def preprocessing_text(text):
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = re.sub("\s+", " ", text).strip()
    return text

class CustomDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def make_prediction(review, tokenizer, model):
    demo_input = preprocessing_text(review)
    demo_encodings = tokenizer([demo_input], truncation=True, max_length=512, padding=True, return_tensors="pt")
    
    with torch.no_grad():
        model.eval()
        outputs = model(**{key: val.to(device) for key, val in demo_encodings.items()})
        predictions = outputs.logits
        predict_label = np.argmax(predictions.cpu().numpy(), axis=1).flatten().tolist()[0]
    
    return predict_label

def predict_label_from_text(text, model_path, tokenizer_path):
    model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    return make_prediction(text, tokenizer, model)
