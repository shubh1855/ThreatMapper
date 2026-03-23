# STRIDE Threat Analyzer

An AI-powered STRIDE threat modeling tool using **Cohere API** as the backend intelligence engine and a simple HTML/CSS/JS frontend.

## 🚀 Features
- Analyze software architecture or system descriptions for potential threats.
- STRIDE categories: **Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege**.
- FastAPI backend + Cohere Agentic AI.
- Lightweight, static frontend.

---

## 📂 Project Structure
```
threat-modelling/
├── backend/
│   ├── main.py            # FastAPI server
│   ├── models.py          # Request/response models
│   ├── stride_agent.py    # Cohere API logic
├── frontend/
│   ├── index.html         # UI
│   ├── style.css          # Styling
│   ├── script.js          # Frontend logic
```

---

## 🛠️ Requirements
- Python **3.9+**
- Node.js *(optional, only if you want advanced frontend tooling)*
- A [Cohere API Key](https://dashboard.cohere.com/)

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Atharva-G100/threat-modelling.git
cd threat-modelling
```

### 2️⃣ Install Backend Dependencies
```bash
cd backend
pip install fastapi uvicorn cohere pydantic
```

### 3️⃣ Set Your Cohere API Key
On **Windows (PowerShell)**:
```powershell
setx COHERE_API_KEY "your_api_key_here"
```
On **Mac/Linux**:
```bash
export COHERE_API_KEY="your_api_key_here"
```
*(You only need to do this once per machine.)*

---

### 4️⃣ Start the Backend Server
```bash
cd backend
uvicorn main:app --reload
```
Server will run at:  
👉 **http://127.0.0.1:8000**

---

### 5️⃣ Open the Frontend
- Open `frontend/index.html` in your browser.
- Enter your system description in the input box.
- View the AI-generated STRIDE threat analysis.

---

## 📝 Notes
- Make sure your backend server is running before using the frontend.
- The API key is stored **locally** and not in GitHub for security.
- If you restart your PC, the API key will still be available (since we used `setx`).

---

## 📜 License
This project is for educational purposes.  
Feel free to fork and improve it.
