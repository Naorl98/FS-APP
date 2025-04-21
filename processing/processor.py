import os
import fitz
import cv2
import numpy as np
from fpdf import FPDF
from processing.utils import detect_visual_titles, apply_highlight, color_name_to_bgr


def process_pdf(file_paths, output_path, scale_percent, highlight_color, clean_whitespace, progress_status=None, task_id=None):
    if len(file_paths) == 1:
        pdf_path = file_paths[0]
    else:
        pdf_path = 'temp_merged.pdf'
        merge_documents(file_paths, pdf_path)

    doc = fitz.open(pdf_path)
    failed_pages = []
    pdf = FPDF(unit='pt', format='A4')

    max_w = 0
    x_position = 1
    index = 0
    good_sum = 0
    y_position = 1

    pdf.add_page()
    highlight_color_bgr = None
    if highlight_color and highlight_color != "None":
        highlight_color_bgr = color_name_to_bgr(highlight_color)
    loading_inc = float(100) / float(doc.page_count)

    for page_num in range(doc.page_count):
        index += 1
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        temp_image_path = f"temp_image_{page_num}.jpg"
        pix.save(temp_image_path)
        image = cv2.imread(temp_image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if progress_status is not None and task_id is not None:
            progress_status[task_id] = int((page_num + 1) * loading_inc)

        # Title highlighting
        if highlight_color_bgr:
            title_boxes = detect_visual_titles(gray)
            image = apply_highlight(image, title_boxes, color=highlight_color_bgr, alpha=0.4)

        inverted_gray = cv2.bitwise_not(gray)
        _, thresholded = cv2.threshold(inverted_gray, 200, 255, cv2.THRESH_BINARY)
        row_sums = thresholded.sum(axis=1)
        col_sums = thresholded.sum(axis=0)

        try:
            if clean_whitespace:
                scaled_image = cv2.resize(image, (int(image.shape[1] * scale_percent / 100),
                                                  int(image.shape[0] * scale_percent / 100)))
            else:
                clean_image = np.delete(np.delete(image, np.where(row_sums == 0), axis=0),
                                        np.where(col_sums == 0), axis=1)
                cv2.imwrite(temp_image_path, clean_image, [cv2.IMWRITE_JPEG_QUALITY, 100])
                scaled_image = cv2.resize(clean_image, (int(clean_image.shape[1] * scale_percent / 100),
                                                        int(clean_image.shape[0] * scale_percent / 100)),
                                          interpolation=cv2.INTER_LANCZOS4)
            if y_position > pdf.h - scaled_image.shape[0]:
                pdf.set_draw_color(0, 0, 0)
                pdf.set_line_width(0.5)
                pdf.line(x_position - 0.5, 0, x_position - 0.5, pdf.h)
                y_position = 1
                x_position += max_w + 1

            if x_position > pdf.w - scaled_image.shape[1]:
                pdf.add_page()
                x_position = 1
                y_position = 1
                max_w = 0

            pdf.image(temp_image_path, x=x_position, y=y_position,
                      w=scaled_image.shape[1], h=scaled_image.shape[0])
            y_position += scaled_image.shape[0] + 1

            if scaled_image.shape[1] >= max_w:
                max_w = scaled_image.shape[1]

            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

            good_sum += 1

        except Exception:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            print(index)
            failed_pages.append(index)

    try:
        pdf.output(output_path)
        doc.close()
        if pdf_path == 'temp_merged.pdf' and os.path.exists(pdf_path):
            os.remove(pdf_path)
    except Exception as e:
        raise RuntimeError("Error saving PDF: " + str(e))


def merge_documents(file_paths, output_path):
    merged = fitz.open()
    for path in file_paths:
        current = fitz.open(path)
        merged.insert_pdf(current)
        current.close()
    merged.save(output_path)
    merged.close()
