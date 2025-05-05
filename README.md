# 📘 Formula Sheet Generator – Full Stack Web App

A web-based tool that helps students automatically generate compressed, high-quality formula sheets from PDF summaries. Built with Python (Flask), OpenCV, HTML/CSS/JS, and deployed as a monetized production site.

---

## 🚀 Features

- ✅ Upload one or more PDF files and merge them
- 📏 Automatically scale and compress pages based on user-defined percentage
- ✂️ Option to remove empty whitespace rows and columns for compact layout
- 🧠 Detects large, bold titles and highlights them like a marker (custom color)
- 🖼️ Outputs multi-column optimized formula sheets in PDF format
- 📁 Option to give a custom filename or auto-generate based on input
- 💰 Integrated Google AdSense with pre-download popup ads
- 🌐 Fully deployed online using [Railway](https://railway.app) with free hosting

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, OpenCV, PyMuPDF
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **PDF Output**: FPDF for dynamic PDF generation
- **Deployment**: Railway.app (free tier), Docker-ready

---

## 📂 Project Structure

```
FS-APP/
├── app.py                     # Flask main application
├── templates/
│   ├── index.html             # Upload form with UI
│   ├── processing.html        # Live progress + download
│   └── how_to_use.html        # Usage explanation
├── static/                    # CSS & JS files
├── uploads/                  # Temp uploaded PDFs
├── output/                   # Temp generated formula sheets
├── processing/
│   └── processor.py           # PDF processing logic
├── requirements.txt
└── README.md
```

---

## 💡 How to Use

1. Upload a PDF summary (or multiple) – preferably with mostly text, not images.
2. Choose a resize percentage (smaller % = more pages per sheet).
3. Optionally choose:
   - To **highlight titles** (choose marker color)
   - To **keep original layout** (no white line/column removal)
   - To **give your own filename**
4. Click `Generate` – an ad will pop up before download.
5. After ~5 seconds, your compressed formula sheet will automatically download.

---

## 🌍 Live Demo

👉 [formula-sheet-generator](https://your-live-url.com)

---

## 📝 License

MIT – Free to use and modify for personal or educational purposes.
