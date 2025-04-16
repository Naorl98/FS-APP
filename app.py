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

    except Exception as e:
        tk.messagebox.showerror('Error', e)


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


def delete_white_lines_and_columns(pdf_path, test_size, output_name):
    load_label.pack(pady=10)
    progress_bar.pack(pady=10)
    # Open the PDF file
    doc = fitz.open(pdf_path)
    failed_pages = []
    pdf = FPDF(unit='pt', format='A4')
    max_w = 0
    # Initialize variables for image positioning
    x_position = 1
    index = 0
    good_sum = 0
    y_position = 1
    pdf.add_page()
    loading_inc = float(100) / float(doc.page_count)

    # Iterate through the pages
    for page_num in range(doc.page_count):
        index += 1
        # Load the page
        page = doc.load_page(page_num)
        # Render the page as an image
        pix = page.get_pixmap(dpi=300)

        # Save the pixmap as an intermediate image
        temp_image_path = f"temp_image_{page_num}.jpg"

        pix.save(temp_image_path)

        image = cv2.imread(temp_image_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Invert the grayscale image
        inverted_gray = cv2.bitwise_not(gray)

        # Apply adaptive thresholding to extract white lines and columns
        _, thresholded = cv2.threshold(inverted_gray, 200, 255, cv2.THRESH_BINARY)

        # Calculate the row and column sums
        row_sums = thresholded.sum(axis=1)
        col_sums = thresholded.sum(axis=0)
        try:
            if var.get() == 0:
                # Delete the white lines and columns
                clean_image = np.delete(np.delete(image, np.where(row_sums == 0), axis=0),
                                        np.where(col_sums == 0), axis=1)
                cv2.imwrite(temp_image_path, clean_image, [cv2.IMWRITE_JPEG_QUALITY, 100])
                # Scale the cleaned image
                scaled_image = cv2.resize(clean_image, (int(clean_image.shape[1] * test_size),
                                                        int(clean_image.shape[0] * test_size)),
                                          interpolation=cv2.INTER_LANCZOS4)

            else:
                scaled_image = cv2.resize(image, (int(image.shape[1] * test_size),
                                                  int(image.shape[0] * test_size)))

            # Add the cleaned image to the PDF object

            if y_position > pdf.h - scaled_image.shape[0]:
                # Draw vertical line to separate columns
                pdf.set_draw_color(0, 0, 0)  # black
                pdf.set_line_width(0.5)  # thin line
                pdf.line(x_position - 0.5, 0, x_position - 0.5, pdf.h)  # from top to bottom of page

                y_position = 1
                x_position += max_w + 1  # Adjust the spacing between columns
            if x_position > pdf.w - scaled_image.shape[1]:
                pdf.add_page()
                x_position = 1
                y_position = 1
                max_w = 0

            # Add the cleaned image to the PDF object
            pdf.image(temp_image_path, x=x_position, y=y_position, w=scaled_image.shape[1], h=scaled_image.shape[0])
            y_position += scaled_image.shape[0] + 1  # Adjust the spacing between images

            # Update the image positioning
            if scaled_image.shape[1] >= max_w:
                max_w = scaled_image.shape[1]

            # Delete the temporary image
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
        # Save the output PDF file
        pdf.output(output_name)
        # Close the PDF file
        doc.close()

        if len(failed_pages) > 0:
            failed_str = ""
            for i in failed_pages:
                failed_str += str(i) + ", "
            msg_box = tk.messagebox.askquestion('Done', "   " + str(good_sum) + " / " + str(index) +
                                                " pages were compressed, "
                                                "pages that failed: " + failed_str[
                                                                        :-2] + "   \n" + "\n" +
                                                "Do you want to create another file?")
            if msg_box == 'yes':
                restart()
            else:
                window.destroy()
        else:
            msg_box = tk.messagebox.askquestion('Done', "   Succeeded - " + str(good_sum) + " pages were compressed   "
                                                + "   \n" + "\n" +
                                                "Do you want to create another file?")
            if msg_box == 'yes':
                tk.messagebox.showinfo('Return', 'You will now return to the application screen')
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

    window.mainloop()
