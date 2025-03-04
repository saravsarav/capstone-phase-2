import os
import joblib
import pandas as pd
import torch
import json
import xml.etree.ElementTree as ET
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
from torch.utils.data import Dataset
from imblearn.over_sampling import SMOTE
from sklearn.feature_extraction.text import TfidfVectorizer

# ✅ Faster CSV Loading

def load_data(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == ".csv":
        data = pd.read_csv(file_path, encoding="utf-8", low_memory=False)  # ✅ FIX: Removed pyarrow
    elif file_extension == ".json":
        data = pd.read_json(file_path)
    elif file_extension == ".xml":
        data = read_xml(file_path)
    else:
        raise ValueError("Unsupported file format. Please use CSV, JSON, or XML.")
    
    return data

# ✅ Parse XML file
def read_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    records = []
    for entry in root.findall("record"):  # Modify based on actual XML structure
        text = entry.find("Description").text if entry.find("Description") is not None else ""
        label = entry.find("Severity").text if entry.find("Severity") is not None else ""
        records.append({"Description": text, "Severity": label})
    return pd.DataFrame(records)

# ✅ Load multiple files from a directory
def load_multiple_files(directory):
    all_data = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            data = load_data(file_path)
            all_data.append(data)
            print(f"✅ Loaded: {filename}")
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
    
    return pd.concat(all_data, ignore_index=True) if all_data else None

# ✅ Load dataset
dataset_directory = "D:\capstone\dataset\data1"
data = load_multiple_files(dataset_directory)
if data is None:
    exit()

# ✅ Normalize column names
data.columns = data.columns.str.strip()
if "Description" not in data.columns or "Severity" not in data.columns:
    print(f"❌ Required columns missing! Found columns: {data.columns.tolist()}")
    exit()

# ✅ Normalize labels
data["Severity"] = data["Severity"].str.strip().str.lower()
severity_mapping = {"low": 0, "medium": 1, "high": 2, "critical": 3}
data["Severity"] = data["Severity"].map(severity_mapping)

if data["Severity"].isnull().sum() > 0:
    print("❌ Some labels could not be mapped! Check your dataset.")
    exit()

# ✅ Handle missing values
data = data.dropna()

# ✅ Convert text to numerical features using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X_transformed = vectorizer.fit_transform(data["Description"])

# ✅ Handle class imbalance using SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_transformed, data["Severity"])

# ✅ Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# ✅ Define PyTorch dataset
class VulnerabilityDataset(Dataset):
    def __init__(self, descriptions, labels):
        self.descriptions = descriptions.toarray()
        self.labels = labels.tolist()

    def __len__(self):
        return len(self.descriptions)

    def __getitem__(self, idx):
        return {
            "input_ids": torch.tensor(self.descriptions[idx], dtype=torch.float32),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }

# ✅ Load BERT tokenizer & model
tokenizer = BertTokenizer.from_pretrained("google/bert_uncased_L-4_H-256_A-4")
model = BertForSequenceClassification.from_pretrained("google/bert_uncased_L-4_H-256_A-4", num_labels=4)

# ✅ Convert to PyTorch dataset
train_dataset = VulnerabilityDataset(X_train, y_train)
test_dataset = VulnerabilityDataset(X_test, y_test)

# ✅ Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=2,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    fp16=torch.cuda.is_available(),
)

# ✅ Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# ✅ Train model
trainer.train()

# ✅ Evaluate model
preds = trainer.predict(test_dataset)
y_pred = preds.predictions.argmax(axis=1)

# ✅ Calculate and display model performance metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"\n✅ BERT Model Accuracy: {accuracy * 100:.2f}%")
print(f"✅ Precision: {precision:.4f}")
print(f"✅ Recall: {recall:.4f}")
print(f"✅ F1 Score: {f1:.4f}")

print("\n📌 Classification Report:\n", classification_report(y_test, y_pred))

# ✅ Save the model
model.save_pretrained("vulnerability_classifier")

tokenizer.save_pretrained("vulnerability_classifier")

print("\n✅ Model Trained, Evaluated, and Saved!")