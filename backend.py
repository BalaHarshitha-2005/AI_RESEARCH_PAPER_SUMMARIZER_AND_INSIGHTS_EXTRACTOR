from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import pdfplumber
import uuid
import os

from transformers import BartTokenizer, BartForConditionalGeneration

app = FastAPI()

# -----------------------------
# In-memory storage
# -----------------------------

users = {}
papers = {}

# -----------------------------
# Load BART model
# -----------------------------

print("Loading BART model...")

tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

print("Model loaded successfully")

# -----------------------------
# Models
# -----------------------------

class Signup(BaseModel):
    username: str
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class SummaryRequest(BaseModel):
    paper_id: str
    length: str


class Question(BaseModel):
    question: str


class Improve(BaseModel):
    text: str


# -----------------------------
# Root API
# -----------------------------

@app.get("/")
def home():
    return {"message": "AI Research Paper Assistant API Running"}


# -----------------------------
# Signup
# -----------------------------

@app.post("/signup")
def signup(user: Signup):

    if user.email in users:
        return {"message": "User already exists"}

    users[user.email] = {
        "username": user.username,
        "password": user.password
    }

    return {"message": "Signup successful"}


# -----------------------------
# Login
# -----------------------------

@app.post("/login")
def login(user: Login):

    if user.email not in users:
        return {"message": "User not found"}

    if users[user.email]["password"] != user.password:
        return {"message": "Invalid password"}

    return {"message": "Login successful"}


# -----------------------------
# Upload Paper
# -----------------------------

@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    file_name = f"{uuid.uuid4()}.pdf"

    with open(file_name, "wb") as f:
        f.write(await file.read())

    text = ""

    with pdfplumber.open(file_name) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    os.remove(file_name)

    if text.strip() == "":
        return {"error": "No readable text found in PDF"}

    paper_id = str(uuid.uuid4())

    papers[paper_id] = text

    return {
        "paper_id": paper_id,
        "message": "Paper uploaded successfully"
    }


# -----------------------------
# BART Summarization
# -----------------------------

def bart_summarize(text, max_len, min_len):

    inputs = tokenizer(
        text,
        max_length=1024,
        truncation=True,
        return_tensors="pt"
    )

    summary_ids = model.generate(
        inputs["input_ids"],
        num_beams=4,
        max_length=max_len,
        min_length=min_len,
        early_stopping=True
    )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


# -----------------------------
# Generate Summary
# -----------------------------

def generate_summary(text, summary_type):

    chunk_size = 900

    chunks = [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]

    partial_summaries = []

    for chunk in chunks[:15]:

        summary = bart_summarize(chunk, 120, 50)

        partial_summaries.append(summary)

    combined_summary = " ".join(partial_summaries)

    # Final summary stage

    if summary_type == "short":

        final_summary = bart_summarize(combined_summary, 180, 120)

        return final_summary


    elif summary_type == "detailed":

        final_summary = bart_summarize(combined_summary, 350, 250)

        return final_summary


    elif summary_type == "bullet":

        final_summary = bart_summarize(combined_summary, 350, 250)

        sentences = final_summary.split(".")

        bullets = [
            "• " + s.strip()
            for s in sentences
            if len(s.strip()) > 20
        ]

        return bullets[:20]

    return combined_summary


# -----------------------------
# Summary API
# -----------------------------

@app.post("/summarize")
def summarize(req: SummaryRequest):

    if req.paper_id not in papers:
        return {"error": "Paper not found"}

    text = papers[req.paper_id]

    summary = generate_summary(text, req.length)

    return {"summary": summary}


# -----------------------------
# Chat with Paper
# -----------------------------

@app.post("/chat")
def chat(q: Question):

    return {
        "answer": "Chat feature can be improved using embeddings + RAG."
    }


# -----------------------------
# Improve Writing
# -----------------------------

@app.post("/improve")
def improve_text(data: Improve):

    improved = data.text + " (Improved academic writing)"

    return {
        "improved_text": improved
    }