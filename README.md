# Outreach Applier

A professional, automated outreach tool for managing and sending job application emails with an anti-spam pipeline and dynamic CSV processing queue.

## 🚀 Quick Start

You can boot both the frontend dashboard and backend service simultaneously with a single command from the project root!

**Windows:**
```cmd
run_service.bat
```
*(Or simply double-click `run_service.bat` in File Explorer)*

**Mac/Linux (or directly via Python):**
```bash
python run_service.py
```

- **Dashboard:** [http://localhost:5173](http://localhost:5173)
- **API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

<details>
<summary><b>🛠️ Configuration & Environment</b></summary>

Before sending emails, you must configure your Google App credentials.

1. Navigate to the `outreach-service/` directory.
2. Copy `.env.example` to a new file named `.env`.
3. Add your email and Google App Password:
   ```env
   SENDER_EMAIL=your_email@gmail.com
   APP_PASSWORD=your_app_password
   PROCESSING_QUEUE_DIR=processing_queue
   PROCESSED_FILE=history/processed_records.xlsx
   ```
*(Note: You must use a [Google App Password](https://support.google.com/accounts/answer/185833?hl=en), standard passwords will not work).*
</details>

<details>
<summary><b>🏗️ Architecture & Manual Setup</b></summary>

### Architecture
- **outreach-ui**: A structured Vue 3 frontend powered by Vite for managing the processing queue and triggering workflows.
- **outreach-service**: A Python FastAPI backend that processes CSV files, generates HTML email templates, and sends emails via SMTP.

### Manual Setup (if not using run_service)
**1. Backend:**
```bash
cd outreach-service
pip install -r requirements.txt
python app.py
```

**2. Frontend:**
```bash
cd outreach-ui
npm install
npm run dev
```
</details>
