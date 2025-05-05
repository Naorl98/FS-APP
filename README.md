# 📘 Formula Sheet Generator – Full Stack Web App

A web-based tool that helps students automatically generate compressed, high-quality formula sheets from PDF summaries. Built with Python (Flask), OpenCV, HTML/CSS/JS, and designed to run locally or be deployed to any web server.

---

## 🚀 Features

- ✅ Upload one or more PDF files and merge them
- 📏 Automatically scale and compress pages based on user-defined percentage
- ✂️ Option to remove empty whitespace rows and columns for compact layout
- 🧠 Detects large, bold titles and highlights them like a marker (custom color)
- 🖼️ Outputs multi-column optimized formula sheets in PDF format
- 📁 Option to give a custom filename or auto-generate based on input
- 💰 Integrated Google AdSense with pre-download popup ads (optional)
- 🌐 Runs locally using Flask or can be deployed manually on any server

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, OpenCV, PyMuPDF
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **PDF Output**: FPDF for dynamic PDF generation
- **Deployment Options**: Locally via Flask, or Docker-ready

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

## 💡 How to Run Locally

1. Clone the repository to your machine:
   ```bash
   git clone https://github.com/your-username/formula-sheet-generator.git
   cd formula-sheet-generator
   ```

2. (Optional but recommended) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask app:
   ```bash
   python app.py
   ```

5. Open your browser and go to:
   ```
   http://localhost:5050
   ```

6. Upload one or more PDF files and fill in the options:
   - Choose a resize percentage (smaller % = smaller text = more content per page)
   - Optionally enable marker highlighting or preserve original layout
   - Enter a custom file name (optional)
   - Click **Generate** – a popup ad will appear
   - After 5 seconds, your formula sheet will automatically be downloaded

> 🧹 The generated file is automatically deleted from the server after the download completes.

---

## 📝 License

MIT – Free to use and modify for personal or educational purposes.