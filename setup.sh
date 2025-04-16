cd /home/dvir/PycharmProjects/FS-_Creator

# מחיקת סביבה קיימת אם קיימת
rm -rf .venv

# יצירת סביבה וירטואלית חדשה
python3 -m venv .venv

# הפעלת הסביבה
source .venv/bin/activate

# עדכון pip
pip install --upgrade pip

# התקנת כל התלויות
pip install opencv-python PyMuPDF numpy fpdf

# בדיקת תקינות
python -c "import cv2, fitz, numpy, fpdf; print('✅ All packages imported successfully!')"
