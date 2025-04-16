import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import cv2
import fitz
import numpy as np
from fpdf import FPDF

global pdf_path, test_size, output_name

def merge_pdfs(file_paths, output_path="temp_merged.pdf"):
    merged_doc = fitz.open()
    for path in file_paths:
        current = fitz.open(path)
        merged_doc.insert_pdf(current)
        current.close()
    merged_doc.save(output_path)
    merged_doc.close()
    return output_path


def browse_file():
    global pdf_path, test_size, output_name
    # Check if percentage input is provided
    if ((number.get('1.0', tk.END))[:-1]) == "":
        tk.messagebox.showerror('Error', 'Enter percent!')
        return

    # Get user input size
    str_size = (number.get('1.0', tk.END))[:-1]

    try:
        test_size = int(str_size) / 100
    except Exception:
        tk.messagebox.showerror('Error', 'Enter numbers please!')
        return

    try:
        # Ask user to select one or more PDF files
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])

        # Return if no file was selected
        if len(file_paths) == 0:
            return

        # Get output file name input
        output_name = (name.get('1.0', tk.END))[:-1]

        if output_name == "" or output_name == "Default name is: ""NEW-filename""":
            cut_index = file_paths[0].rindex("/")
            output = file_paths[0][cut_index + 1:]
            output_name = os.path.join(dir_path, "NEW-" + output)
        else:
            output_name += ".pdf"
            output_name = os.path.join(dir_path, output_name)

        # Merge files if multiple PDFs were selected
        if len(file_paths) == 1:
            pdf_path = file_paths[0]
        else:
            pdf_path = merge_pdfs(file_paths)

        messagebox.showinfo("Files received", f"{len(file_paths)} PDF file(s) loaded successfully.")

    except Exception as e:
        tk.messagebox.showerror('Error', e)

def generate():
    global pdf_path, test_size, output_name
    # Check if output file already exists
    if os.path.isfile(output_name):
        msg_box = tk.messagebox.askquestion('File exist',
                                            'A file with this name exists - do you want to carry on?',
                                            icon='warning')
        if msg_box == 'yes':
            delete_white_lines_and_columns(pdf_path, test_size, output_name)
        else:
            restart()
    else:
        delete_white_lines_and_columns(pdf_path, test_size, output_name)
def color_name_to_bgr(color_name):
    colors = {
        "Yellow": (0, 255, 255),
        "Green": (0, 255, 0),
        "Blue": (255, 0, 0),
        "Pink": (255, 0, 255),
        "Cyan": (255, 255, 0)
    }
    return colors.get(color_name, (0, 255, 255))  # Default: Yellow

def restart():
    progress_bar['value'] = 0
    load_label.pack_forget()
    progress_bar.pack_forget()
    var.set(0)
    number.delete("1.0", "end")
    number.pack(pady=5)
    name.delete("1.0", "end")
    number.pack(pady=5)
    home.pack(fill='both', expand=1)


def detect_visual_titles(gray_img, top_ratio=0.3):
    """
    Improved title detection based on:
    - Dark thick horizontal lines
    - Appearing at the top portion of the image
    - Height threshold to ignore short bold lines
    """
    h, w = gray_img.shape
    limit = int(h * top_ratio)
    min_height = 15
    proj = np.sum(gray_img[0:limit] < 100, axis=1)
    avg_proj = np.mean(proj)
    std_proj = np.std(proj)
    threshold = avg_proj + std_proj * 1.5
    titles = []
    in_block = False
    y1 = 0
    for y, val in enumerate(proj):
        if val > threshold:
            if not in_block:
                y1 = y
                in_block = True
        else:
            if in_block:
                y2 = y
                if (y2 - y1) > min_height:
                    titles.append((y1, y2))
                in_block = False
    return titles


def apply_highlight(image, regions, color=(0, 255, 255), alpha=0.4, margin=5):
    """
    Applies semi-transparent background highlight like a marker behind text.
    """
    overlay = image.copy()
    for y1, y2 in regions:
        y1 = max(0, y1 - margin)
        y2 = min(image.shape[0], y2 + margin)
        cv2.rectangle(overlay, (0, y1), (image.shape[1], y2), color, -1)
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

def delete_white_lines_and_columns(pdf_path, test_size, output_name):
    load_label.pack(pady=10)
    progress_bar.pack(pady=10)

    doc = fitz.open(pdf_path)
    failed_pages = []
    pdf = FPDF(unit='pt', format='A4')

    max_w = 0
    x_position = 1
    index = 0
    good_sum = 0
    y_position = 1

    pdf.add_page()
    loading_inc = float(100) / float(doc.page_count)
    if(color_var.get() != "None"):
        highlight_color = color_name_to_bgr(color_var.get())

    for page_num in range(doc.page_count):
        index += 1
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        temp_image_path = f"temp_image_{page_num}.jpg"
        pix.save(temp_image_path)
        image = cv2.imread(temp_image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Title highlighting
        title_boxes = detect_visual_titles(gray)
        image = apply_highlight(image, title_boxes, color=highlight_color, alpha=0.4)

        inverted_gray = cv2.bitwise_not(gray)
        _, thresholded = cv2.threshold(inverted_gray, 200, 255, cv2.THRESH_BINARY)
        row_sums = thresholded.sum(axis=1)
        col_sums = thresholded.sum(axis=0)

        try:
            if var.get() == 0:
                clean_image = np.delete(np.delete(image, np.where(row_sums == 0), axis=0),
                                        np.where(col_sums == 0), axis=1)
                cv2.imwrite(temp_image_path, clean_image, [cv2.IMWRITE_JPEG_QUALITY, 100])
                scaled_image = cv2.resize(clean_image, (int(clean_image.shape[1] * test_size),
                                                        int(clean_image.shape[0] * test_size)),
                                          interpolation=cv2.INTER_LANCZOS4)
            else:
                scaled_image = cv2.resize(image, (int(image.shape[1] * test_size),
                                                  int(image.shape[0] * test_size)))

            if y_position > pdf.h - scaled_image.shape[0]:
                # Draw vertical line to separate columns
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
            progress_bar['value'] += loading_inc
            home.update_idletasks()

        except Exception:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            print(index)
            failed_pages.append(index)

    try:
        pdf.output(output_name)
        doc.close()

        # 🗑️ Delete the temp merged PDF if it exists
        if pdf_path == "temp_merged.pdf" and os.path.exists("temp_merged.pdf"):
            os.remove("temp_merged.pdf")

        if len(failed_pages) > 0:
            failed_str = ", ".join(str(i) for i in failed_pages)
            msg_box = tk.messagebox.askquestion('Done', f"   {good_sum} / {index} pages were compressed.\n"
                                                        f"Pages that failed: {failed_str}\n\n"
                                                        "Do you want to create another file?")
        else:
            msg_box = tk.messagebox.askquestion('Done', f"   Succeeded - {good_sum} pages were compressed.\n\n"
                                                        "Do you want to create another file?")
        if msg_box == 'yes':
            restart()
        else:
            window.destroy()

    except Exception as e:
        tk.messagebox.showerror('Error', 'Check if there is a file with the same name that is open: \n' + str(e))
        restart()



if __name__ == '__main__':

    window = tk.Tk()
    dir_path = os.path.join(os.path.expanduser("~/Desktop"), "FormulaSheet")
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path, mode=0o666)
    # Set the window title
    window.title("Formula sheet creator")
    style_frame = ttk.Style()
    # Set the background color for the frame
    style_frame.configure("My.TFrame", background="black")


    home = ttk.Frame(window, style="My.TFrame")
    home.pack(fill='both', expand=1)
    label = tk.Label(home, text="   Click the button to upload a PDF file:   ", bg='Black', fg='White',
                     font=('David', 20))
    label.pack(pady=20)
    # Create a button
    label2 = tk.Label(home, text=" Enter size (by percent): ", bg='Black', fg='White',
                      font=('David', 15))
    label2.pack(pady=5)
    number = tk.Text(home, height=1, font=('Ariel', 15), width=5)
    number.pack(pady=5)
    label3 = tk.Label(home, text=" Enter output file`s name: ", bg='Black', fg='White',
                      font=('David', 15))
    label3.pack(pady=5)
    name_def = tk.Label(home, text="Default name is: ""NEW-filename""", bg='Black', fg='Red',
                        font=('David', 10))
    name_def.pack(pady=5)
    name = tk.Text(home, height=1, font=('Ariel', 15), width=20)
    name.pack(pady=5)
    var = tk.IntVar()
    check1 = tk.Checkbutton(home, text='Do not delete empty lines and columns', bg='Black', fg='Red', variable=var,
                            onvalue=1, offvalue=0)
    check1.pack(pady=5)
    brow = tk.Button(home, text="Upload", font=('David', 15), bg='Black', fg='White', width=20, command=browse_file)
    brow.pack(pady=10)
    load_label = tk.Label(home, text="   Please wait for the file to be ready   ", bg='Black',
                          fg='White', font=('David', 15))
    progress_bar = ttk.Progressbar(home, length=400, orient=HORIZONTAL)

    # Highlight color selection
    label_color = tk.Label(home, text=" Choose highlight color: ", bg='Black', fg='White', font=('David', 15))
    label_color.pack(pady=5)

    color_var = tk.StringVar(value="None")
    color_options = ["None", "Yellow", "Green", "Blue", "Pink", "Cyan"]
    color_menu = ttk.Combobox(home, textvariable=color_var, values=color_options, width=10, state="readonly")
    color_menu.pack(pady=5)

    generateB = tk.Button(home, text="Generate", font=('David', 15), bg='Black', fg='White', width=20, command=generate)
    generateB.pack(pady=10)

    window.mainloop()
