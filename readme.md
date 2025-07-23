# 🚀 FastAPI Upload Service

A modular FastAPI application with an upload route and clean folder structure.

---

## 📁 Project Structure

```
HackRx/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── routes/
│       ├── __init__.py
│       └── upload.py
├── .env              # Not committed
├── .gitignore
├── README.md
├── requirements.txt
└── venv/             # Virtual environment (ignored)
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Set `PYTHONPATH` if needed

```powershell
$env:PYTHONPATH = "."
```

### 5. Run the FastAPI Server

```bash
uvicorn app.main:app --reload
```
