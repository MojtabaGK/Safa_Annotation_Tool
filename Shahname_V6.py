# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk 
import shutil
from ultralytics import YOLO
import numpy as np
import time


class ProjectViewerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Viewer")
        self.geometry("1200x700")
        self.configure(bg="#ffffff")
        self.minsize(1000, 600)

        self._setup_styles()
        self._setup_menu()
        self._setup_widgets()

        self.model = None
        self.image_tk = None  # Keep reference to avoid GC
        self.start_x = None
        self.start_y = None
        self.rect = None # canvas rectangle id during drawing
        self.rec_IDs = [] # ids for the current rectangles
        self.original_image = None
        self.image_full_path = None
        self.rectangles = []
        self.IsLocks = []
        self.Labels = []
        self.img_index = None # index of drawn image in left convas
        self.rect_index = None # index of rectangle selected in right list
        self.label_var.set("")
        self.coords = [] # Coordinates of the selected rectangle
        self.zoom_factor = 1 # Zoom factor
        self.crop_cords = [0, 0 , 1, 1] #Crop coordinations used for zoom
        self.label_to_number = {}
        self.last_zoom_time = 0
        self.char_sequense = ""

        self.project_data = {
            "name": "",               # Project name (str)
            "project_folder": "",     # Project folder path (str)
            "image_folder": "",       # Folder where images are located (str)
            "path_to_AI": "",         # path to AI assistant model *.pt
            "images": [],             # List of image full paths (list of str)
            "rectangles": {},         # Dict of {image_path: [ (x1, y1, x2, y2), ... ] }
            "IsLocks": {},             # List of Lock boolian values for each Rectangle
            "Labels": {}           # List of Label name values for each Rectangle
        }

        chars_per = [1570, 1575, 1576, 1662, 1578, 1579, 1580, 1670, 1581, 1582, 1583,
                    1584, 1585, 1586, 1688, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594,
                    1601, 1602, 1705, 1711, 1604, 1605, 1606, 1608, 1607, 1740, 1569, 1571,
                    1572, 1574, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785,
                    40, 41, 91, 93, 1567, 33, 46, 1548, 58, 1563, 171, 187, 43, 45, 47,
                    215, 247, 60, 61, 62, 1643, 8204, 32,
                    48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
        strs_per = []
        for code in chars_per:
            strs_per.append(chr(code))
        

        Char_labels=["Aaa", "Alf", "Beh", "Peh", "Teh", "Seh", "Jim", "Che", "Hej",
        "khe", "Dal", "Zal", "Reh", "Zeh", "Zhe", "Sin", "Shin", "Sad",
        "Zad", "Taa", "Zaa", "Ein", "Ghein", "Feh", "Ghaf", "Kaf", "Gaf",
        "Lam", "Mim", "Nun", "Vav", "Heh", "Yeh", "Hmz", "Ahmz", "Vhmz",
        "Ehmz", "#0", "#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8", "#9",
        "())", "(()", "[]]", "[[]", "؟", "!", ".", "،", ":", "؛", "«»»", "««»",
        "+", "-", "/", "×", "÷", "<>>", "=", "<<>", "MMYZ", "HSPC", "SPC",
        "#0", "#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8", "#9"]

        # ایجاد دیکشنری برای نگاشت کاراکتر به کلمه معادل
        self.Str_to_name = {code: name for code, name in zip(strs_per, Char_labels)}

    def _setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#ffffff')
        self.style.configure('Listbox.TFrame', background='#f9fafb', borderwidth=1, relief='solid')
        self.style.configure('Side.TFrame', background='#f3f4f6', borderwidth=1, relief='solid')
        self.style.configure('TLabel', background='#f3f4f6', foreground='#6b7280', font=('Segoe UI', 10))

    def _setup_menu(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Add New Image to the Project", command=self.Add_New_Image_to_Project)
        file_menu.add_command(label="Save Project As", command=self.save_project)
        Edit_menu = tk.Menu(menu_bar, tearoff=0)
        Edit_menu.add_command(label="Find Persian character sequense", command=self.Find_Persian_character_sequense)
        Edit_menu.add_separator()  # اضافه کردن خط جداکننده
        Edit_menu.add_command(label="Lock All", command=self.Lock_All)
        Edit_menu.add_command(label="unLock All", command=self.unLock_All)
        Edit_menu.add_separator()  # اضافه کردن خط جداکننده
        Edit_menu.add_command(label="Lock This Image", command=self.Lock_This_Image)
        Edit_menu.add_command(label="unLock This Image", command=self.unLock_This_Image)
        Edit_menu.add_separator()  # اضافه کردن خط جداکننده
        Edit_menu.add_command(label="Clear Bounding box for the current image", command=self.Clear_BBox_list)
        Export_menu = tk.Menu(menu_bar, tearoff=0)
        Export_menu.add_command(label="Split images by BBoxes", command=self.Split_images_by_BBoxes)
        Export_menu.add_command(label="Split images by BBoxes and label", command=self.Split_images_by_Label)
        Export_menu.add_command(label="Export to YAML format", command=self.Export_to_YAML)
        Export_menu.add_separator()  # اضافه کردن خط جداکننده
        Export_menu.add_command(label="Split Current Image by BBoxes", command=self.Split_Current_image_by_BBoxes)
        Export_menu.add_command(label="Export Current Image to YAML format", command=self.Export_Image_to_YAML)
        Export_menu.add_command(label="Split Current Image by BBoxes and label", command=self.Split_Current_image_by_Label)
        Export_menu.add_separator()  # اضافه کردن خط جداکننده
        Export_menu.add_command(label="Split Project by Current image", command=self.Split_Project_by_Current_image)
        Import_menu = tk.Menu(menu_bar, tearoff=0)
        Import_menu.add_command(label="Import YOLO Database", command=self.Import_YOLO_dataset)
        Import_menu.add_separator()  # اضافه کردن خط جداکننده
        Import_menu.add_command(label="Merge with another Project", command=self.Merge_Project)
        Labels_menu = tk.Menu(menu_bar, tearoff=0)
        Labels_menu.add_command(label="Import Label Names List", command=self.Import_Label_Names_List)
        Labels_menu.add_command(label="Merge Label Names List", command=self.Merge_Label_Names_List)
        Labels_menu.add_command(label="Reset Label Names List", command=self.Reset_Label_Names_List)
        Labels_menu.add_separator()  # اضافه کردن خط جداکننده
        Labels_menu.add_command(label="Change Persian Characters to Label names", command=self.Change_Persian_Characters_to_Label_names)
        AI_menu = tk.Menu(menu_bar, tearoff=0)
        AI_menu.add_command(label="Load deep learning model for assistance", command=self.Load_deep_learning_model)
        AI_menu.add_separator()  # اضافه کردن خط جداکننده
        AI_menu.add_command(label="Apply deep learning model to the current image", command=self.Apply_deep_learning_model)
        AI_menu.add_separator()  # اضافه کردن خط جداکننده
        AI_menu.add_command(label="Apply deep learning model to All images with no BBox", command=self.Apply_deep_learning_model_to_All)
        AI_menu.add_separator()  # اضافه کردن خط جداکننده
        AI_menu.add_command(label="Check label conflict with the current image", command=self.Check_Label_Conflict)
        AI_menu.add_command(label="Check label conflict with All images", command=self.Check_All_Label_Conflict)
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=Edit_menu)
        menu_bar.add_cascade(label="Export", menu=Export_menu)
        menu_bar.add_cascade(label="Import", menu=Import_menu)
        menu_bar.add_cascade(label="Labels", menu=Labels_menu)
        menu_bar.add_cascade(label="AI Assist", menu=AI_menu)
        self.config(menu=menu_bar)

    def open_project(self):
        project_txt_path = filedialog.askopenfilename(
            title="Select Project File",
            filetypes=[("Project Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if project_txt_path:
            self.load_project_from_file(project_txt_path)

    def load_project_from_file(self, project_txt_path):
        # Clear Project Data
        self.clear_project_general_data()
        # Open project file
        try:
            with open(project_txt_path, "r", encoding="utf-8") as f:
                lines = [line.rstrip('\n') for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"Could not read project file:\n{e}")
            return
        
        if len(lines) < 4:
            messagebox.showerror("Error", "Project file format is incorrect or incomplete.")
            return

        # Parse header info
        if not lines[0].startswith("Project:"):
            messagebox.showerror("Error", "Project name not found in project file.")
            return
        self.project_data["name"] = lines[0][len("Project:"):].strip()

        if not lines[1].startswith("Project Folder:"):
            messagebox.showerror("Error", "Project folder path not found in project file.")
            return
        self.project_data["project_folder"] = lines[1][len("Project Folder:"):].strip()
        check_folder = os.path.exists(self.project_data["project_folder"])
        if not check_folder:
            self.project_data["project_folder"] = os.path.abspath(os.path.dirname(project_txt_path))
            messagebox.showinfo("Caution", f"Project folder didn't exist.\nWe suppose the current folder and continue.\n\n{self.project_data['project_folder']}")
            
        if not lines[2].startswith("Image Folder:"):
            messagebox.showerror("Error", "Image folder path not found in project file.")
            return
        self.project_data["image_folder"] = lines[2][len("Image Folder:"):].strip()
        check_folder = os.path.exists(self.project_data["image_folder"])
        if not check_folder:
            self.project_data["image_folder"] = os.path.abspath(os.path.dirname(project_txt_path)) + '\\images'
            messagebox.showinfo("Caution", f"Image folder didn't exist.\nWe suppose the default folder \"images\" and continue.\n\n{self.project_data['image_folder']}")

        if not lines[3].startswith("Path to AI:"):
            messagebox.showerror("Error", "AI assistant model path not found in project file.")
            return
        self.project_data["path_to_AI"] = lines[3][len("Path to AI:"):].strip()
        if self.project_data["path_to_AI"] != "":
            if os.path.exists(self.project_data["path_to_AI"]):
                response = messagebox.askyesno(
                    title="بارگذاری هوش مصنوعی کمکی",
                    message=f"آیا مایلید هوش مصنوعی موجود در پروژه برای کمک به لیبل گذاری بارگذاری شود<",
                    icon=messagebox.QUESTION
                )
                if response:
                    try:
                        self.model = YOLO(self.project_data["path_to_AI"])
                        self.model.eval()
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not load AI\n\n{self.project_data["path_to_AI"]}\n\nYou can load new AI later and try again\n\n{e}")
                        self.project_data["path_to_AI"] = ""
            else:
                messagebox.showinfo("Error", "AI assistant model path is was not valid.\nYou can load another later.")
                self.project_data["path_to_AI"] = ""

        # Parse images list - starting at line 4 until an empty line or "Rectangles per image:"
        i = 3
        image_files = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("Rectangles per image:"):
            line = lines[i]
            # Expected format: [N] filename
            if line.startswith('['):
                close_bracket_idx = line.find(']')
                if close_bracket_idx != -1:
                    fname = line[close_bracket_idx+1:].strip()
                    image_files.append(fname)
            i += 1
        self.project_data["images"] = image_files

        # Initialize empty rectangles list for each image
        self.project_data["rectangles"] = {img_path: [] for img_path in self.project_data["images"]}
        self.project_data["IsLocks"] = {img_path: [] for img_path in self.project_data["images"]}
        self.project_data["Labels"] = {img_path: [] for img_path in self.project_data["images"]}

        # Skip empty lines and "Rectangles per image:" header
        while i < len(lines) and (not lines[i].strip() or lines[i].startswith("Rectangles per image:")):
            i += 1

        # Parse rectangles per image
        while i < len(lines) and (not lines[i].startswith("names:")):
            line = lines[i].strip()
            if line.startswith('['):  # image line
                close_bracket_idx = line.find(']')
                if close_bracket_idx == -1:
                    i += 1
                    continue
                img_name = line[close_bracket_idx+1:].strip()
                # Find matching image path:
                img_path = None
                for p in self.project_data["images"]:
                    if os.path.basename(p) == img_name:
                        img_path = p
                        break
                i += 1
                # Read rectangles for this image (until next image or end)
                rects = []
                isLocks = []
                recLabels = []
                while i < len(lines) and (not lines[i].startswith('[')) and (not lines[i].startswith("names:")):
                    rect_line = lines[i].strip()
                    if rect_line.lower() != "no rectangles":
                        # Expected format: Rect: (x1, y1), (x2, y2)
                        if rect_line.startswith("Rect"):
                            coords_start = rect_line.find('(')
                            coords_end = rect_line.find(')')
                            coords_start2 = rect_line.find('(', coords_end)
                            coords_end2 = rect_line.find(')', coords_start2)
                            if coords_start != -1 and coords_end != -1 and coords_start2 != -1 and coords_end2 != -1:
                                try:
                                    x1, y1 = map(float, rect_line[coords_start+1:coords_end].split(','))
                                    x2, y2 = map(float, rect_line[coords_start2+1:coords_end2].split(','))
                                    rects.append((x1, y1, x2, y2))
                                except Exception:
                                    pass  # skip malformed
                            i += 1
                            if i < len(lines):
                                prop_line = lines[i].strip()
                                if prop_line.startswith('Lock'):
                                    # استخراج وضعیت قفل
                                    lock_status = lines[i].split(':=')[1].strip()  # جدا کردن قسمت بعد از ':='
                                    lock_value = lock_status.split('(')[1].split(')')[0].strip()  # استخراج مقدار داخل پرانتز
                                    # استخراج متن داخل گیومه
                                    class_text = lines[i].split('Class :=')[1].strip()  # جدا کردن قسمت بعد از 'Class :='
                                    class_value = class_text.split('"')[1]  # استخراج متن داخل گیومه
                                    isLocks.append(lock_value.lower() == 'true')
                                    recLabels.append(class_value)
                                else:
                                    messagebox.showerror("Error", "File not compatible, Every Rectangle needs a property line after it like Lock:= () Class:=\"\"")
                                    return
                                
                    i += 1


                if img_path:
                    self.project_data["rectangles"][img_path] = rects
                    self.project_data["IsLocks"][img_path] = isLocks
                    self.project_data["Labels"][img_path] = recLabels
            else:
                i += 1
        if i < len(lines) and lines[i].startswith("names:"):
            self.label_to_number = {}
            i += 1
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                # جدا کردن عدد و متن داخل ""
                if ':' in line and '"' in line:
                    parts = line.split(':', 1)  # فقط اولین : را جدا کن
                    try:
                        number = int(parts[0].strip())  # تبدیل به عدد صحیح
                    except ValueError:
                        messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                        continue
                    
                    # پیدا کردن متن داخل ""
                    text_part = parts[1].strip()
                    if text_part.count('"') >= 2:
                        start = text_part.find('"') + 1
                        end = text_part.find('"', start)
                        label = text_part[start:end]
                        if not (label in self.label_to_number):
                            # اگر label جدید است، یک عدد جدید اختصاص بده
                            self.label_to_number[label] = number
                        else:
                            messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                    else:
                        messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                else:
                    messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")

                i += 1

        # Retrieve the list of rectangles for the first image
        image_files = self.project_data["images"]
        self.populate_image_list(image_files)
        if image_files:
            self.img_index = 0
            self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]
            self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
            self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
            if self.rectangles == []:
                self.rect_index = None
                self.label_var.set("")
                self.coords = None
                self.rec_islock = None
                self.Rec_Label = None
                self.crop_canvas.delete("all")
            else:
                self.rect_index = 0
                self.coords = list(self.rectangles[self.rect_index])  # Copy for editing
                self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
                self.Rec_Label = self.Labels[self.rect_index]  # Copy for editing
            project_name = self.project_data["name"]
            self.title(f"Project Viewer: {project_name}")

            self.populate_rectangle_list()
            
            # activate first image
            self.lb1.selection_clear(0, tk.END)    # Clear any previous selection
            self.lb1.selection_set(self.img_index)              # Select the first item (index 0)
            self.lb1.activate(self.img_index)                  # Set the active item to the first one
            self.lb1.see(self.img_index)                      # Scroll to make sure the first item is visible
            self.lb1.focus_set()                 # Set keyboard focus to the listbox for better UX                
            self.display_image() # Your method to display the image number self.img_index
            self.draw_rectamgles()
            self.update_edit_panel_and_image_crop()
            self.label_entry.icursor(tk.END)  # Move cursor to end of text

        else:
            messagebox.showerror("Warning", "No image is available in the project you selected.\nAdd images if you want.", icon='warning')
        
        messagebox.showinfo("Success", "Project opened successfully")

    def new_project(self):
        # Clear Project Data

        while True:
            project_folder = filedialog.askdirectory(title="Select Base Folder for New Project")
            if not project_folder:
                return  # User cancelled folder selection
            project_folder = project_folder.replace("\\",  "/")
            project_name = simpledialog.askstring("Project Name", "Enter new project name:")
            if not project_name:
                return  # User cancelled project name input
            try:
                os.makedirs(project_folder, exist_ok=True)
                break  # Folder created successfully, exit loop
            except Exception as e:
                messagebox.showerror("Error", f"Could not create project folder:\n\n{e}")
                return


        jpg_folder = filedialog.askdirectory(title="Select Folder Containing JPG Images")
        if not jpg_folder:
            return
        image_files = [f for f in os.listdir(jpg_folder)
                    if os.path.isfile(os.path.join(jpg_folder, f)) and f.lower().endswith(".jpg")]
        
        self.clear_project_general_data()
        self.crop_canvas.delete("all")
        self.canvas.delete("all")
        self.image_tk = None
        self.lb2.delete(0, tk.END)  # Clear existing items
        self.lb1.delete(0, tk.END)  # Clear existing items

        # مسیر پوشه مقصد (project_folder/images)
        project_image_folder = os.path.join(project_folder, "images").replace("\\",  "/")

        # اگر پوشه مقصد وجود نداشت، آن را ایجاد کنید
        os.makedirs(project_image_folder, exist_ok=True)

        if jpg_folder == project_image_folder:
            messagebox.showinfo("تذکر", f"مبدا و مقصد یکسان هستند و نیازی به انتقال فایلها نیست.")
        else:
            files_moved = [] # فایلهایی که با موفقیت جابجا شده اند
            # کپی تمام فایل‌های JPG به پوشه مقصد
            for image_file in image_files:
                src_path = os.path.join(jpg_folder, image_file).replace("\\",  "/")
                dst_path = os.path.join(project_image_folder, image_file).replace("\\",  "/")

                if os.path.exists(dst_path):
                    response = messagebox.askyesnocancel(
                        title="فایل تکراری",
                        message=f"فایل '{image_file}' از قبل وجود دارد.\n\nآیا می‌خواهید جایگزین شود؟\n(Yes: جایگزینی, No: ذخیره با نام جدید, Cancel: رد کردن)",
                        icon=messagebox.WARNING
                    )
                    
                    if response is None:  # Cancel
                        pass
                    elif response:  # Yes (جایگزینی)
                        shutil.copy2(src_path, dst_path)
                        files_moved.append(image_file)
                        messagebox.showinfo("جایگزینی موفق", f"فایل '{image_file}' با موفقیت جایگزین شد.")
                    else:  # No (ذخیره با نام جدید)
                        new_name = simpledialog.askstring(
                            "نام جدید",
                            f"نام جدید برای فایل '{image_file}' وارد کنید:",
                            initialvalue=image_file
                        )
                        if new_name:
                            if not new_name.lower().endswith('.jpg'):
                                new_name += '.jpg'
                            new_dst_path = os.path.join(project_image_folder, new_name).replace("\\",  "/")
                            shutil.copy2(src_path, new_dst_path)
                            files_moved.append(new_name)
                            messagebox.showinfo("ذخیره موفق", f"فایل با نام جدید '{new_name}' ذخیره شد.")
                else:
                    shutil.copy2(src_path, dst_path)
                    files_moved.append(image_file)

        # به روز رسانی لیست تصاویر در فولدر جدید ساخته شده
        image_files = files_moved
        # initialize project global information
        self.project_data["name"] = project_name
        self.project_data["project_folder"] = project_folder
        self.project_data["image_folder"] = project_image_folder
        self.project_data["path_to_AI"] = ""
        self.Load_deep_learning_model()

        project_txt_path = os.path.join(project_folder, self.project_data["name"] + '_project.txt').replace("\\",  "/")
        i = 0
        while os.path.isfile(project_txt_path):
            self.project_data["name"] += f'_{i}'
            project_txt_path = os.path.join(project_folder, self.project_data["name"] + '_project.txt').replace("\\",  "/")

        try:
            with open(project_txt_path, "w", encoding="utf-8") as f:
                f.write(f"Project: {project_name}\n\n")
                f.write(f"Project Folder: {project_folder}\n\n")
                f.write(f"Image Folder: {project_image_folder}\n\n")
                f.write(f"Path to AI: {self.project_data['path_to_AI']}\n\n")

                # Write images list
                for index, fname in enumerate(image_files, start=1):
                    f.write(f"[{index}] {fname}\n")

                f.write("\nRectangles per image:\n")

                # Write rectangles - empty initially
                for index, fname in enumerate(image_files, start=1):
                    f.write(f"\t[{index}] {fname}\n")
                    f.write("\n")
            
                f.write("\nnames:\n")
            self.project_data["images"] = image_files

            # Initialize empty rectangles list for each image
            self.project_data["rectangles"] = {img_path: [] for img_path in self.project_data["images"]}
            self.project_data["IsLocks"] = {img_path: [] for img_path in self.project_data["images"]}
            self.project_data["Labels"] = {img_path: [] for img_path in self.project_data["images"]}

            project_name = self.project_data["name"]
            self.title(f"Project Viewer: {project_name}")

            self.populate_image_list(image_files)
            if image_files:
                self.img_index = 0
                self.display_image() # Your method to display the image number self.img_index
                # activate first image
                self.lb1.selection_clear(0, tk.END)    # Clear any previous selection
                self.lb1.selection_set(self.img_index)              # Select the first item (index 0)
                self.lb1.activate(self.img_index)                  # Set the active item to the first one
                self.lb1.see(self.img_index)                      # Scroll to make sure the first item is visible
                self.lb1.focus_set()                 # Set keyboard focus to the listbox for better UX                

                self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]
                self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
                self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
                self.rect_index = None
                self.label_var.set("")
                self.populate_rectangle_list()
                self.crop_canvas.delete("all")
            else:
                messagebox.showerror("Warning", "No image is available in the folder you selected.\nAdd images if you want.", icon='warning')
            
            messagebox.showinfo(
                "عملیات کامل شد",
                f"عملیات ایجاد پروژه جدید با موفقیت انجام شد.\nتعداد فایل‌های منتقل شده به فولدر تصاویر پروژه : {len(image_files)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not initialize a new project properly:\n{e}")

    def Add_New_Image_to_Project(self):
        new_image_files = filedialog.askopenfilenames(
            title="Select New Image Files",
            filetypes=[("Project Text Files", "*.jpg"), ("All Files", "*.*")]
        )

        responce_import_BBoxes = messagebox.askyesno(
            title="اشیاء متناظر با عکس",
            message="فایل‌های متنی هم نام را برای اضافه کردن به پروژه بررسی کنم؟",
            icon=messagebox.WARNING
        )
        for image_file in new_image_files:
            # استخراج مسیر دایرکتوری
            jpg_folder = os.path.dirname(image_file)
            fname = os.path.basename(image_file)

            # ساخت مسیر فایل متن متناظر
            txt_path = os.path.join(jpg_folder, os.path.splitext(fname)[0] + '.txt').replace("\\",  "/")
            # بررسی وجود فایل متن
            responce_import_BBox_file = None
            resp = None
            if os.path.exists(txt_path) and responce_import_BBoxes:
                responce_import_BBox_file = messagebox.askyesno(
                    title="اشیاء متناظر با عکس",
                    message=f"کنار تصویر {fname} یک فایل متنی به همان نام پیدا شد \nممکن است حاوی لیست اشیاء دیده شده در تصویر باشد.\nآیا مایل هستید محتوای این فایل تا جای ممکنه به پروژه اضافه شود؟",
                    icon=messagebox.WARNING
                )

            if jpg_folder == self.project_data["image_folder"]:
                if not fname in self.project_data["images"]:
                    self.project_data["rectangles"][fname] = [] 
                    self.project_data["IsLocks"][fname] = [] 
                    self.project_data["Labels"][fname] = [] 

                    image_files = self.project_data["images"]
                    image_files.append(fname)
                    self.project_data["images"] = image_files
                    resp = True

            else:
            # کپی تمام فایل‌های JPG به پوشه مقصد
                src_path = os.path.join(jpg_folder, fname).replace("\\",  "/")
                dst_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")

                if os.path.exists(dst_path):
                    response = messagebox.askyesnocancel(
                        title="فایل تکراری",
                        message=f"فایل '{image_file}' از قبل وجود دارد.\n\nآیا می‌خواهید جایگزین شود؟\n(Yes: جایگزینی, No: ذخیره با نام جدید, Cancel: رد کردن)",
                        icon=messagebox.WARNING
                    )
                    
                    if response is None:  # Cancel
                        pass
                    elif response:  # Yes (جایگزینی)
                        shutil.copy2(src_path, dst_path)
                        messagebox.showinfo("جایگزینی موفق", f"فایل '{image_file}' با موفقیت جایگزین شد.")
                        self.project_data["rectangles"][fname] = [] 
                        self.project_data["IsLocks"][fname] = [] 
                        self.project_data["Labels"][fname] = [] 

                        if not fname in self.project_data["images"]:
                            image_files = self.project_data["images"]
                            image_files.append(fname)
                            self.project_data["images"] = image_files
                        resp = True
                    else:  # No (ذخیره با نام جدید)
                        name, ext = os.path.splitext(fname)  # جدا کردن نام و پسوند
                        i = 1
                        new_dst_path = dst_path
                        while os.path.exists(new_dst_path):
                            new_dst_path = os.path.join(self.project_data["image_folder"], f"{name}_{i}{ext}").replace("\\",  "/")
                            i += 1

                        new_fname = f"{name}_{i-1}{ext}"      # ساخت نام جدید
                        new_name = simpledialog.askstring(
                            "نام جدید",
                            f"نام جدید برای فایل '{image_file}' وارد کنید:",
                            initialvalue = new_fname
                        )
                        if new_name:
                            if not new_name.lower().endswith('.jpg'):
                                new_name += '.jpg'
                            new_dst_path = os.path.join(self.project_data["image_folder"], new_name).replace("\\",  "/")
                            shutil.copy2(src_path, new_dst_path)
                            messagebox.showinfo("ذخیره موفق", f"فایل با نام جدید '{new_name}' ذخیره شد.")
                            self.project_data["rectangles"][new_name] = [] 
                            self.project_data["IsLocks"][new_name] = [] 
                            self.project_data["Labels"][new_name] = [] 
                            
                            if not new_name in self.project_data["images"]:
                                image_files = self.project_data["images"]
                                image_files.append(new_name)
                                self.project_data["images"] = image_files
                            fname = new_name
                            resp = True
                else:
                    shutil.copy2(src_path, dst_path)
                    self.project_data["rectangles"][fname] = [] 
                    self.project_data["IsLocks"][fname] = [] 
                    self.project_data["Labels"][fname] = [] 

                    image_files = self.project_data["images"]
                    image_files.append(fname)
                    self.project_data["images"] = image_files
                    resp = True

            if responce_import_BBox_file and resp != None:
                rects = []
                isLocks = []
                Labels = []
                try:
                    with open(txt_path, "r", encoding="utf-8") as f:
                        lines = [line.rstrip('\n') for line in f if line.strip()]

                    for i, rect_line in enumerate(lines):

                        try:
                            parts = rect_line.strip().split()
                            if len(parts) == 6:  # بررسی تعداد المان‌ها
                                label_txt, x_center, y_center, width, height, score = parts
                            elif len(parts) == 5:  # بررسی تعداد المان‌ها
                                label_txt, x_center, y_center, width, height = parts
                            else:
                                messagebox.showerror('Error', f"خطا در فرمت خط {i}: {rect_line}")
                                continue
                            label = ""
                            for labeli in self.label_to_number:
                                if int(label_txt) == self.label_to_number[labeli]:
                                    label = labeli
                            x_center, y_center, width, height =  map(float, (x_center, y_center, width, height))
                            x1 = x_center - width / 2
                            x2 = x_center + width / 2
                            y1 = y_center - height / 2
                            y2 = y_center + height / 2

                            rects.append((x1,y1,x2,y2))
                            Labels.append(label)
                            isLocks.append(False)
                        except Exception as e:
                            messagebox.showerror('Error', f"خطا در پردازش خط {i}: {str(e)}")
                            continue
                except Exception as e:
                    pass
                self.project_data["rectangles"][fname] = rects
                self.project_data["IsLocks"][fname] = isLocks
                self.project_data["Labels"][fname] = Labels

            

        self.populate_image_list(image_files)
        self.img_index = len(image_files) - 1
        self.display_image() # Your method to display the image number self.img_index
        # activate last new image
        self.lb1.selection_clear(0, tk.END)    # Clear any previous selection
        self.lb1.selection_set(self.img_index)              # Select the first item (index 0)
        self.lb1.activate(self.img_index)                  # Set the active item to the first one
        self.lb1.see(self.img_index)                      # Scroll to make sure the first item is visible
        self.lb1.focus_set()                 # Set keyboard focus to the listbox for better UX                

        self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]
        self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
        self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
        if self.rectangles == []:
            self.rect_index = None
            self.label_var.set("")
        else:
            self.rect_index = 0
       
        self.populate_rectangle_list()
        self.update_edit_panel_and_image_crop()
        self.label_entry.focus_set()
        self.label_entry.icursor(tk.END)  # Move cursor to end of text
  
        messagebox.showinfo(
            "عملیات کامل شد",
            f"عملیات اضافه کردن تصاویر جدید با موفقیت انجام شد.\nتعداد تصویر پردازش شده: {len(image_files)}")


    def delete_image_from_project(self):
        if self.img_index != None:
            fname = self.project_data["images"][self.img_index]
            response = messagebox.askyesnocancel(
                title="حذف یک تصویر از پروژه",
                message=f"آیا از حذف تصویر زیر مطمئن هستید؟ \n\n {fname}",
                icon=messagebox.WARNING
            )
            if response:
                del self.project_data["rectangles"][fname]
                del self.project_data["IsLocks"][fname]
                del self.project_data["Labels"][fname]
                del self.project_data["images"][self.img_index]

                response = messagebox.askyesnocancel(
                    title="حذف تصویر از فولدر",
                    message=f"آیا تصویر زیر در فولدر تصاویر پروژه نیز نگه داشته شود؟ \n\n {fname}",
                    icon=messagebox.WARNING
                )
                if not response:
                    try:
                        os.remove(os.path.join(self.project_data["image_folder"], fname)).replace("\\",  "/")
                    except Exception as e:
                        messagebox.showerror(title="Image Delete Error", message=f"Couldn't delet the image from the project images folder:\n{e}")

                if len(self.project_data["images"]) > 0:
                    self.img_index = min(len(self.project_data["images"]) - 1, self.img_index)
                else:
                    self.img_index = None
                    self.rect_index = None
                    self.label_var.set("")

                image_files = self.project_data["images"]
                self.populate_image_list(image_files)
                if self.img_index != None:
                    self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]
                    self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
                    self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
                    if self.rectangles == []:
                        self.rect_index = None
                        self.label_var.set("")
                        self.coords = None
                        self.rec_islock = None
                        self.Rec_Label = None
                        self.crop_canvas.delete("all")
                    else:
                        self.rect_index = 0
                        self.coords = list(self.rectangles[self.rect_index])  # Copy for editing
                        self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
                        self.Rec_Label = self.Labels[self.rect_index]  # Copy for editing

                    self.populate_rectangle_list()
                    
                    # activate first image
                    self.lb1.selection_clear(0, tk.END)    # Clear any previous selection
                    self.lb1.selection_set(self.img_index)              # Select the first item (index 0)
                    self.lb1.activate(self.img_index)                  # Set the active item to the first one
                    self.lb1.see(self.img_index)                      # Scroll to make sure the first item is visible
                    self.lb1.focus_set()                 # Set keyboard focus to the listbox for better UX                

                    # Reset Zoom
                    self.zoom_factor = 1 # Zoom factor
                    self.crop_cords = [0, 0 , 1, 1] #Crop coordinations used for zoom
                    self.display_image() # Your method to display the image number self.img_index
                    self.draw_rectamgles()
                    self.update_edit_panel_and_image_crop()
                    self.label_entry.icursor(tk.END)  # Move cursor to end of text

                else:
                    self.canvas.delete("all")
                    self.image_tk = None
                    messagebox.showerror("Error", "No image is available in the project you selected.")
                    return
                
        else:
            return

    def save_project(self):
        """Save the current project data to a text file."""
        # Default file path is the same as the opened project
        default_file_path = self.project_data.get("file_path", "")  # Assuming you store the opened file path

        # Ask user for file path to save the project
        project_txt_path = filedialog.asksaveasfilename(
            title="Save Project File",
            defaultextension=".txt",
            initialfile=os.path.basename(default_file_path) if default_file_path else (self.project_data["name"] + '_project.txt'),
            filetypes=[("Project Text Files", "*.txt"), ("All Files", "*.*")]
        )

        current_number = len(self.label_to_number)  # شمارنده برای labelهای جدید

        # شروع شمارش تعداد تکرار لیبلها
        label_counter = {}
        for label in self.label_to_number:
            label_counter[label] = 0

        if project_txt_path:
            folder_path = os.path.dirname(project_txt_path)
            try:
                with open(project_txt_path, "w", encoding="utf-8") as f:
                    # Write project name
                    f.write(f"Project: {self.project_data['name']}\n\n")
                    # Write project folder
                    f.write(f"Project Folder: {folder_path}\n\n")
                    # Write image folder
                    f.write(f"Image Folder: {folder_path + '/images'}\n\n")
                    # Write path to AI assitant model
                    if self.project_data['path_to_AI'] == "":
                        f.write(f"Path to AI: \n\n")
                    else:
                        f.write(f"Path to AI: {folder_path + '/' + os.path.basename(self.project_data['path_to_AI'])}\n\n")

                    # Write images list with index
                    for idx, image_file in enumerate(self.project_data["images"], start=1):
                        f.write(f"[{idx:03d}] {image_file}\n")
                    
                    f.write("\nRectangles per image:\n")
                    
                    # Write rectangles for each image
                    for idx, image_file in enumerate(self.project_data["images"], start=1):
                        f.write(f"[{idx:03d}] {image_file}\n")
                        rects = self.project_data["rectangles"][image_file]
                        Locks = self.project_data["IsLocks"][image_file]
                        Labels = self.project_data["Labels"][image_file]
                        if rects:
                            for rcs, (x1, y1, x2, y2) in enumerate(rects):
                                f.write(f"\tRect: ({x1:.6f}, {y1:.6f}), ({x2:.6f}, {y2:.6f})\n")
                                label = Labels[rcs]
                                f.write(f"\t\tLock := ({Locks[rcs]})  \tClass := \"{label}\" \n")
                                if not (label in self.label_to_number):
                                    # اگر label جدید است، یک عدد جدید اختصاص بده
                                    self.label_to_number[label] = current_number
                                    label_counter[label] = 0
                                    current_number += 1
                                label_counter[label] += 1    
                            f.write("\n")
                        else:
                            f.write("\n")  # If no rectangles, just add a new line

                    f.write("\nnames:\n")  # List of label names
                    for label in self.label_to_number:
                        f.write(f"{self.label_to_number[label]:02d}: \"{label}\"".ljust(16) + f" times appeared = {label_counter[label]:>4d} \n")
                    f.write("\n")  # End of file
                                    
                    # move images
                    try:
                        jpg_folder = self.project_data["image_folder"].replace("\\",  "/")
                        dst_folder = os.path.join(folder_path, 'images').replace("\\",  "/")
                        os.makedirs(dst_folder, exist_ok=True)
                        if os.path.exists(dst_folder) and os.path.exists(jpg_folder):
                            for image_file in self.project_data["images"]:
                                scr_path = os.path.join(jpg_folder, image_file)
                                dst_path = os.path.join(dst_folder, image_file)
                                if scr_path !=  dst_path:
                                    if os.path.isfile(scr_path):
                                        if os.path.isfile(dst_path):
                                            # بررسی هم‌نام و هم‌اندازه بودن فایل‌ها
                                            if (os.path.getsize(scr_path) == os.path.getsize(dst_path) and 
                                                os.path.getctime(scr_path) == os.path.getctime(dst_path)):
                                                # فایل‌ها یکسان هستند - نیازی به کپی نیست
                                                continue
                                            else:
                                                # فایل‌ها هم‌نام ولی با اندازه‌های متفاوت هستند -> هشدار بده
                                                messagebox.showinfo('Warning', 
                                                    f'{image_file} already exists in destination folder with different size!\n'
                                                    f'Source size: {os.path.getsize(scr_path)} bytes\n'
                                                    f'Destination size: {os.path.getsize(dst_path)} bytes', 
                                                    icon='warning')
                                                try:
                                                    shutil.copy2(scr_path, dst_path)
                                                except PermissionError:
                                                    messagebox.showwarning('Warning', 
                                                        f'Cannot copy {image_file} because it is being used by this program in image panel.\n'
                                                        f'Please repeat SavaAs when another image is shown in panel', 
                                                        icon='warning')
                                                    return
                                        else:
                                            # فایل در مقصد وجود ندارد -> کپی کن
                                            shutil.copy2(scr_path, dst_path)
                                    else:
                                        messagebox.showinfo('Warning', 
                                            f'{image_file} not found in source folder!\n You will have to add it manually or delete it from image list.', 
                                            icon='warning')
                        else:
                            messagebox.showinfo('Error', 'Source or destination folder for images doesnt Exist!', icon='error')
                            return
                        
                        messagebox.showinfo("Success", "Project saved successfully.\n اگر قصد دارید پروژه‌ای را که اخیرا ذخیره کرده اید ویرایش کنید باید آنرا باز کنید. در غیر این صورت فایل قدیم پروژه ویرایش خواهد شد. مگر اینکه مبدا و مقصد یکی بوده باشند.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Error happend during SaveAs operation\n{image_file}\n{e}", icon='error')
            except Exception as e:
                messagebox.showerror("Error", f"Could not save project comletely:\n{e}\nlast image moved is: {image_file}")
        else:
            project_txt_path = None
        return project_txt_path

    def Auto_save_project(self):
        """Auto Save the project data to a text file for backup."""
        # Default file path is the same as the opened project
        default_file_path = self.project_data["project_folder"]

        # file path to Backup the project
        if default_file_path:
            project_txt_path = os.path.join(default_file_path, self.project_data["name"] + '_project_Auto_Save.txt').replace("\\",  "/")
        else:
            messagebox.showwarning('Warning', 'could not backup the project', icon='warning')

        current_number = len(self.label_to_number)  # شمارنده برای labelهای جدید

        # شروع شمارش تعداد تکرار لیبلها
        label_counter = {}
        for label in self.label_to_number:
            label_counter[label] = 0

        if project_txt_path:
            folder_path = os.path.dirname(project_txt_path)
            try:
                with open(project_txt_path, "w", encoding="utf-8") as f:
                    # Write project name
                    f.write(f"Project: {self.project_data['name']}\n\n")
                    # Write project folder
                    f.write(f"Project Folder: {folder_path}\n\n")
                    # Write image folder
                    f.write(f"Image Folder: {folder_path + '/images'}\n\n")
                    # Write path to AI assitant model
                    if self.project_data['path_to_AI'] == "":
                        f.write(f"Path to AI: \n\n")
                    else:
                        f.write(f"Path to AI: {folder_path + '/' + os.path.basename(self.project_data['path_to_AI'])}\n\n")

                    # Write images list with index
                    for idx, img in enumerate(self.project_data["images"], start=1):
                        f.write(f"[{idx:02d}] {img}\n")
                    
                    f.write("\nRectangles per image:\n")
                    
                    # Write rectangles for each image
                    for idx, img in enumerate(self.project_data["images"], start=1):
                        f.write(f"[{idx:02d}] {img}\n")
                        rects = self.project_data["rectangles"][img]
                        Locks = self.project_data["IsLocks"][img]
                        Labels = self.project_data["Labels"][img]
                        if rects:
                            for rcs, (x1, y1, x2, y2) in enumerate(rects):
                                f.write(f"\tRect: ({x1:.6f}, {y1:.6f}), ({x2:.6f}, {y2:.6f})\n")
                                label = Labels[rcs]
                                f.write(f"\t\tLock := ({Locks[rcs]})  \tClass := \"{label}\" \n")
                                if not (label in self.label_to_number):
                                    # اگر label جدید است، یک عدد جدید اختصاص بده
                                    self.label_to_number[label] = current_number
                                    label_counter[label] = 0
                                    current_number += 1
                                label_counter[label] += 1    
                            f.write("\n")
                        else:
                            f.write("\n")  # If no rectangles, just add a new line

                    f.write("\nnames:\n")  # List of label names
                    for label in self.label_to_number:
                        f.write(f"{self.label_to_number[label]:02d}: \"{label}\"".ljust(16) + f" times appeared = {label_counter[label]:>4d} \n")
                    f.write("\n")  # End of file
      
            except:
                messagebox.showwarning('Warning', 'could not backup the project truly', icon='warning')
        else:
            project_txt_path = None
        return project_txt_path

    def clear_project_general_data(self):
        self.project_data = {
            "name": "",               # Project name (str)
            "project_folder": "",     # Project folder path (str)
            "image_folder": "",       # Folder where images are located (str)
            "path_to_AI": "",         # path to AI assistant model *.pt
            "images": [],             # List of image full paths (list of str)
            "rectangles": {},         # Dict of {image_path: [ (x1, y1, x2, y2), ... ] }
            "IsLocks": {},            # List of Lock boolian values for each Rectangle
            "Labels": {}              # List of Label name values for each Rectangle
        }
        self.model = None
        self.image_tk = None  # Keep reference to avoid GC
        self.start_x = None
        self.start_y = None
        self.rect = None # canvas rectangle id during drawing
        self.rec_IDs = [] # ids for the current rectangles
        self.original_image = None
        self.image_full_path = None
        self.rectangles = []
        self.IsLocks = []
        self.Labels = []
        self.img_index = None # index of drawn image in left convas
        self.rect_index = None # index of rectangle selected in right list
        self.label_var.set("")
        self.coords = [] # Coordinates of the selected rectangle
        self.rec_islock = None
        self.Rec_Label = None
        self.zoom_factor = 1 # Zoom factor
        self.crop_cords = [0, 0 , 1, 1] #Crop coordinations used for zoom
        self.label_to_number = {}
        self.canvas.delete("all")
        self.char_sequense = ""



    def _setup_widgets(self):
        main_frame = ttk.Frame(self, padding=10, style='TFrame', width=1000, height=800)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame: contains buttons (top) and canvas (bottom)
        self.left_frame = ttk.Frame(main_frame, width=750, height=500, style='Side.TFrame')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.left_frame.pack_propagate(False)

        # Button frame (under menu, above canvas)
        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)

        # self.split_button = ttk.Button(btn_frame, text="Split", command=self.Split_images_by_BoundingBoxes)
        # self.split_button.pack(side=tk.LEFT, padx=5)


        button3 = ttk.Button(btn_frame, text="←↕→", command=self.Zoom_in, width=4)
        button3.pack(side=tk.LEFT, padx=2)

        button4 = ttk.Button(btn_frame, text="→←", command=self.Zoom_out, width=4)
        button4.pack(side=tk.LEFT, padx=2)

        # Arrow Buttons
        up_button = ttk.Button(btn_frame, text="↑", command=self.move_up, width=2)
        up_button.pack(side=tk.LEFT, padx=1)
        down_button = ttk.Button(btn_frame, text="↓", command=self.move_down, width=2)
        down_button.pack(side=tk.LEFT, padx=1)
        left_button = ttk.Button(btn_frame, text="←", command=self.move_left, width=2)
        left_button.pack(side=tk.LEFT, padx=1)
        right_button = ttk.Button(btn_frame, text="→", command=self.move_right, width=2)
        right_button.pack(side=tk.LEFT, padx=1)
        delete_image = ttk.Button(btn_frame, text="delete image", command=self.delete_image_from_project, width=12)
        delete_image.pack(side=tk.RIGHT, padx=2)
        self.apply_ai = ttk.Button(btn_frame, text="Apply AI", command=self.Apply_deep_learning_model, width=8)
        self.apply_ai.pack(side=tk.RIGHT, padx=2)
        Backup = ttk.Button(btn_frame, text="Backup", command=self.Auto_save_project, width=8)
        Backup.pack(side=tk.RIGHT, padx=2)
        save = ttk.Button(btn_frame, text="Save As", command=self.save_project, width=8)
        save.pack(side=tk.RIGHT, padx=2)



        # Entry for Search text (اضافه شده)
        self.char_sequense2 = tk.StringVar()
        self.char_sequense2.set("")  # مقدار اولیه خالی
        self.Search_entry = ttk.Entry(
            btn_frame,
            textvariable=self.char_sequense2,
            width=15,
            validate="key",
            validatecommand=(self.register(self.validate_label_entry2), '%P'), 
            font=('Tahoma', 10)
        )
        self.Search_entry.pack(side=tk.RIGHT, padx=2)

        Search = ttk.Button(btn_frame, text="🔎", command=self.Find_Persian_character_sequense2, width=3)
        Search.pack(side=tk.RIGHT, padx=2)

        # Canvas for image & rectangles - below buttons
        self.canvas = tk.Canvas(self.left_frame, bg='white', width=700, height=550)
        self.canvas.pack( padx=5, pady=5)

        # Bind canvas resize to redraw image and rectangles appropriately
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        # Bind canvas events for drawing rectangles
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind('<Motion>', self.draw_cross_lines)
        self.canvas.bind("<Leave>", self.on_leave_image_canvas)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # بایند کردن چرخش غربیلک
        # اتصال رویدادهای درگ تصویر با کلیک راست
        self.canvas.bind("<Button-3>", self.start_drag)  # کلیک راست
        self.canvas.bind("<B3-Motion>", self.on_drag)    # درگ با کلیک راست
        self.canvas.bind("<ButtonRelease-3>", self.end_drag)  # رها کردن کلیک راست

        # Right frame with 2 columns for lists and a box below for correction
        self.right_frame = ttk.Frame(main_frame, style='TFrame')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))


        # 1. فریمی برای نگهداری frame1 و frame2 کنار هم
        self.list_container = ttk.Frame(self.right_frame)
        self.list_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # ارتفاع بر اساس محتوا

        # تنظیم سیستم grid برای توزیع فضای مناسب
        self.list_container.grid_columnconfigure(0, weight=3, minsize=200, pad=0)  # وزن 2 برای lb1
        self.list_container.grid_columnconfigure(1, weight=1, minsize=140, pad=0)  # وزن 1 برای lb2
        self.list_container.grid_rowconfigure(0, weight=1)

        # Frame 1: List of images (عرض دو برابر)
        frame1 = ttk.Frame(self.list_container, style='Listbox.TFrame')
        frame1.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=(0, 5))

        image_label = ttk.Label(frame1, text="Images", font=('Segoe UI', 10))
        image_label.pack(pady=(2, 1))

        # --- add a scrollable container for Images list ---
        list1_container = ttk.Frame(frame1, style='Listbox.TFrame')
        list1_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lb1 = tk.Listbox(list1_container, relief=tk.FLAT, borderwidth=0, font=('Segoe UI', 10),
                              activestyle='none', selectbackground='#2563eb', selectforeground='white',
                              exportselection=False)
        self.lb1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb1 = ttk.Scrollbar(list1_container, orient="vertical", command=self.lb1.yview)
        sb1.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb1.configure(yscrollcommand=sb1.set)

        # smooth scrolling with mouse wheel
        self.lb1.bind("<MouseWheel>", lambda e: self.lb1.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.lb1.bind("<Button-4>", lambda e: self.lb1.yview_scroll(-1, "units"))  # Linux up
        self.lb1.bind("<Button-5>", lambda e: self.lb1.yview_scroll(1, "units"))   # Linux down
        # Bind selection events; only first list will select images, 2nd list manages rectangles
        self.lb1.bind("<<ListboxSelect>>", self.on_file_select)
        # اتصال رویداد رها کردن دکمه موس به تابع
        self.lb1.bind('<ButtonRelease-1>', self.on_listbox_release)


        # Frame 2: List of Bounding Boxes (عرض معمولی)
        frame2 = ttk.Frame(self.list_container, style='Listbox.TFrame')
        frame2.grid(row=0, column=1, sticky='nsew', padx=(5, 5), pady=(0, 5))

        rectangle_label = ttk.Label(frame2, text="Bounding Boxes", font=('Segoe UI', 10))
        rectangle_label.pack(pady=(2, 1))

        # --- add a scrollable container for Bounding Boxes list ---
        list2_container = ttk.Frame(frame2, style='Listbox.TFrame')
        list2_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lb2 = tk.Listbox(list2_container, relief=tk.FLAT, borderwidth=0, font=('Segoe UI', 10),
                              activestyle='none', selectbackground='#2563eb', selectforeground='white',
                              exportselection=False)
        self.lb2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb2 = ttk.Scrollbar(list2_container, orient="vertical", command=self.lb2.yview)
        sb2.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb2.configure(yscrollcommand=sb2.set)

        # smooth scrolling with mouse wheel
        self.lb2.bind("<MouseWheel>", lambda e: self.lb2.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.lb2.bind("<Button-4>", lambda e: self.lb2.yview_scroll(-1, "units"))  # Linux up
        self.lb2.bind("<Button-5>", lambda e: self.lb2.yview_scroll(1, "units"))   # Linux down
        self.lb2.bind("<<ListboxSelect>>", self.on_rectangle_select)
        self.lb2.bind("<Button-3>", self.on_rectangle_right_click)  # Bind right-click event
        # اتصال رویداد رها کردن دکمه موس به تابع
        self.lb2.bind('<ButtonRelease-1>', self.on_listbox_release)

        MoveUp_button = ttk.Button(frame2, text="↑", padding=0, width=5, command=self.move_rectangle_up)
        MoveUp_button.pack(side=tk.LEFT, padx=0)
        Auto_sort = ttk.Button(frame2, text="⇊ Sort ⇇", padding=0, width=10, command=self.Auto_sort_rectangles)
        Auto_sort.pack(side=tk.LEFT, expand=True, padx=0)
        MoveDown_button = ttk.Button(frame2, text="↓", padding=0, width=5, command=self.move_rectangle_down)
        MoveDown_button.pack(side=tk.RIGHT, padx=0)


        # 2. حالا فریم سوم با ارتفاع 300 زیر لیست‌ها اضافه شود
        self.frame3 = ttk.Frame(self.right_frame, style='Listbox.TFrame', height=400)
        self.frame3.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=5, pady=(5, 0))
        self.frame3.pack_propagate(False)  # جلوگیری از تغییر ارتفاع با محتوا
       
        # تنظیم سیستم grid برای توزیع فضای مناسب
        self.frame3.grid_columnconfigure(0, weight=0, minsize=200, pad=0)  # وزن 1 برای edit_frame
        self.frame3.grid_columnconfigure(1, weight=1, pad=0)  # وزن 2 برای canvas_frame
        self.frame3.grid_rowconfigure(0, weight=1)

        # Left Frame: Image Preview
        self.canvas_frame = tk.Frame(self.frame3, height=350, bg="#dddddd")
        self.canvas_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 5), pady=(5, 5))
        # bind رویداد تغییر اندازه
        self._resize_timer = None
        self.canvas_frame.bind("<Configure>", self._handle_resize)

        # Canvas for Image Preview
        self.crop_canvas = tk.Canvas(self.canvas_frame, width=100, height=100, bg="#dddddd", highlightthickness=0)
        self.crop_canvas.pack(expand=True, fill=tk.BOTH, padx=(5, 5), pady=(5, 5))
        self.crop_canvas.grid_propagate(False)

        # Right Frame: Arrow Buttons
        self.edit_frame = tk.Frame(self.frame3, height=350, bg="#f0f0f0")
        self.edit_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        # 1. غیرفعال کردن تغییر اندازه خودکار
        self.edit_frame.grid_propagate(False)

        self.top_frame = tk.Frame(self.edit_frame, bg="#f0f0f0")
        self.top_frame.pack(pady=2)

        # در این قسمت دکمه‌های تنظیم دقیق‌تر کادر دور شیء ایجاد می‌شوند. این دکمه‌ها قابلیت اسکرول هم دارند
        button_width = 6
        # Top Frame
        self.left_top_button = ttk.Button(self.top_frame, text="↑", padding=0, width=button_width+3, command=self.move_top_up)
        self.left_top_button.pack(side=tk.TOP, padx=1)
        self.left_top_button.bind("<MouseWheel>", self.on_top_scroll)
        self.left_top_button.bind("<Button-4>", self.on_top_scroll_up)  # برای لینوکس/مک
        self.left_top_button.bind("<Button-5>", self.on_top_scroll_down)  # برای لینوکس/مک


        self.right_top_button = ttk.Button(self.top_frame, text="Top\n  ↓ ", padding=0, width=button_width+3, command=self.move_top_down)
        self.right_top_button.pack(side=tk.TOP, padx=1)
        self.right_top_button.bind("<MouseWheel>", self.on_top_scroll)
        self.right_top_button.bind("<Button-4>", self.on_top_scroll_up)  # برای لینوکس/مک
        self.right_top_button.bind("<Button-5>", self.on_top_scroll_down)  # برای لینوکس/مک

        # Left Frame
        self.left_frame2 = tk.Frame(self.edit_frame, bg="#f0f0f0")
        self.left_frame2.pack(side=tk.TOP, pady=2)

        self.up_left_button = ttk.Button(self.left_frame2, text="←", padding=0, width=button_width-3, command=self.move_left_left)
        self.up_left_button.pack(side=tk.LEFT, padx=0)
        self.up_left_button.bind("<MouseWheel>", self.on_left_scroll)
        self.up_left_button.bind("<Button-4>", self.on_left_scroll_up)  # برای لینوکس/مک
        self.up_left_button.bind("<Button-5>", self.on_left_scroll_down)  # برای لینوکس/مک

        self.down_left_button = ttk.Button(self.left_frame2, text="Left →", padding=0, width=button_width+2, command=self.move_left_right)
        self.down_left_button.pack(side=tk.LEFT,  padx=(0, 10))
        self.down_left_button.bind("<MouseWheel>", self.on_left_scroll)
        self.down_left_button.bind("<Button-4>", self.on_left_scroll_up)  # برای لینوکس/مک
        self.down_left_button.bind("<Button-5>", self.on_left_scroll_down)  # برای لینوکس/مک

        # Right Frame
        self.up_right_button = ttk.Button(self.left_frame2, text="← Right", padding=0, width=button_width+2, command=self.move_right_left)
        self.up_right_button.pack(side=tk.LEFT, padx=(10, 0))
        self.up_right_button.bind("<MouseWheel>", self.on_right_scroll)
        self.up_right_button.bind("<Button-4>", self.on_right_scroll_up)  # برای لینوکس/مک
        self.up_right_button.bind("<Button-5>", self.on_right_scroll_down)  # برای لینوکس/مک

        self.down_right_button = ttk.Button(self.left_frame2, text="→", padding=0, width=button_width-3, command=self.move_right_right)
        self.down_right_button.pack(side=tk.LEFT,  padx=0)
        self.down_right_button.bind("<MouseWheel>", self.on_right_scroll)
        self.down_right_button.bind("<Button-4>", self.on_right_scroll_up)  # برای لینوکس/مک
        self.down_right_button.bind("<Button-5>", self.on_right_scroll_down)  # برای لینوکس/مک

        # Bottom Frame
        self.bottom_frame = tk.Frame(self.edit_frame, bg="#f0f0f0")
        self.bottom_frame.pack(side=tk.TOP, pady=2)

        self.left_bottom_button = ttk.Button(self.bottom_frame,padding=0,  text="     ↑\nBottom", width=button_width+3, command=self.move_bottom_up)
        self.left_bottom_button.pack(side=tk.TOP, padx=1)
        self.left_bottom_button.bind("<MouseWheel>", self.on_But_scroll)
        self.left_bottom_button.bind("<Button-4>", self.on_But_scroll_up)  # برای لینوکس/مک
        self.left_bottom_button.bind("<Button-5>", self.on_But_scroll_down)  # برای لینوکس/مک

        self.right_bottom_button = ttk.Button(self.bottom_frame, text="↓",padding=0, width=button_width+3, command=self.move_bottom_down)
        self.right_bottom_button.pack(side=tk.TOP,  padx=1)
        self.right_bottom_button.bind("<MouseWheel>", self.on_But_scroll)
        self.right_bottom_button.bind("<Button-4>", self.on_But_scroll_up)  # برای لینوکس/مک
        self.right_bottom_button.bind("<Button-5>", self.on_But_scroll_down)  # برای لینوکس/مک

        # ایجاد متن توضیحی زیر دکمه
        self.bottom_button_label = tk.Label(
            self.bottom_frame, 
            text="Click or hold Control\nand Scroll on Buttons",
            font=("Tahoma", 8),
            fg="gray"
        )
        self.bottom_button_label.pack(side=tk.TOP, pady=(2, 0))

        # Lableling Frame
        self.Lableling_frame = tk.Frame(self.edit_frame, bg="#f0f0f0")
        self.Lableling_frame.pack(side=tk.TOP,  pady=2)

        # Entry for label text (اضافه شده)
        self.label_var = tk.StringVar()
        self.label_entry = ttk.Entry(
            self.Lableling_frame,
            textvariable=self.label_var,
            width=10,
            validate="key",
            validatecommand=(self.register(self.validate_label_entry), '%P'), 
            font=('Tahoma', 10)
        )
        self.label_entry.pack(side=tk.LEFT, padx=2)
        self.label_entry.bind("<KeyRelease>", self.update_label_text)
        self.label_entry.bind("<Down>", self.on_key_down)
        self.label_entry.bind("<Control-Down>", self.on_key_down)
        self.label_entry.bind("<Up>", self.on_key_down)
        self.label_entry.bind("<Control-Up>", self.on_key_down)
        self.label_entry.bind("<Return>", self.on_key_down)
        



        self.UnLock_button = ttk.Button(self.Lableling_frame, text="UnLock",padding=0, width=button_width+2, command=self.UnLock)
        self.UnLock_button.pack(side=tk.LEFT,  padx=2)

        self.Lockframe = tk.Frame(self.edit_frame, bg="#f0f0f0")
        self.Lockframe.pack(side=tk.TOP,  pady=2)

        self.Lockandgo_button = ttk.Button(self.Lockframe, text="Lock and go",padding=0, width=button_width+6, command=self.Lock_and_go_next)
        self.Lockandgo_button.pack(side=tk.LEFT,  padx=2)

        self.Lock_button = ttk.Button(self.Lockframe, text="Lock", padding=0, width=button_width, command=self.Lock_Rectangle)
        self.Lock_button.pack(side=tk.LEFT, padx=2)

        self.delet_frame = tk.Frame(self.edit_frame, bg="#f0f0f0")
        self.delet_frame.pack(side=tk.BOTTOM,  pady=2)

        self.delete_button = ttk.Button(self.delet_frame, text="Delete", padding=0,  command=self.delete_rectangle)
        self.delete_button.pack(side=tk.BOTTOM, padx=5, pady=(100,0))

    # توابع لازم برای اسکرول کردن ضلع‌های جعبه دور شیء
    def on_top_scroll(self, event):
        """فقط اسکرول UP"""
        if event.state & 0x0004:  # Control key mask
            if event.delta > 0:  # اسکرول به بالا
                self.move_top_up()
            elif event.delta < 0:
                self.move_top_down()

    def on_top_scroll_up(self, event):
        """برای لینوکس/مک"""
        if event.state & 0x0004:  # Control key mask
            self.move_top_up()
    def on_top_scroll_down(self, event):
        """برای لینوکس/مک"""
        if event.state & 0x0004:  # Control key mask
            self.move_top_down()

    def on_But_scroll(self, event):
        """فقط اسکرول UP"""
        if event.state & 0x0004:  # Control key mask
            if event.delta > 0:  # اسکرول به بالا
                self.move_bottom_up()
            elif event.delta < 0:
                self.move_bottom_down()

    def on_But_scroll_up(self, event):
        """برای لینوکس/مک"""
        if event.state & 0x0004:  # Control key mask
            self.move_bottom_up()
    def on_But_scroll_down(self, event):
        """برای لینوکس/مک"""
        if event.state & 0x0004:  # Control key mask
            self.move_bottom_down()

    def on_left_scroll(self, event):
        """فقط اسکرول UP"""
        if event.state & 0x0004:  # Control key mask
            if event.delta > 0:  # اسکرول به بالا
                self.move_left_left()
            elif event.delta < 0:
                self.move_left_right()

    def on_left_scroll_up(self, event):
        """برای لینوکس/مک"""
        if event.state & 0x0004:  # Control key mask
            self.move_left_left()
    def on_left_scroll_down(self, event):
        """برای لینوکس/مک"""
        if event.state & 0x0004:  # Control key mask
            self.move_left_right()

    def on_right_scroll(self, event):
        """فقط اسکرول UP"""
        if event.state & 0x0004:  # Control key mask
            if event.delta > 0:  # اسکرول به بالا
                self.move_right_right()
            elif event.delta < 0:
                self.move_right_left()

    def on_right_scroll_up(self, event):
        """برای لینوکس/مک"""
        if event.state & 0x0004:  # Control key mask
            self.move_right_right()
    def on_right_scroll_down(self, event):
        """برای لینوکس/مک"""
        if event.state & 0x0004:  # Control key mask
            self.move_right_left()

    # توابع مربوط به درگ عکس اصلی
    def start_drag(self, event):
        """شروع درگ با ذخیره موقعیت کلیک راست."""
        self.drag_start = (event.x, event.y)

    def on_drag(self, event):
        if self.image_tk != None:

            """جابجایی تصویر کراپ شده با درگ موس."""
            if not self.drag_start:
                return
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            dx = (event.x - self.drag_start[0]) / canvas_width / self.zoom_factor
            dy = (event.y - self.drag_start[1]) / canvas_height / self.zoom_factor

            dx = min(dx,  self.crop_cords[0])
            dx = max(dx,  self.crop_cords[2] - 1)
            dy = min(dy,  self.crop_cords[1])
            dy = max(dy,  self.crop_cords[3] - 1)


            # آپدیت مختصات کراپ
            self.crop_cords = [
                self.crop_cords[0] - dx,
                self.crop_cords[1] - dy,
                self.crop_cords[2] - dx,
                self.crop_cords[3] - dy,
            ]

            # آپدیت نقطه شروع برای حرکت بعدی
            self.drag_start = (event.x, event.y)
            self.refresh_image()  # Your method to display the image
            self.draw_rectamgles()

    def end_drag(self, event):
        """پایان درگ."""
        self.drag_start = None

    def on_listbox_release(self, event):
        # این تابع زمانی فراخوانی می‌شود که دکمه موس روی لیست باکس رها شود
        self.after(10, lambda: self.label_entry.focus_set())  # از after برای اطمینان از اجرای صحیح استفاده می‌کنیم

    def validate_label_entry2(self, new_text):
        last_char = new_text[-1] if new_text else None
        if last_char != None:
            if ord(last_char) == 63:
                messagebox.showinfo("Type failed", "برای نوشتن اعداد از کیبورد انگلیسی استفاده کنید\n\nبرای نوشتن ممیز فارسی به انگلیسی کلمه زیر را تایپ کنید\nMMYZ")
                return False
        # مجموعه کاراکترهای مجاز (برای سرعت بیشتر)
        allowed_chars = {
            'آ', 'ا', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'ژ', 'س', 'ش', 'ص',
            'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن', 'و', 'ه', 'ي', 'ی',
            'ؤ', 'ئ', 'أ', 'ء'
            '۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹',
            ')', '(', ']', '[', '؟', '!', '.', '،', ':', '؛', '»', '«',
            '+', '-', '/', '×', '÷', '>', '=', '<', '٫', '‌', ' ',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
        }
        return all(char in allowed_chars for char in new_text)

    def validate_label_entry(self, new_text):
        """اعتبارسنجی با مجموعه کاراکترهای مجاز"""
        if len(new_text) > 10:
            return False
        
        last_char = new_text[-1] if new_text else None
        if last_char != None:
            if ord(last_char) == 63:
                messagebox.showinfo("Type failed", "برای نوشتن اعداد از کیبورد انگلیسی استفاده کنید\n\nبرای نوشتن ممیز فارسی به انگلیسی کلمه زیر را تایپ کنید\nMMYZ")
                return False
        # مجموعه کاراکترهای مجاز (برای سرعت بیشتر)
        allowed_chars = {
            'آ', 'ا', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'ژ', 'س', 'ش', 'ص',
            'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن', 'و', 'ه', 'ي', 'ی',
            'ؤ', 'ئ', 'أ', 'ء'
            '۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹',
            ')', '(', ']', '[', '؟', '!', '.', '،', ':', '؛', '»', '«',
            '+', '-', '/', '×', '÷', '>', '=', '<', '٫', '‌', ' ',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '#'
        }
        
        return all(char in allowed_chars for char in new_text)

    def update_label_text(self, event=None):
        """تابع آپدیت هنگام تغییر برچسب با پشتیبانی از کاراکترهای فارسی و خاص"""
        try:
            label_text = self.label_var.get()
            
            if self.rect_index is not None:
                # ذخیره متن با پشتیبانی کامل از یونیکد
                self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
                self.Labels[self.rect_index] = label_text
                self.project_data["Labels"][self.project_data["images"][self.img_index]] = self.Labels
                
                # به روزرسانی لیست
                self.populate_rectangle_list()
                self.update_edit_panel_and_image_crop()
              
        except Exception as e:
            messagebox.showerror("Error", f"Error in update_label_text: {str(e)}")

    def on_key_down(self, event):
        """مدیریت فشردن کلیدها"""
        if event.keysym == "Down":  # اگر دکمه پایین فشار داده شد
            if event.state & 0x4:  # بررسی اینکه کلید Ctrl هم فشرده شده
                self.move_rectangle_down()  # تابع جدید برای Ctrl + پایین
            else:
                self.go_next()           
        elif event.keysym == "Up":  # اگر دکمه بالا فشار داده شد
            if event.state & 0x4:  # بررسی اینکه کلید Ctrl هم فشرده شده
                self.move_rectangle_up()  # تابع جدید برای Ctrl + بالا
            else:
                self.go_back()        
        elif event.keysym == "Return":  # اگر اینتر فشار داده شد
            self.Lock_and_go_next()

    # Event handlers for drawing rectangles
    def on_button_press(self, event):
        """Start drawing a rectangle only if an image is displayed."""
        if self.image_tk == None:
            # Optionally inform the user or silently ignore
            return  # Do nothing if no image is loaded
        self.start_x = event.x
        self.start_y = event.y
        if hasattr(self, 'rect') and self.rect:
            self.canvas.delete(self.rect)
        self.rect = None  # Reset rectangle ID
        # Reset all rectangles to their original color (if needed)
        if self.rect_index != None:
            self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="blue")  # Reset to original color

    def on_mouse_drag(self, event):
        if self.image_tk == None:
            # Optionally inform the user or silently ignore
            return  # Do nothing if no image is loaded
        """Draw rectangle while dragging the mouse."""
        if self.rect:
            self.canvas.delete(self.rect)  # Remove the previous rectangle
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="cyan", width=2)

    def on_button_release(self, event):
        #  redraw cross lines
        self.draw_cross_lines(event)
       
        if self.image_tk == None:
            return  # Do nothing if no image is loaded
        if not self.rect:
            return  # no rectangle was drawn
        """Finalize the rectangle on mouse release."""
        if self.rect:
            # Get the final coordinates and save the rectangle
            x1, y1, x2, y2 = self.start_x, self.start_y, event.x, event.y

            if (max(x1, x2)-min(x1, x2)) > 3 and (max(y1, y2)-min(y1, y2)) > 3:

                # Get image display size and canvas size (they should match)
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()

                # Calculate coordinates relative to image size
                rel_start_x = min(x1, x2) / canvas_width
                rel_start_y = min(y1, y2) / canvas_height
                rel_end_x = max(x1, x2) / canvas_width
                rel_end_y = max(y1, y2) / canvas_height

                # Update coordinates relative to image Zoom
                rel_start_x = self.crop_cords[0] + rel_start_x/self.zoom_factor
                rel_start_y = self.crop_cords[1] + rel_start_y/self.zoom_factor
                rel_end_x = self.crop_cords[0] + rel_end_x/self.zoom_factor
                rel_end_y = self.crop_cords[1] + rel_end_y/self.zoom_factor


                # Save the rectangle coordinates as needed
                """Handle selection of an image from the image list."""
                self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
                self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
                self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
                # add new rectangle
                self.coords = list((rel_start_x, rel_start_y, rel_end_x, rel_end_y))
                self.rec_islock = False
                self.Rec_Label = ""
                if self.rect_index == None:
                    self.rectangles.append(self.coords)
                    self.IsLocks.append(self.rec_islock)
                    self.Labels.append(self.Rec_Label)
                    # add id to the new rectangle
                    self.rec_IDs.append(self.rect)
                    self.rect_index = len(self.rec_IDs)-1
                elif self.rect_index < len(self.rectangles):
                    self.rectangles.insert(self.rect_index + 1, self.coords)  # درج در موقعیت بعد از مستطیل حاضر
                    self.IsLocks.insert(self.rect_index + 1, self.rec_islock)
                    self.Labels.insert(self.rect_index + 1, self.Rec_Label)
                    # add id to the new rectangle
                    self.rec_IDs.insert(self.rect_index + 1, self.rect)
                    # Reset all rectangles to their original color (if needed)
                    self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="blue")  # Reset to original color
                    self.rect_index += 1
                else:
                    messagebox.showerror('Error', 'Somthing is going wrong. code 2112455')
                    
                self.project_data["rectangles"][self.project_data["images"][self.img_index]] = self.rectangles
                self.project_data["IsLocks"][self.project_data["images"][self.img_index]] = self.IsLocks
                self.project_data["Labels"][self.project_data["images"][self.img_index]] = self.Labels
                
                self.rect = None  # Reset rectangle ID

                    
                self.populate_rectangle_list()  # Populate the rectangle list
                self.update_edit_panel_and_image_crop()
                # Change the color of the selected rectangle to red
                self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="red", width=2)

                self.populate_rectangle_list()
                self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
            else:
                self.canvas.delete(self.rect)  # Remove the small rectangle

    def Split_images_by_BBoxes(self):
        # دریافت مسیرها از کاربر
        destination = filedialog.askdirectory(title="Select Base Folder for New Project")
        if not destination:
            return  # User cancelled folder selection

        for fname in self.project_data["images"]:
            image_full_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")

            filename, extension = os.path.splitext(os.path.basename(image_full_path))
            try:
                img = Image.open(image_full_path)
            except Exception as e:
                messagebox.showerror(title="Image Load Error", message=f"Failed to load image:\n{e}\nIt is continued for other images.")
                continue
            rectangles = self.project_data["rectangles"][fname]
            for rec, coords in enumerate(rectangles):
                x1, y1, x2, y2 = coords
                img_width, img_height = img.size

                # Calculate pixel coordinates
                left = int(x1 * img_width)
                top = int(y1 * img_height)
                right = int(x2 * img_width)
                bottom = int(y2 * img_height)

                # Ensure coordinates are within bounds
                left = max(0, left)
                top = max(0, top)
                right = min(img_width, right)
                bottom = min(img_height, bottom)

                # Crop the image
                cropped_img = img.crop((left, top, right, bottom))
                new_filename = f"{filename}_{(rec+1):03d}{extension}"
                
                new_path = os.path.join(destination, new_filename).replace("\\",  "/")
                cropped_img.save(new_path, quality=95)  # تغییر این خط

        messagebox.Message("عملیات با موفقیت انجام شد!")
        proceed = messagebox.askyesno(
            "Success",
            f"Project Splited successfully.\nThe folder is:\n{destination}\n\n Do you want to open the folder?")
        if proceed:
            os.startfile(destination)


    def Split_images_by_Label(self):
        # دریافت کلمه از کاربر
        label = simpledialog.askstring("ورود لیبل", "لطفاً لیبل مورد نظر خود\nبرای تفکیک تصاویر را وارد کنید:\n\n")
        if not label:
            return # User cancelled folder selection

        # دریافت مسیرها از کاربر
        destination = filedialog.askdirectory(title="Select Base Folder for Moving the splited images to")
        if not destination:
            return  # User cancelled folder selection

        for fname in self.project_data["images"]:
            image_full_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")
            filename, extension = os.path.splitext(os.path.basename(image_full_path))
            try:
                img = Image.open(image_full_path)
            except Exception as e:
                messagebox.showerror(title="Image Load Error", message=f"Failed to load image:\n{e}\nIt is continued for other images.")
                continue
            rectangles = self.project_data["rectangles"][fname]
            Lables = self.project_data["Labels"][fname]
            for rec, coords in enumerate(rectangles):
                if Lables[rec] == label:
                    x1, y1, x2, y2 = coords
                    img_width, img_height = img.size

                    # Calculate pixel coordinates
                    left = int(x1 * img_width)
                    top = int(y1 * img_height)
                    right = int(x2 * img_width)
                    bottom = int(y2 * img_height)

                    # Ensure coordinates are within bounds
                    left = max(0, left)
                    top = max(0, top)
                    right = min(img_width, right)
                    bottom = min(img_height, bottom)

                    # Crop the image
                    cropped_img = img.crop((left, top, right, bottom))
                    new_filename = f"{filename}_{(rec+1):03d}{extension}"
                    
                    new_path = os.path.join(destination, new_filename).replace("\\",  "/")
                    cropped_img.save(new_path, quality=95)  # تغییر این خط

        messagebox.Message("عملیات با موفقیت انجام شد!")
        proceed = messagebox.askyesno(
            "Success",
            f"Project Splited successfully.\nThe folder is:\n{destination}\n\n Do you want to open the folder?")
        if proceed:
            os.startfile(destination)

    def Split_Current_image_by_BBoxes(self):
        if self.img_index != None:
            # دریافت مسیرها از کاربر
            destination = filedialog.askdirectory(title="Select the Destination Folder to Split Current Image")
            if not destination:
                return  # User cancelled folder selection
            
            project_name = simpledialog.askstring("Project Name", "Enter new project name\nThis names will be used to create a folder for Project files too.")
            if not project_name:
                return  # User cancelled project name input
            full_project_path = os.path.join(destination, project_name).replace("\\",  "/")
            try:
                os.makedirs(full_project_path, exist_ok=False)
                project_folder = full_project_path
            except FileExistsError:
                response = messagebox.askyesno(
                    "Folder Exists",
                    f"The folder '{full_project_path}' already exists.\n\n\nDo you want to continue and use this folder?"
                )
                if response:
                    project_folder = full_project_path
                else:
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Could not create project folder:\n\n{e}")
                return

            try:
                os.makedirs(os.path.join(project_folder, 'images').replace("\\",  "/"), exist_ok=True)
                project_image_folder = os.path.join(project_folder, 'images').replace("\\",  "/")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create images folder:\n\n{e}")
                return


            fname = self.project_data["images"][self.img_index]
            image_full_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")
            filename, extension = os.path.splitext(os.path.basename(image_full_path))
            try:
                img = Image.open(image_full_path)
            except Exception as e:
                messagebox.showerror(title="Image Load Error", message=f"Failed to load image:\n{e}")
                return
            
            project_txt_path = os.path.join(project_folder, project_name + '_project.txt').replace("\\",  "/")
            try:
                with open(project_txt_path, "w", encoding="utf-8") as f:
                    f.write(f"Project: {project_name}\n\n")
                    f.write(f"Project Folder: {project_folder}\n\n")
                    f.write(f"Image Folder: {project_image_folder}\n\n")
                    f.write(f"Path to AI: \n\n")
                    rectangles = self.project_data["rectangles"][fname]
                    for rec, coords in enumerate(rectangles):
                        x1, y1, x2, y2 = coords
                        img_width, img_height = img.size

                        # Calculate pixel coordinates
                        left = int(x1 * img_width)
                        top = int(y1 * img_height)
                        right = int(x2 * img_width)
                        bottom = int(y2 * img_height)

                        # Ensure coordinates are within bounds
                        left = max(0, left)
                        top = max(0, top)
                        right = min(img_width, right)
                        bottom = min(img_height, bottom)

                        # Crop the image
                        cropped_img = img.crop((left, top, right, bottom))
                        new_filename = f"{filename}_{(rec+1):03d}{extension}"
                        
                        new_path = os.path.join(project_image_folder, new_filename).replace("\\",  "/")
                        cropped_img.save(new_path, quality=95)  # تغییر این خط

                        f.write(f"[{rec+1}] {new_filename}\n")

                    f.write("\nRectangles per image:\n\n")
                    f.write("\nnames:\n")

            except Exception as e:
                messagebox.showerror("Error", f"Could not split current image by BBoxes properly:\n{e}")

        messagebox.Message("عملیات با موفقیت انجام شد!")
        proceed = messagebox.askyesno(
            "Success",
            f"Project Splited successfully.\nThe folder is:\n{destination}\n\n Do you want to open the folder?")
        if proceed:
            os.startfile(project_folder)

    def Split_Current_image_by_Label(self):
        # دریافت کلمه از کاربر
        label = simpledialog.askstring("ورود لیبل", "لطفاً لیبل مورد نظر خود\nبرای تفکیک تصاویر را وارد کنید:\n\n")
        if not label:
            return # User cancelled folder selection

        if self.img_index != None:
            # دریافت مسیرها از کاربر
            destination = filedialog.askdirectory(title="Select the Destination Folder to Split Current Image by Label")
            if not destination:
                return  # User cancelled folder selection
            fname = self.project_data["images"][self.img_index]
            image_full_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")
            filename, extension = os.path.splitext(os.path.basename(image_full_path))
            try:
                img = Image.open(image_full_path)
            except Exception as e:
                messagebox.showerror(title="Image Load Error", message=f"Failed to load image:\n{e}")
                return
            rectangles = self.project_data["rectangles"][fname]
            Lables = self.project_data["Labels"][fname]
            for rec, coords in enumerate(rectangles):
                if Lables[rec] == label:
                    x1, y1, x2, y2 = coords
                    img_width, img_height = img.size

                    # Calculate pixel coordinates
                    left = int(x1 * img_width)
                    top = int(y1 * img_height)
                    right = int(x2 * img_width)
                    bottom = int(y2 * img_height)

                    # Ensure coordinates are within bounds
                    left = max(0, left)
                    top = max(0, top)
                    right = min(img_width, right)
                    bottom = min(img_height, bottom)

                    # Crop the image
                    cropped_img = img.crop((left, top, right, bottom))
                    new_filename = f"{filename}_{(rec+1):03d}{extension}"
                    
                    new_path = os.path.join(destination, new_filename).replace("\\",  "/")
                    cropped_img.save(new_path, quality=95)  # تغییر این خط

        messagebox.Message("عملیات با موفقیت انجام شد!")
        proceed = messagebox.askyesno(
            "Success",
            f"Project Splited successfully.\nThe folder is:\n{destination}\n\n Do you want to open the folder?")
        if proceed:
            os.startfile(destination)

    def Split_Project_by_Current_image(self):
        if self.img_index != None:
            destination = filedialog.askdirectory(title="Select the Destination Folder to Split Current Image")
            if not destination:
                return  # User cancelled folder selection
            fname = self.project_data["images"][self.img_index]
            try:
                project_txt_path = os.path.join(destination, f"{fname}_project.txt").replace("\\",  "/")
                with open(project_txt_path, "w", encoding="utf-8") as f:
                    # Write project name
                    f.write(f"Project: {fname}\n\n")
                    # Write project folder
                    f.write(f"Project Folder: {destination}\n\n")
                    # Write image folder
                    f.write(f"Image Folder: {destination + '/images'}\n\n")
                    # Write empty path to AI assitant model
                    f.write(f"Path to AI: \n\n")

                    # Write images list with index
                    f.write(f"[{1:03d}] {fname}\n")
                    
                    f.write("\nRectangles per image:\n")
                    
                    # Write rectangles for each image
                    f.write(f"[{1:03d}] {fname}\n")
                    rects = self.project_data["rectangles"][fname]
                    Locks = self.project_data["IsLocks"][fname]
                    Labels = self.project_data["Labels"][fname]
                    if rects:
                        for rcs, (x1, y1, x2, y2) in enumerate(rects):
                            f.write(f"\tRect: ({x1:.6f}, {y1:.6f}), ({x2:.6f}, {y2:.6f})\n")
                            label = Labels[rcs]
                            f.write(f"\t\tLock := ({Locks[rcs]})  \tClass := \"{label}\" \n")
                        f.write("\n")
                    else:
                        f.write("\n")  # If no rectangles, just add a new line

                    f.write("\nnames:\n")  # List of label names
                    f.write("\n")  # End of file
                
                # move images
                image_full_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")
                # اگر فولدر مقصد وجود ندارد، ایجادش کن
                image_destination_path = os.path.join(destination, 'images').replace("\\", "/")
                image_destination_path = os.path.abspath(image_destination_path)
                os.makedirs(image_destination_path, exist_ok=True)
                # تبدیل مسیرها به فرم استاندارد و مقایسه
                source_abs = os.path.abspath(self.project_data['image_folder'])

                if source_abs != image_destination_path:
                    try:
                        # مسیر مقصد کامل
                        dest_file = os.path.join(image_destination_path, os.path.basename(image_full_path)).replace("\\",  "/")
                        # بررسی وجود فایل در مقصد
                        if not os.path.exists(dest_file):
                            shutil.copy2(image_full_path, image_destination_path)
                        else:
                            messagebox.showinfo("Info", f"This file exsisted in destination!!\n      {fname}.")
                        messagebox.showinfo("Success", f"New Project is exported successfully with image\n      {fname}.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not copy image to destination:\n{e}\n image moved is: {fname}")
                else:
                    messagebox.showinfo("Info", f"Source and destination folders for images are the same\n      {source_abs}.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export project comletely for image\n      {fname}")


    def populate_image_list(self, image_files):
        """Populate the image listbox with image filenames."""
        self.lb1.delete(0, tk.END)  # Clear existing items
        if len(self.project_data["images"]) > 0:
            for idx, img_file in enumerate(image_files, start=1):
                self.lb1.insert(tk.END, f'{idx:03d}: {img_file}')  # Add each image file to the listbox
        elif len(self.project_data["images"]) == 0:
            self.lb1.insert(tk.END, "No image: \n Add image")  # Add no image to the listbox


    def populate_rectangle_list(self):
        """Populate the rectangle listbox with rectangle coordinates."""
        self.lb2.delete(0, tk.END)  # Clear existing items
        self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
        self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
        self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
        if self.rectangles != [] and self.rect_index != None:
            for idx, coords in enumerate(self.rectangles, start=1):
                # self.lb2.insert(tk.END, f"Rect {idx}: {self.Labels[idx-1]} {self.IsLocks[idx-1]} ({coords[0]:.3f}, {coords[1]:.3f}), ({coords[2]:.3f}, {coords[3]:.3f})")
                Lockemoji = "     \t"
                if self.IsLocks[idx-1]:
                    Lockemoji = "\U0001F512\t"
                self.lb2.insert(tk.END, f"{Lockemoji} Rect {idx:02d}: {self.Labels[idx-1]:<8s} ")

            # activate last rectangle
            self.lb2.selection_clear(0, tk.END)    # Clear any previous selection
            self.lb2.selection_set(self.rect_index)              # Select the first item (index 0)
            self.lb2.activate(self.rect_index)                  # Set the active item to the first one
            self.lb2.see(self.rect_index)                      # Scroll to make sure the first item is visible
            self.update_edit_panel_and_image_crop
            # if self.rec_islock:
            #     self.disable_frame()
            # else:
            #     self.enable_frame()
                
        else:
            self.lb2.insert(tk.END, "(No rectangles)")  # Indicate no rectangles
        self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                

    def on_file_select(self, event):
        """Handle selection of an image from the image list."""
        if len(self.project_data["images"]) == 0:
            self.img_index = None
            self.rect_index = None
            self.label_var.set("")
            return
        selected_index = self.lb1.curselection()
        if selected_index:
            self.img_index = selected_index[0]  # Get the first selected index
            self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
            self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
            self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
            if self.rectangles == []:
                self.label_var.set("")
                self.rect_index = None
                self.crop_canvas.delete("all")
                self.disable_frame()
            else:
                if self.rect_index == None:
                    self.rect_index = 0
                else:
                    if self.rect_index > len(self.rectangles)-1:
                        self.rect_index = len(self.rectangles)-1
                        
                self.coords = list(self.rectangles[self.rect_index])  # Copy for editing
                self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
                self.Rec_Label = self.Labels[self.rect_index]  # Copy for editing
            self.populate_rectangle_list()  # Populate the rectangle list
            # Load the image and rectangles for the selected image

            # Reset Zoom
            self.zoom_factor = 1 # Zoom factor
            self.crop_cords = [0, 0 , 1, 1] #Crop coordinations used for zoom
            self.display_image()  # Your method to display the image number self.img_index

            self.draw_rectamgles()
            self.update_edit_panel_and_image_crop()
            self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
            self.label_entry.icursor(tk.END)  # Move cursor to end of text

            self.Auto_save_project() # Auto save project for backup

    def display_image(self):
        self.canvas.delete("all")
        if self.img_index != None:
            self.lb1.selection_clear(0, tk.END)    # Clear any previous selection
            self.lb1.selection_set(self.img_index)              # Select the first item (index 0)
            self.lb1.activate(self.img_index)                  # Set the active item to the first one
            self.lb1.see(self.img_index)                      # Scroll to make sure the first item is visible
            self.lb1.focus_set()                 # Set keyboard focus to the listbox for better UX                

            fname = self.project_data["images"][self.img_index]
            self.image_full_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")

            try:
                img = Image.open(self.image_full_path)
                self.crop_img = img # تصویر با رزولوشن کامل برای نمایش در پنل ویرایش مستطیل
                # کاهش بر اساس عرض مشخص (حفظ نسبت ابعاد)
                target_width = 800  # پیکسل
                width, height = img.size
                ratio = target_width / width
                new_height = int(height * ratio)

                img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)

                self.original_image = img  # Store the original image for resizing later
                # Get available display frame size
                frame_width = self.left_frame.winfo_width()-25
                frame_height = self.left_frame.winfo_height()-75

                # crop image
                img = img.crop((int(self.crop_cords[0]*img.width), int(self.crop_cords[1]*img.height), int(self.crop_cords[2]*img.width), int(self.crop_cords[3]*img.height)))  # Crop the image


                # Calculate scale factor based on height only for uniform scaling without cropping
                scale_factor_H = frame_height / img.height
                scale_factor_W = frame_width / img.width
                scale_factor = min(scale_factor_H, scale_factor_W) 
                scaled_width = int(img.width * scale_factor)
                scaled_height = int(img.height * scale_factor)

                # Resize the canvas to exact image size (no extra padding)
                self.canvas.config(width=scaled_width, height=scaled_height)

                # Resize image using high-quality resampling
                img = img.resize((scaled_width, scaled_height))


                # Create PhotoImage and display
                self.image_tk = ImageTk.PhotoImage(img)

                # Save image visible area for future reference [x1, y1, x2, y2]
                self.canvas.create_image(scaled_width//2, scaled_height//2, anchor=tk.CENTER, image=self.image_tk)

            except Exception as e:
                self.image_tk = None
                messagebox.showerror(title="Image Load Error", message=f"Failed to load image:\n{e}")
        else:
            self.image_tk = None

    def refresh_image(self):
        self.canvas.delete("all")
        self.image_tk = None # reset and initialize

        if self.img_index != None:
            try:
                img = self.original_image # Store the original image for resizing later
                # Get available display frame size
                frame_width = self.left_frame.winfo_width()-25
                frame_height = self.left_frame.winfo_height()-75

                # crop image
                img = img.crop((int(self.crop_cords[0]*img.width), int(self.crop_cords[1]*img.height), int(self.crop_cords[2]*img.width), int(self.crop_cords[3]*img.height)))  # Crop the image


                # Calculate scale factor based on height only for uniform scaling without cropping
                scale_factor_H = frame_height / img.height
                scale_factor_W = frame_width / img.width
                scale_factor = min(scale_factor_H, scale_factor_W) 
                scaled_width = int(img.width * scale_factor)
                scaled_height = int(img.height * scale_factor)

                # Resize the canvas to exact image size (no extra padding)
                self.canvas.config(width=scaled_width, height=scaled_height)

                # Resize image using high-quality resampling
                img = img.resize((scaled_width, scaled_height))


                # Create PhotoImage and display
                self.image_tk = ImageTk.PhotoImage(img)

                # Save image visible area for future reference [x1, y1, x2, y2]
                self.canvas.create_image(scaled_width//2, scaled_height//2, anchor=tk.CENTER, image=self.image_tk)

            except Exception as e:
                messagebox.showerror(title="Image Load Error", message=f"Failed to load image:\n{e}")

    def on_canvas_resize(self, event):
        self.canvas.delete("all")
        # Redraw the displayed image and rectangles to fit the new canvas size.
        if hasattr(self, 'original_image') and self.original_image:  # Check if original image exists
            try:
                img = self.original_image
                img = img.crop((int(self.crop_cords[0]*img.width), int(self.crop_cords[1]*img.height), int(self.crop_cords[2]*img.width), int(self.crop_cords[3]*img.height)))  # Crop the image


                # Get available display frame size
                frame_width = self.left_frame.winfo_width()-25
                frame_height = self.left_frame.winfo_height()-75

                # Calculate scale factor based on height and width for uniform scaling
                scale_factor_H = frame_height / img.height
                scale_factor_W = frame_width / img.width
                scale_factor = min(scale_factor_H, scale_factor_W) 
                scaled_width = int(img.width * scale_factor)
                scaled_height = int(img.height * scale_factor)

                # Resize the canvas to exact image size (no extra padding)
                self.canvas.config(width=scaled_width, height=scaled_height)

                # Resize the original image using high-quality resampling
                resized_image = img.resize((scaled_width, scaled_height), Image.LANCZOS)
                self.image_tk = ImageTk.PhotoImage(resized_image)  # Create a new PhotoImage from the resized image

                # Clear the canvas and display the resized image
                # self.canvas.delete("all")
                self.canvas.create_image(scaled_width//2, scaled_height//2, anchor=tk.CENTER, image=self.image_tk)

                # Save image visible area for future reference [x1, y1, x2, y2]
                # self.image_area = (0, 0, scaled_width, scaled_height)

            except Exception as e:
                messagebox.showerror(title="Image Load Error", message=f"Failed to load image:\n{e}")

            if self.image_tk  != None:
                self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
                self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
                self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
            else:
                self.rectangles = []
                self.IsLocks = []
                self.Labels = []
                return
                
            self.draw_rectamgles()

    def _handle_resize(self, event):
        """مدیریت هوشمند رویدادهای تغییر اندازه"""
        if self._resize_timer:
            self.after_cancel(self._resize_timer)
        
        self._resize_timer = self.after(50, self.on_frame_resize)

    # تابعی برای تنظیم خودکار اندازه
    def on_frame_resize(self):
        """انجام واقعی تغییر اندازه پس از تثبیت پنجره"""
        self._resize_timer = None
        # self.crop_canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        self.update_edit_panel_and_image_crop()


    def draw_rectamgles(self):
        # Recalculate absolute coords on canvas based on relative coords and draw
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if self.rec_IDs:
            for rec in self.rec_IDs:
                self.canvas.delete(rec)
        rec_ids = []
        if self.img_index != None:
            self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]
            for coords in self.rectangles:
                # Update coordinates relative to image Zoom
                rel_start_x = (-self.crop_cords[0] + coords[0])*self.zoom_factor
                rel_start_y = (-self.crop_cords[1] + coords[1])*self.zoom_factor
                rel_end_x =   (-self.crop_cords[0] + coords[2])*self.zoom_factor
                rel_end_y =   (-self.crop_cords[1] + coords[3])*self.zoom_factor

                x1 = int(rel_start_x * canvas_width)
                y1 = int(rel_start_y * canvas_height)
                x2 = int(rel_end_x * canvas_width)
                y2 = int(rel_end_y * canvas_height)
                new_id = self.canvas.create_rectangle(x1 - 1, y1 - 1, x2, y2, outline="blue", width=2)    
                rec_ids.append(new_id)
            
            self.rec_IDs = rec_ids
            if self.rec_IDs != []:
                if self.rect_index == None:
                    self.rect_index = 0
                self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="red")
            else:
                self.rect_index = None
                self.label_var.set("")

    def on_rectangle_select(self, event):
        # Reset all rectangles to their original color (if needed)
        if self.rect_index != None:
            self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="blue")  # Reset to original color

        """Handle selection of a rectangle from the rectangle list."""
        selected_index = self.lb2.curselection()
        if selected_index:
            # Get the selected index and corresponding rectangle ID
            self.rect_index = selected_index[0]  # Get the first selected index
            if len(self.rec_IDs) == 0:  # Ensure the index is valid
                self.rect_index = None
                self.label_var.set("")
                return

        # Get currently selected image and rectangles list
        if self.lb1.curselection():
            self.img_index = self.lb1.curselection()[0]

            self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
            self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
            self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
            self.coords = list(self.rectangles[self.rect_index])  # Copy for editing
            self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
            self.Rec_Label = self.Labels[self.rect_index]  # Copy for editing

            # Proper zoom on the rectangle
            self.zoom_factor = max(1, min(1/(self.coords[2]-self.coords[0]), 1/(self.coords[3]-self.coords[1])))
            Zoomwidth = min(1, 10 / self.zoom_factor)
            self.zoom_factor = 1 / Zoomwidth
            rel_x1 = ((self.coords[0] + self.coords[2]) / 2 - Zoomwidth / 2) 
            if rel_x1 < 0:
                rel_x1 = 0
            if rel_x1 > (1-Zoomwidth):
                rel_x1 = (1-Zoomwidth)
            rel_y1 = ((self.coords[1] + self.coords[3]) / 2 - Zoomwidth / 2) 
            if rel_y1 < 0:
                rel_y1 = 0
            if rel_y1 > (1-Zoomwidth):
                rel_y1 = (1-Zoomwidth)
            self.crop_cords = list((rel_x1, rel_y1, rel_x1+Zoomwidth, rel_y1+Zoomwidth))
            self.refresh_image()  # Your method to display the image number self.img_index
            self.draw_rectamgles()
            self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
            # self.populate_rectangle_list()
            self.lb2.selection_clear(0, tk.END)    # Clear any previous selection
            self.lb2.selection_set(self.rect_index)              # Select the first item (index 0)
            self.lb2.activate(self.rect_index)                  # Set the active item to the first one
            self.update_edit_panel_and_image_crop()
            # self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
            self.label_entry.icursor(tk.END)  # Move cursor to end of text
        else:
            return

    def move_rectangle_up(self):
        if self.rect_index != None:
            if self.rect_index > 0:
                self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
                self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
                self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image

                # جابجایی سطرها در تمام لیست‌ها به صورت همزمان
                self.rectangles[self.rect_index], self.rectangles[self.rect_index - 1] = self.rectangles[self.rect_index - 1], self.rectangles[self.rect_index]
                self.IsLocks[self.rect_index], self.IsLocks[self.rect_index - 1] = self.IsLocks[self.rect_index - 1], self.IsLocks[self.rect_index]
                self.Labels[self.rect_index], self.Labels[self.rect_index - 1] = self.Labels[self.rect_index - 1], self.Labels[self.rect_index]
                
                self.project_data["rectangles"][self.project_data["images"][self.img_index]] = self.rectangles
                self.project_data["IsLocks"][self.project_data["images"][self.img_index]] = self.IsLocks
                self.project_data["Labels"][self.project_data["images"][self.img_index]] = self.Labels

                self.rect_index -= 1
                self.draw_rectamgles()
                self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
                self.populate_rectangle_list()
                self.update_edit_panel_and_image_crop()
                # self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
                self.label_entry.icursor(tk.END)  # Move cursor to end of text

    def move_rectangle_down(self):
        if self.rect_index != None:
            if self.rect_index < len(self.project_data["rectangles"][self.project_data["images"][self.img_index]])- 1:
                self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
                self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image
                self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]  # Load rectangles for the selected image

                # جابجایی سطرها در تمام لیست‌ها به صورت همزمان
                self.rectangles[self.rect_index], self.rectangles[self.rect_index + 1] = self.rectangles[self.rect_index + 1], self.rectangles[self.rect_index]
                self.IsLocks[self.rect_index], self.IsLocks[self.rect_index + 1] = self.IsLocks[self.rect_index + 1], self.IsLocks[self.rect_index]
                self.Labels[self.rect_index], self.Labels[self.rect_index + 1] = self.Labels[self.rect_index + 1], self.Labels[self.rect_index]
                
                self.project_data["rectangles"][self.project_data["images"][self.img_index]] = self.rectangles
                self.project_data["IsLocks"][self.project_data["images"][self.img_index]] = self.IsLocks
                self.project_data["Labels"][self.project_data["images"][self.img_index]] = self.Labels

                self.rect_index += 1
                self.draw_rectamgles()
                self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
                self.populate_rectangle_list()
                self.update_edit_panel_and_image_crop()
                # self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
                self.label_entry.icursor(tk.END)  # Move cursor to end of text

    def Auto_sort_rectangles(self):
        # Identify the clicked image item index
        if self.img_index == None:
            messagebox.showerror("Error", "No image is selected.")
            return
        fname = self.project_data["images"][self.img_index]

        response = messagebox.askyesnocancel(
            title='Sort Direction?',
            message='(YES)آیا مایلید به صورت عمودی از بالا به پایین مرتب شوند؟\n\n(NO)مایلم به صورت افقی مرتب شوند', 
            icon='question'
            )
        if response == True:
            direction  = 3 # Vertically
        elif response == False:
            direction  = 2 # Horisontally
        else:
            return

        self.rectangles = self.project_data["rectangles"][fname]
        coord_list = []
        for rec in self.rectangles:
            coord_list.append(list(rec)[direction])
        if self.rectangles != []:
            if response == True:
                sorted_indices = np.argsort(coord_list) # Vertically
            elif response == False:
                sorted_indices = np.argsort(coord_list)[::-1] # Horisontally
            
            # تبدیل به لیست معمولی پایتون
            sorted_indices_list = sorted_indices.tolist()

            self.project_data["rectangles"][fname] = [self.project_data["rectangles"][fname][i] for i in sorted_indices_list]
            self.project_data["IsLocks"][fname] = [self.project_data["IsLocks"][fname][i] for i in sorted_indices_list]
            self.project_data["Labels"][fname] = [self.project_data["Labels"][fname][i] for i in sorted_indices_list]

            self.rect_index = 0
            self.draw_rectamgles()
            self.populate_rectangle_list()  # Populate the rectangle list
            self.update_edit_panel_and_image_crop()
            self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
            self.label_entry.icursor(tk.END)  # Move cursor to end of text

            if response == True:
                messagebox.showinfo('Success', 'List is successfully sorted vertically.')  # Vertically
            elif response == False:
                messagebox.showinfo('Success', 'List is successfully sorted horisontally.') # Horisontally

        else:
            self.rect_index = None
            messagebox.showerror('Error', 'List is empty.')

    def on_rectangle_right_click(self, event):
        # Identify the clicked image item index
        if self.img_index == None:
            messagebox.showerror("Error", "No image is selected.")
            return
        else:
            # reset the color of previouse rectancle color is any
            if self.rect_index != None:
                self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="blue")  # Reset to original color
            # Identify the clicked BBox item index
            self.rect_index = self.lb2.nearest(event.y)
            if self.rect_index < 0 or self.rect_index > len(self.rec_IDs) or len(self.rec_IDs) == 0:
                self.rect_index = None
                self.label_var.set("")
                return  # Click not on an item

            # Select the clicked item
            self.lb2.selection_clear(0, tk.END)
            self.lb2.selection_set(self.rect_index)
            self.lb2.activate(self.rect_index)

            # self.img_index = self.lb1.curselection()[0]
            # self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]
            self.coords = list(self.rectangles[self.rect_index])  # Copy for editing
            self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
            self.Rec_Label = self.Labels[self.rect_index]  # Copy for editing
            self.update_edit_panel_and_image_crop()
            
            self.crop_cords = list((0, 0, 1, 1))
            self.zoom_factor = 1
            self.display_image()  # Your method to display the image number self.img_index
            self.draw_rectamgles()
            # Change the color of the selected rectangle to red
            self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="purple")

            # Ask for confirmation
            answer = messagebox.askyesno(
                "Confirm Deletion",
                "Are you sure you want to delete this rectangle?",
                icon='warning'
            )
            if answer:
                # Proceed with deletion
                self.delete_rectangle()
            else:
                self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="red")
                self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
                self.label_entry.icursor(tk.END)  # Move cursor to end of text

    def delete_rectangle(self):
        if self.rect_index != None:
            # delete a rectangle amd its ID from the project data
            self.rectangles =  self.project_data["rectangles"][self.project_data["images"][self.img_index]]
            del self.rectangles[self.rect_index]
            self.project_data["rectangles"][self.project_data["images"][self.img_index]] = self.rectangles

            self.IsLocks =  self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
            del self.IsLocks[self.rect_index]
            self.project_data["IsLocks"][self.project_data["images"][self.img_index]] = self.IsLocks

            self.Labels =  self.project_data["Labels"][self.project_data["images"][self.img_index]]
            del self.Labels[self.rect_index]
            self.project_data["Labels"][self.project_data["images"][self.img_index]] = self.Labels

            self.canvas.delete(self.rec_IDs[self.rect_index])
            del self.rec_IDs[self.rect_index]

            if self.rect_index > len(self.rectangles) - 1:
                self.rect_index -=1
            if self.rect_index == -1:
                self.rect_index = None
                self.label_var.set("")
            self.populate_rectangle_list()
            if self.rect_index != None:
                self.coords = list(self.rectangles[self.rect_index])  # Copy for editing
                self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
                self.Rec_Label = self.Labels[self.rect_index]  # Copy for editing
                self.update_edit_panel_and_image_crop()
                self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="red")
            else:
                self.crop_canvas.delete("all")
            self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
            self.label_entry.icursor(tk.END)  # Move cursor to end of text

    def draw_cross_lines(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        x = event.x
        y = event.y
        self.canvas.delete('lines')  # delete previous lines

        hex_color = f"#50ff50"

        self.canvas.create_line(x - 1, 0, x - 1, canvas_height, tags='lines', fill=hex_color)  # vertical line
        self.canvas.create_line(0, y - 1, canvas_width, y - 1, tags='lines', fill=hex_color)  # horizontal line

    def on_leave_image_canvas(self, event):
        self.canvas.delete('lines')  # delete previous lines

    def Zoom_out(self):
        if self.image_tk != None:
            Movement_x = min((self.crop_cords[2]-self.crop_cords[0])/10 , (1-(self.crop_cords[2]-self.crop_cords[0]))/2  )
            Movement_y = min((self.crop_cords[3]-self.crop_cords[1])/10 , (1-(self.crop_cords[3]-self.crop_cords[1]))/2  )
            self.crop_cords[0] -= Movement_x 
            self.crop_cords[1] -= Movement_y 
            self.crop_cords[2] += Movement_x 
            self.crop_cords[3] += Movement_y 

            if self.crop_cords[0] < 0:
                self.crop_cords[2] += (0-self.crop_cords[0])
                self.crop_cords[0] = 0
            if self.crop_cords[1] < 0:
                self.crop_cords[3] += (0-self.crop_cords[1])
                self.crop_cords[1] = 0
            if self.crop_cords[2] > 1:
                self.crop_cords[0] -= (self.crop_cords[2] - 1)
                self.crop_cords[2] = 1
            if self.crop_cords[3] > 1:
                self.crop_cords[1] -= (self.crop_cords[3] - 1)
                self.crop_cords[3] = 1


            self.zoom_factor = 1 / ((self.crop_cords[2]-self.crop_cords[0]))

            self.refresh_image()  # Your method to display the image
            self.draw_rectamgles()

    def Zoom_in(self):
        if self.image_tk != None:
            Movement_x = (self.crop_cords[2]-self.crop_cords[0])/10
            Movement_y = (self.crop_cords[3]-self.crop_cords[1])/10
            self.crop_cords[0] += Movement_x 
            self.crop_cords[1] += Movement_y 
            self.crop_cords[2] -= Movement_x 
            self.crop_cords[3] -= Movement_y 

            self.zoom_factor = 1 / ((self.crop_cords[2]-self.crop_cords[0]))

            self.refresh_image()  # Your method to display the image
            self.draw_rectamgles()

    def move_up(self):
        if self.image_tk != None:
            Movement = min((self.crop_cords[3]-self.crop_cords[1])/2 , (self.crop_cords[1]) )
            self.crop_cords[1] -= Movement 
            self.crop_cords[3] -= Movement 
            self.refresh_image()  # Your method to display the image
            self.draw_rectamgles()

    def move_down(self):
        if self.image_tk != None:
            Movement = min((self.crop_cords[3]-self.crop_cords[1])/2 , (1-self.crop_cords[3]) )
            self.crop_cords[1] += Movement 
            self.crop_cords[3] += Movement 
            self.refresh_image()  # Your method to display the image
            self.draw_rectamgles()

    def move_left(self):
        if self.image_tk != None:
            Movement = min((self.crop_cords[2]-self.crop_cords[0])/2 , (self.crop_cords[0]) )
            self.crop_cords[0] -= Movement 
            self.crop_cords[2] -= Movement 
            self.refresh_image()  # Your method to display the image
            self.draw_rectamgles()

    def move_right(self):
        if self.image_tk != None:
            Movement = min((self.crop_cords[2]-self.crop_cords[0])/2 , (1-self.crop_cords[2]) )
            self.crop_cords[0] += Movement 
            self.crop_cords[2] += Movement 
            self.refresh_image()  # Your method to display the image
            self.draw_rectamgles()

    # Command functions for arrow buttons
    def move_top_up(self):
        current_time = time.time()
        if current_time - self.last_zoom_time < 0.20:  # محدودیت 2 کلیک بر ثانیه
            self.delta_far_height = self.delta_far_height * 4
        self.last_zoom_time = current_time

        if self.rect_index  != None:
            self.coords[1] = max(0.0, self.coords[1] - self.delta_far_height)  # y1 -
            self.update_croped_image()

    def move_top_down(self):
        current_time = time.time()
        if current_time - self.last_zoom_time < 0.20:  # محدودیت 2 کلیک بر ثانیه
            self.delta_close_height = self.delta_close_height * 4
        self.last_zoom_time = current_time

        if self.rect_index  != None:
            if (self.coords[3] - self.coords[1]) > 3 * self.delta_close_height:
                self.coords[1] = min(1.0, self.coords[1] + self.delta_close_height)  # y1 +
            self.update_croped_image()

    def move_bottom_up(self):
        current_time = time.time()
        if current_time - self.last_zoom_time < 0.20:  # محدودیت 2 کلیک بر ثانیه
            self.delta_close_height = self.delta_close_height * 4
        self.last_zoom_time = current_time

        if self.rect_index  != None:
            if (self.coords[3] - self.coords[1]) > 3 * self.delta_close_height:
                self.coords[3] = max(0.0, self.coords[3] - self.delta_close_height)  # y2 -
            self.update_croped_image()

    def move_bottom_down(self):
        current_time = time.time()
        if current_time - self.last_zoom_time < 0.20:  # محدودیت 2 کلیک بر ثانیه
            self.delta_far_height = self.delta_far_height * 4
        self.last_zoom_time = current_time

        if self.rect_index  != None:
            self.coords[3] = min(1.0, self.coords[3] + self.delta_far_height)  # y2 +
            self.update_croped_image()

    def move_left_left(self):
        current_time = time.time()
        if current_time - self.last_zoom_time < 0.20:  # محدودیت 2 کلیک بر ثانیه
            self.delta_far_width = self.delta_far_width * 4
        self.last_zoom_time = current_time

        if self.rect_index  != None:
            self.coords[0] = max(0.0, self.coords[0] - self.delta_far_width)  # x1 -
            self.update_croped_image()

    def move_left_right(self):
        current_time = time.time()
        if current_time - self.last_zoom_time < 0.20:  # محدودیت 2 کلیک بر ثانیه
            self.delta_close_width = self.delta_close_width * 4
        self.last_zoom_time = current_time

        if self.rect_index  != None:
            if (self.coords[2] - self.coords[0]) > 3 * self.delta_close_width:
                self.coords[0] = min(1.0, self.coords[0] + self.delta_close_width)  # x1 +
            self.update_croped_image()

    def move_right_left(self):
        current_time = time.time()
        if current_time - self.last_zoom_time < 0.20:  # محدودیت 2 کلیک بر ثانیه
            self.delta_close_width = self.delta_close_width * 4
        self.last_zoom_time = current_time

        if self.rect_index  != None:
            if (self.coords[2] - self.coords[0]) > 3 * self.delta_close_width:
                self.coords[2] = max(0.0, self.coords[2] - self.delta_close_width)  # x2 -
            self.update_croped_image()

    def move_right_right(self):
        current_time = time.time()
        if current_time - self.last_zoom_time < 0.20:  # محدودیت 2 کلیک بر ثانیه
            self.delta_far_width = self.delta_far_width * 4
        self.last_zoom_time = current_time

        if self.rect_index  != None:
            self.coords[2] = min(1.0, self.coords[2] + self.delta_far_width)  # x2 +
            self.update_croped_image()

    def update_croped_image(self):
        # Reset all rectangles to their original color (if needed)
        if self.rect_index != None:
            # self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="blue")  # Reset to original color
            # Update data store
            self.rectangles[self.rect_index] = tuple(self.coords)
            self.project_data["rectangles"][self.project_data["images"][self.img_index]] = self.rectangles

            # Refresh rectangle list and redraw canvas rectangles
            self.draw_rectamgles()
            self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="red")

            # Update image preview
            self.update_edit_panel_and_image_crop()

    def Lock_Rectangle(self):
        if self.rect_index  != None:
            self.rec_islock = True
            self.IsLocks[self.rect_index] = self.rec_islock
            self.project_data["IsLocks"][self.project_data["images"][self.img_index]] = self.IsLocks
            # Refresh rectangle list and redraw canvas rectangles
            self.populate_rectangle_list()
            self.disable_frame()
    
    def go_next(self):
        if self.rect_index  != None:
            start_point = list((self.rect_index, self.img_index))
            current_point = list((self.rect_index + 1, self.img_index))
            self.rectangles = self.project_data["rectangles"][self.project_data["images"][current_point[1]]]
            while True:
                if current_point[0] >= len(self.rectangles):
                    current_point[0] = 0
                    current_point[1] += 1
                if current_point[1] >= len(self.project_data["images"]):
                    current_point[1] = 0
                self.rectangles = self.project_data["rectangles"][self.project_data["images"][current_point[1]]]
                self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][current_point[1]]]
                self.Labels = self.project_data["Labels"][self.project_data["images"][current_point[1]]]
                if self.IsLocks == []:
                    current_point[0] = 0
                    current_point[1] += 1
                    continue
                if not self.IsLocks[current_point[0]] or True:  # delete or True if you want to move just on unlocked rects
                    self.img_index = current_point[1]
                    self.rect_index = current_point[0]
                    self.rec_islock = self.IsLocks[current_point[0]]
                    self.coords = self.rectangles[current_point[0]]
                    self.Rec_Label = self.Labels[current_point[0]]  # Copy for editing
                    self.populate_rectangle_list()
                    if current_point[1] != start_point[1]:
                        self.crop_cords = list((0, 0, 1, 1))
                        self.zoom_factor = 1
                        self.display_image() # Your method to display the image number self.img_index
                    self.draw_rectamgles()
                    # self.update_edit_panel_and_image_crop()
                    self.update_rectangle_preview()
                    self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
                    self.label_entry.icursor(tk.END)  # Move cursor to end of text
                    return
                if current_point == start_point:
                    self.Lockandgo_button.config(state='disabled')
                    return                
                current_point[0] += 1

    def go_back(self):
        if self.rect_index  != None:
            start_point = list((self.rect_index, self.img_index))
            current_point = list((self.rect_index - 1, self.img_index))
            self.rectangles = self.project_data["rectangles"][self.project_data["images"][current_point[1]]]
            while True:
                if current_point[0] < 0:
                    current_point[1] -= 1
                if current_point[1] < 0:
                    current_point[1] = len(self.project_data["images"]) - 1
                self.rectangles = self.project_data["rectangles"][self.project_data["images"][current_point[1]]]
                self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][current_point[1]]]
                self.Labels = self.project_data["Labels"][self.project_data["images"][current_point[1]]]
                if current_point[0] < 0:
                    current_point[0] = len(self.rectangles) - 1
                if self.IsLocks == []:
                    continue
                if not self.IsLocks[current_point[0]] or True:  # delete or True if you want to move just on unlocked rects
                    self.img_index = current_point[1]
                    self.rect_index = current_point[0]
                    self.rec_islock = self.IsLocks[current_point[0]]
                    self.coords = self.rectangles[current_point[0]]
                    self.Rec_Label = self.Labels[current_point[0]]  # Copy for editing
                    self.populate_rectangle_list()
                    if current_point[1] != start_point[1]:
                        self.crop_cords = list((0, 0, 1, 1))
                        self.zoom_factor = 1
                        self.display_image() # Your method to display the image number self.img_index
                    self.draw_rectamgles()
                    # self.update_edit_panel_and_image_crop()
                    self.update_rectangle_preview()
                    self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
                    self.label_entry.icursor(tk.END)  # Move cursor to end of text
                    return
                if current_point == start_point:
                    self.Lockandgo_button.config(state='disabled')
                    return                
                current_point[0] -= 1

    def Lock_and_go_next(self):
        if self.rect_index  != None:
            self.rec_islock = True
            self.IsLocks[self.rect_index] = self.rec_islock
            self.project_data["IsLocks"][self.project_data["images"][self.img_index]] = self.IsLocks
            # Refresh rectangle list and redraw canvas rectangles
            self.populate_rectangle_list()
            self.disable_frame()

            start_point = list((self.rect_index, self.img_index))
            current_point = list((self.rect_index + 1, self.img_index))
            self.rectangles = self.project_data["rectangles"][self.project_data["images"][current_point[1]]]
            while True:
                if current_point[0] >= len(self.rectangles):
                    current_point[0] = 0
                    current_point[1] += 1
                if current_point[1] >= len(self.project_data["images"]):
                    current_point[1] = 0
                self.rectangles = self.project_data["rectangles"][self.project_data["images"][current_point[1]]]
                self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][current_point[1]]]
                self.Labels = self.project_data["Labels"][self.project_data["images"][current_point[1]]]
                if self.IsLocks == []:
                    current_point[0] = 0
                    current_point[1] += 1
                    continue
                if not self.IsLocks[current_point[0]]:
                    self.img_index = current_point[1]
                    self.rect_index = current_point[0]
                    self.rec_islock = self.IsLocks[current_point[0]]
                    self.coords = self.rectangles[current_point[0]]
                    self.Rec_Label = self.Labels[current_point[0]]  # Copy for editing
                    self.populate_rectangle_list()
                    if current_point[1] != start_point[1]:
                        self.display_image() # Your method to display the image number self.img_index
                        self.Auto_save_project()
                    self.draw_rectamgles()
                    # self.update_edit_panel_and_image_crop()
                    self.update_rectangle_preview()
                    self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
                    self.label_entry.icursor(tk.END)  # Move cursor to end of text
                    return
                if current_point == start_point:
                    self.Lockandgo_button.config(state='disabled')
                    return                
                current_point[0] += 1  

    def UnLock(self):
        if self.rect_index  != None:
            if self.rec_islock:
                self.rec_islock = False
            else:
                self.rec_islock = True
            self.IsLocks[self.rect_index] = self.rec_islock
            self.project_data["IsLocks"][self.project_data["images"][self.img_index]] = self.IsLocks
            # Refresh rectangle list and redraw canvas rectangles
            self.populate_rectangle_list()
            self.enable_frame()

    def Find_Persian_character_sequense2(self):
        search_text = self.char_sequense2.get()
        if search_text != "":
            Label_sequense = []
            for chr in search_text:
                if chr == 'ي':
                    chr = 'ی'
                if chr in self.Str_to_name:
                    Label_sequense.append(self.Str_to_name[chr])
                else:
                    messagebox.showerror('Error', f"This character is not in our Persian character list:\n\"{chr}\"")
                    continue

            if self.rect_index != None:
                start_point = list((self.rect_index, self.img_index))
                current_point = list((self.rect_index + 1, self.img_index))
                self.Labels = self.project_data["Labels"][self.project_data["images"][current_point[1]]]
                check = True
                while check:
                    if current_point[0] >= len(self.Labels) - len(Label_sequense) + 1:
                        current_point[0] = 0
                        current_point[1] += 1
                    if current_point[1] >= len(self.project_data["images"]):
                        current_point[1] = 0
                    self.rectangles = self.project_data["rectangles"][self.project_data["images"][current_point[1]]]
                    self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][current_point[1]]]
                    self.Labels = self.project_data["Labels"][self.project_data["images"][current_point[1]]]
                    if self.Labels == []:
                        current_point[0] = 0
                        current_point[1] += 1
                        continue
                    if  self.Labels[current_point[0]] == Label_sequense[0]:
                        found_sequense = []
                        for idx in range(len(Label_sequense)):
                            found_sequense.append(self.project_data["Labels"][self.project_data["images"][current_point[1]]][current_point[0] + idx])
                        if Label_sequense == found_sequense:
                            self.img_index = current_point[1]
                            self.rect_index = current_point[0]
                            self.rec_islock = self.IsLocks[current_point[0]]
                            self.coords = self.rectangles[current_point[0]]
                            self.Rec_Label = self.Labels[current_point[0]]  # Copy for editing
                            self.populate_rectangle_list()
                            if current_point[1] != start_point[1]:
                                self.crop_cords = list((0, 0, 1, 1))
                                self.zoom_factor = 1
                                self.display_image() # Your method to display the image number self.img_index
                            self.draw_rectamgles()
                            # self.update_edit_panel_and_image_crop()
                            self.update_rectangle_preview()
                            self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
                            self.label_entry.icursor(tk.END)  # Move cursor to end of text
                            check = False
                    if current_point == start_point:
                        check = False                
                    current_point[0] += 1

    def Find_Persian_character_sequense(self):
        while True:

            char_sequense = simpledialog.askstring("Find String", "Write the character sequense\nyou are looking for (In Persian):", initialvalue= self.char_sequense)

            if char_sequense == None:
                return
            else:
                self.char_sequense = char_sequense
                
            Label_sequense = []
            for chr in self.char_sequense:
                if chr == 'ي':
                    chr = 'ی'
                if chr in self.Str_to_name:
                    Label_sequense.append(self.Str_to_name[chr])
                else:
                    messagebox.showerror('Error', f"This character is not in our Persian character list:\n\"{chr}\"")
                    continue

            if self.rect_index != None:
                start_point = list((self.rect_index, self.img_index))
                current_point = list((self.rect_index + 1, self.img_index))
                self.Labels = self.project_data["Labels"][self.project_data["images"][current_point[1]]]
                check = True
                while check:
                    if current_point[0] >= len(self.Labels) - len(Label_sequense) + 1:
                        current_point[0] = 0
                        current_point[1] += 1
                    if current_point[1] >= len(self.project_data["images"]):
                        current_point[1] = 0
                    self.rectangles = self.project_data["rectangles"][self.project_data["images"][current_point[1]]]
                    self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][current_point[1]]]
                    self.Labels = self.project_data["Labels"][self.project_data["images"][current_point[1]]]
                    if self.Labels == []:
                        current_point[0] = 0
                        current_point[1] += 1
                        continue
                    if  self.Labels[current_point[0]] == Label_sequense[0]:
                        found_sequense = []
                        for idx in range(len(Label_sequense)):
                            found_sequense.append(self.project_data["Labels"][self.project_data["images"][current_point[1]]][current_point[0] + idx])
                        if Label_sequense == found_sequense:
                            self.img_index = current_point[1]
                            self.rect_index = current_point[0]
                            self.rec_islock = self.IsLocks[current_point[0]]
                            self.coords = self.rectangles[current_point[0]]
                            self.Rec_Label = self.Labels[current_point[0]]  # Copy for editing
                            self.populate_rectangle_list()
                            if current_point[1] != start_point[1]:
                                self.crop_cords = list((0, 0, 1, 1))
                                self.zoom_factor = 1
                                self.display_image() # Your method to display the image number self.img_index
                            self.draw_rectamgles()
                            # self.update_edit_panel_and_image_crop()
                            self.update_rectangle_preview()
                            self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
                            self.label_entry.icursor(tk.END)  # Move cursor to end of text
                            check = False
                    if current_point == start_point:
                        check = False                
                    current_point[0] += 1


    def Lock_All(self):
        for fname in self.project_data["images"]:
            for i in range(len(self.project_data["IsLocks"][fname])):
                self.project_data["IsLocks"][fname][i] = True
        self.populate_rectangle_list()
        self.update_edit_panel_and_image_crop()
        if self.rect_index != None:
            self.disable_frame()

    def unLock_All(self):
        for fname in self.project_data["images"]:
            for i in range(len(self.project_data["IsLocks"][fname])):
                self.project_data["IsLocks"][fname][i] = False
        self.populate_rectangle_list()
        self.update_edit_panel_and_image_crop()
        if self.rect_index != None:
            self.enable_frame()


    def Lock_This_Image(self):
        if self.img_index != None:
            fname = self.project_data["images"][self.img_index]
            for i in range(len(self.project_data["IsLocks"][fname])):
                self.project_data["IsLocks"][fname][i] = True
            self.populate_rectangle_list()
            self.update_edit_panel_and_image_crop()
            if self.rect_index != None:
                self.disable_frame()

    def unLock_This_Image(self):
        if self.img_index != None:
            fname = self.project_data["images"][self.img_index]
            for i in range(len(self.project_data["IsLocks"][fname])):
                self.project_data["IsLocks"][fname][i] = False

            self.populate_rectangle_list()
            self.update_edit_panel_and_image_crop()
            if self.rect_index != None:
                self.enable_frame()


    def Clear_BBox_list(self):
        if self.img_index != None:
            fname = self.project_data["images"][self.img_index]

            self.project_data["rectangles"][fname] = []
            self.project_data["IsLocks"][fname] = []
            self.project_data["Labels"][fname] = []

            self.rect_index = None
            self.populate_rectangle_list()
            self.update_edit_panel_and_image_crop()
            # self.disable_frame()

    def disable_frame(self):
        self.left_top_button.config(state='disabled')
        self.right_top_button.config(state='disabled')
        self.up_left_button.config(state='disabled')
        self.down_left_button.config(state='disabled')
        self.up_right_button.config(state='disabled')
        self.down_right_button.config(state='disabled')
        self.left_bottom_button.config(state='disabled')
        self.right_bottom_button.config(state='disabled')
        self.Lock_button.config(state='disabled')
        self.Lockandgo_button.config(state='disabled')
        self.label_entry.config(state='disabled')
        self.delete_button.config(state='disabled')
        self.UnLock_button.config(state='normal')

    def enable_frame(self):
        self.left_top_button.config(state='normal')
        self.right_top_button.config(state='normal')
        self.up_left_button.config(state='normal')
        self.down_left_button.config(state='normal')
        self.up_right_button.config(state='normal')
        self.down_right_button.config(state='normal')
        self.left_bottom_button.config(state='normal')
        self.right_bottom_button.config(state='normal')
        self.Lock_button.config(state='normal')
        self.Lockandgo_button.config(state='normal')
        self.Lockandgo_button.config(state='normal')
        self.label_entry.config(state='normal')
        self.delete_button.config(state='normal')
        self.UnLock_button.config(state='disabled')
    
    def on_mouse_wheel(self, event):
        # محاسبه مختصات نسبی مرکز بزرگنمایی
        convas_width = self.canvas.winfo_width()
        convas_height = self.canvas.winfo_height()
        center_x = self.crop_cords[0] + event.x / convas_width / self.zoom_factor
        center_y = self.crop_cords[1] + event.y / convas_height / self.zoom_factor 

        # تغییر ضریب بزرگنمایی بر اساس چرخش غربیلک
        if event.delta > 0:  # چرخش به سمت بالا
            self.zoom_factor = (self.zoom_factor * 1.2)  # بزرگنمایی
        else:  # چرخش به سمت پایین
            self.zoom_factor = max(1, self.zoom_factor / 1.2)  # کوچک‌نمایی

        # محاسبه طول و عرض نسبی تصویر زوم شده
        zoomed_width = 1 / self.zoom_factor
        zoomed_height = 1 / self.zoom_factor



        self.crop_cords = list((center_x-zoomed_width*(event.x / convas_width), center_y-zoomed_height*((event.y / convas_height)), center_x+zoomed_width*(1-((event.x / convas_width))), center_y+zoomed_height*(1-((event.y / convas_height)))))
        if self.crop_cords[0] < 0:
            self.crop_cords[2] += (0-self.crop_cords[0])
            self.crop_cords[0] = 0
        if self.crop_cords[1] < 0:
            self.crop_cords[3] += (0-self.crop_cords[1])
            self.crop_cords[1] = 0
        if self.crop_cords[2] > 1:
            self.crop_cords[0] -= (self.crop_cords[2] - 1)
            self.crop_cords[2] = 1
        if self.crop_cords[3] > 1:
            self.crop_cords[1] -= (self.crop_cords[3] - 1)
            self.crop_cords[3] = 1
        # چاپ مختصات و ابعاد
        self.refresh_image()  # Your method to display the image
        self.draw_rectamgles()
        self.update_rectangle_preview()

    # Function to update the rectangle and image preview
    def update_rectangle_preview(self):
        # Reset all rectangles to their original color (if needed)
        if self.rect_index != None:
            self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="blue")  # Reset to original color
            # Update data store
            self.rectangles[self.rect_index] = tuple(self.coords)
            self.project_data["rectangles"][self.project_data["images"][self.img_index]] = self.rectangles

            # Refresh rectangle list and redraw canvas rectangles
            self.populate_rectangle_list()
            # self.display_image()
            self.draw_rectamgles()
            self.canvas.itemconfig(self.rec_IDs[self.rect_index], outline="red")

            # Update image preview
            self.update_edit_panel_and_image_crop()

    def update_edit_panel_and_image_crop(self):
        if self.rect_index != None:
            self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]
            self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
            self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
            self.coords = list(self.rectangles[self.rect_index])  # Copy for editing
            self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
            self.Rec_Label = self.Labels[self.rect_index]  # Copy for editing
            # Crop the image based on rectangle coordinates
            x1, y1, x2, y2 = self.coords
            # self.crop_img در تابع display_image ایجاد شده است و در رزولوشن کامل است
            img_width, img_height = self.crop_img.size

            
            
            # Arrow Button Configuration
            self.delta_far_width = max(1 / img_width, 0.02*(self.coords[2]-self.coords[0])) # Small increment for coordinate changes
            self.delta_close_width = max(1 / img_width, self.delta_far_width / 2)  # Small increment for coordinate changes
            self.delta_far_height = max(1 / img_height, 0.02*(self.coords[3]-self.coords[1])) # Small increment for coordinate changes
            self.delta_close_height = max(1 / img_height, self.delta_far_height / 2)  # Small increment for coordinate changes


            # Calculate pixel coordinates
            left = int(x1 * img_width)
            top = int(y1 * img_height)
            right = int(x2 * img_width)
            bottom = int(y2 * img_height)

            # Ensure coordinates are within bounds
            left = max(0, left)
            top = max(0, top)
            right = min(img_width, right)
            bottom = min(img_height, bottom)

            # Crop the image
            cropped_img = self.crop_img.crop((left, top, right, bottom))

            canvas_width = self.crop_canvas.winfo_width()
            canvas_height = self.crop_canvas.winfo_height()

            ratio = max( cropped_img.width/(canvas_width) , cropped_img.height/(canvas_height) )

            # Resize the cropped image to fit the canvas
            cropped_img = cropped_img.resize((int(cropped_img.width / ratio), int(cropped_img.height / ratio)), Image.LANCZOS)
            cropped_img_tk = ImageTk.PhotoImage(cropped_img)

            # Update the canvas
            self.crop_canvas.delete("all")
            self.crop_canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=cropped_img_tk)
            self.crop_canvas.image = cropped_img_tk  # Keep a reference to prevent garbage collection
            self.crop_canvas.create_text(canvas_width // 2 - 1, canvas_height // 2 - 1, text=self.Rec_Label, 
                                 fill="white", font=("Times New Roman", 18, "bold"))
            self.crop_canvas.create_text(canvas_width // 2 + 1, canvas_height // 2 - 1, text=self.Rec_Label, 
                                 fill="white", font=("Times New Roman", 18, "bold"))
            self.crop_canvas.create_text(canvas_width // 2 - 1, canvas_height // 2 + 1, text=self.Rec_Label, 
                                 fill="white", font=("Times New Roman", 18, "bold"))
            self.crop_canvas.create_text(canvas_width // 2 + 1, canvas_height // 2 + 1, text=self.Rec_Label, 
                                 fill="white", font=("Times New Roman", 18, "bold"))
            self.crop_canvas.create_text(canvas_width // 2, canvas_height // 2, text=self.Rec_Label, 
                                 fill="blue", font=("Times New Roman", 18, "bold"))

            if self.rec_islock:
                self.disable_frame()
            else:
                self.enable_frame()
            
            if self.rect_index != None:
                self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
                self.label_var.set(self.Labels[self.rect_index])  # تغییر مقدار متغیر متنی
                self.label_entry.focus()  # اختیاری: فوکوس را به کادر متنی بدهد
        else:
            self.disable_frame()
            self.crop_canvas.delete("all")

    def Export_to_YAML(self):
        response = messagebox.askyesno("Caution", "آیا از درستی لیست لیبل‌ها و شماره هر لیبل اطمینان دارید؟\n\nبهر حال لیست لیبل‌ها در فایلی با پسوند yaml قرار داده خواهد شد.")
        if not response:
            return
        # شروع شمارش لیبلها
        current_number = len(self.label_to_number)  # شمارنده برای labelهای جدید
        # دریافت مسیرها از کاربر
        destination = filedialog.askdirectory(title="Select destination folder for Dataset in YAML fornat")
        if not destination:
            return  # User cancelled folder selection

        for image in self.project_data["images"]:
            rectangles = self.project_data["rectangles"][image]
            if rectangles != []:
                yolo_dataset = []
                image_full_path = os.path.join(self.project_data["image_folder"], image).replace("\\",  "/")
                filename, extension = os.path.splitext(os.path.basename(image_full_path))
                try:
                    img = Image.open(image_full_path)
                except Exception as e:
                    messagebox.showerror(title="Image Load Error", message=f"Failed to load image:\n{e}")
                    return
                
                Labels = self.project_data["Labels"][image]
                for rec, coords in enumerate(rectangles):
                    if self.project_data["IsLocks"][image][rec]:
                        # تغییر فرمت bounding box از xyxy به xywh
                        x1, y1, x2, y2 = coords
                        width = x2 - x1
                        height = y2 - y1
                        x_center = x1 + width / 2
                        y_center = y1 + height / 2

                        # manage labels
                        label = Labels[rec]

                        if not (label in self.label_to_number):
                            # اگر label جدید است، یک عدد جدید اختصاص بده
                            self.label_to_number[label] = current_number
                            current_number += 1

                        # اضافه کردن اطلاعات به متن فایل یامل
                        yolo_dataset.append(str(f"{self.label_to_number[label]:02d} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"))

                if yolo_dataset != []: # ذخیره محتوای هر فایل تصویری در یک فایل متنی
                    # Copy the image and generate .txt file           
                    new_path = os.path.join(destination, image).replace("\\",  "/")
                    img.save(new_path, quality=95)  

                    # ایجاد نام فایل متنی با پسوند .txt
                    txt_filename = os.path.splitext(filename)[0] + '.txt'
                    txt_path = os.path.join(destination, txt_filename).replace("\\",  "/")
                    with open(txt_path, 'w') as txt_file:
                        for line in yolo_dataset:
                            txt_file.write(line)
                            txt_file.write('\n')
            

        YAML_filename = 'List_of_Labels.yaml'
        YAML_path = os.path.join(destination, YAML_filename).replace("\\",  "/")
        # ذخیره لیست لیبل‌ها و شماره منتسب به هرکدام
        with open(YAML_path, 'w', encoding="utf-8") as txt_file:
            txt_file.write("train: ../images/train\n")
            txt_file.write("val:  ../images/val\n")
            txt_file.write("test:  \n\n")
            txt_file.write("#classes\n")
            txt_file.write("\nnames:\n")
            for label, number  in self.label_to_number.items():
                txt_file.write(f"  {number:02d}: \"{label}\"")
                txt_file.write("\n")
                

        messagebox.Message("عملیات با موفقیت انجام شد!")
        proceed = messagebox.askyesno(
            "Success",
            f"Project Splited successfully.\nThe folder is:\n{destination}\n\n Do you want to open the folder?"  )
        if proceed:
            os.startfile(destination)

    def Export_Image_to_YAML(self):
        response = messagebox.askyesno("Caution", "آیا از درستی لیست لیبل‌ها و شماره هر لیبل اطمینان دارید؟\n\nبهر حال لیست لیبل‌ها در فایلی به نام تصویر با پسوند yaml قرار داده خواهد شد.")
        if not response:
            return
            
        if self.img_index != None:
            # شروع شمارش لیبلها
            current_number = len(self.label_to_number)  # شمارنده برای labelهای جدید
            # دریافت مسیرها از کاربر
            destination = filedialog.askdirectory(title="Select the Folder to export image in YAML format")
            if not destination:
                return  # User cancelled folder selection
            
            image = self.project_data["images"][self.img_index]
            yolo_dataset = []
            image_full_path = os.path.join(self.project_data["image_folder"], image).replace("\\",  "/")
            fname, extension = os.path.splitext(os.path.basename(image_full_path))
            try:
                img = Image.open(image_full_path)
            except Exception as e:
                messagebox.showerror(title="Image Load Error", message=f"Failed to load image:\n{e}")
                return
            
            response = messagebox.askyesno("Locked or All", "همه موارد در فایل ذکر شوند (yes)\nفقط موارد قفل شده در فایل ذکر شوند (No)")
            rectangles = self.project_data["rectangles"][image]
            Labels = self.project_data["Labels"][image]
            for rec, coords in enumerate(rectangles):
                if self.project_data["IsLocks"][image][rec] or response:
                    # تغییر فرمت bounding box از xyxy به xywh
                    x1, y1, x2, y2 = coords
                    width = x2 - x1
                    height = y2 - y1
                    x_center = x1 + width / 2
                    y_center = y1 + height / 2

                    # manage labels
                    label = Labels[rec]

                    if not (label in self.label_to_number):
                        # اگر label جدید است، یک عدد جدید اختصاص بده
                        self.label_to_number[label] = current_number
                        current_number += 1

                    # اضافه کردن اطلاعات به متن فایل یامل
                    yolo_dataset.append(str(f"{self.label_to_number[label]:02d} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"))
            # Copy the image and generate .txt file           
            new_path = os.path.join(destination, image).replace("\\",  "/")
            img.save(new_path, quality=95)  

            # ایجاد نام فایل متنی با پسوند .txt
            txt_filename = os.path.splitext(fname)[0] + '.txt'
            txt_path = os.path.join(destination, txt_filename).replace("\\",  "/")

            # ذخیره محتوای هر فایل تصویری در یک فایل متنی
            with open(txt_path, 'w') as txt_file:
                for line in yolo_dataset:
                    txt_file.write(line)
                    txt_file.write('\n')

        YAML_filename = os.path.splitext(fname)[0] + '_List_of_Labels.yaml'
        YAML_path = os.path.join(destination, YAML_filename).replace("\\",  "/")
        # ذخیره لیست لیبل‌ها و شماره منتسب به هرکدام
        with open(YAML_path, 'w', encoding="utf-8") as txt_file:
            txt_file.write("train: ../images/train\n")
            txt_file.write("val:  ../images/val\n")
            txt_file.write("test:  \n\n")
            txt_file.write("#classes\n")
            txt_file.write("\nnames:\n")
            for label, number  in self.label_to_number.items():
                txt_file.write(f"  {number:02d}: \"{label}\"")
                txt_file.write("\n")


        messagebox.Message("عملیات با موفقیت انجام شد!")
        proceed = messagebox.askyesno(
            "Success",
            f"Image exported in YAML format successfully.\nThe folder is:\n{destination}\n\n Do you want to open the folder?")
        if proceed:
            os.startfile(destination)

    def Import_YOLO_dataset(self):

        self.clear_project_general_data()
        self.crop_canvas.delete("all")
        self.canvas.delete("all")
        self.image_tk = None
        self.lb2.delete(0, tk.END)  # Clear existing items
        self.lb1.delete(0, tk.END)  # Clear existing items

        # دریافت مسیرها از کاربر
        sourcepath = filedialog.askdirectory(title="Select Base Folder of the YOLO dataset to import")
        if not sourcepath:
            return  # User cancelled folder selection

        # دیکشنری برای نگاشت لیبل به عدد
        # دریافت مسیرها از کاربر
        Label_List_txt_path = filedialog.askopenfilename(
            title="Select the file containing list of label names",
            filetypes=[("list of label names", "*.yaml"), ("All Files", "*.*")]
        )
        if Label_List_txt_path:
            number_to_label = {}
            # Open file of label names
            try:
                with open(Label_List_txt_path, "r", encoding="utf-8") as f:
                    lines = [line.rstrip('\n') for line in f if line.strip()]
            except Exception as e:
                messagebox.showerror("Error", f"Could not read Label names file:\n{e}")
                return
            
            if len(lines) < 2:
                messagebox.showerror("Error", "Project file format is incorrect or incomplete.")
                return

            # Skip header lines
            i = 0
            while i < len(lines) and (not lines[i].startswith("names:")):
                    i += 1
            # Read label number and name per line
            i += 1
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                # جدا کردن عدد و متن داخل ""
                if ':' in line and '"' in line:
                    parts = line.split(':', 1)  # فقط اولین : را جدا کن
                    try:
                        number = int(parts[0].strip())  # تبدیل به عدد صحیح
                    except ValueError:
                        messagebox.showerror("Error", f"خطا: عدد نامعتبر در خط:\n{line}")
                        continue
                    
                    # پیدا کردن متن داخل ""
                    text_part = parts[1].strip()
                    if text_part.count('"') >= 2:
                        start = text_part.find('"') + 1
                        end = text_part.find('"', start)
                        label = text_part[start:end]
                        if not (label in number_to_label):
                            # اگر label جدید است، یک عدد جدید اختصاص بده
                            number_to_label[number] = label
                        else:
                            messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                    else:
                        messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                else:
                    messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")

                i += 1
                    
        else:
            messagebox.showinfo("Load failed", "No label list imported, not successful.")
            return  # User cancelled file selection
        messagebox.showinfo("Success", "New label list imported successfully.")

        image_files = [f for f in os.listdir(sourcepath)
                    if os.path.isfile(os.path.join(sourcepath, f)) and f.lower().endswith(".jpg")]
        self.project_data["images"] = image_files

        # Initialize empty rectangles list for each image
        self.project_data["rectangles"] = {img_path: [] for img_path in self.project_data["images"]}
        self.project_data["IsLocks"] = {img_path: [] for img_path in self.project_data["images"]}
        self.project_data["Labels"] = {img_path: [] for img_path in self.project_data["images"]}

        for image in image_files:
            rects = []
            isLocks = []
            Labels = []

            image_full_path = os.path.join(sourcepath, image).replace("\\",  "/")
            filename, extension = os.path.splitext(os.path.basename(image_full_path))
            # خواندن  فایل متنی با نام تصویر اگر وجود داشت .txt
            txt_filename = os.path.splitext(filename)[0] + '.txt'
            txt_path = os.path.join(sourcepath, txt_filename).replace("\\",  "/")

            try:
                with open(txt_path, "r", encoding="utf-8") as f:
                    lines = [line.rstrip('\n') for line in f if line.strip()]

                for i, rect_line in enumerate(lines):

                    try:
                        parts = rect_line.strip().split()
                        if len(parts) == 6:  # بررسی تعداد المان‌ها
                            label_txt, x_center, y_center, width, height, score = parts
                            label = number_to_label[int(label_txt)]
                        elif len(parts) == 5:  # بررسی تعداد المان‌ها
                            label_txt, x_center, y_center, width, height = parts
                            label = number_to_label[int(label_txt)]
                        else:
                            messagebox.showerror('Error', f"خطا در فرمت خط {i}: {rect_line}")
                            continue
                        x_center, y_center, width, height =  map(float, (x_center, y_center, width, height))
                        x1 = x_center - width / 2
                        x2 = x_center + width / 2
                        y1 = y_center - height / 2
                        y2 = y_center + height / 2

                        rects.append((x1,y1,x2,y2))
                        Labels.append(label)
                        isLocks.append(True)
                    except Exception as e:
                        messagebox.showerror('Error', f"خطا در پردازش خط {i}: {str(e)}")
                        continue

            
            except Exception as e:
                pass

            self.project_data["rectangles"][image] = rects
            self.project_data["IsLocks"][image] = isLocks
            self.project_data["Labels"][image] = Labels
 
        self.project_data["name"] = "Project_Name"
        self.project_data["project_folder"] = sourcepath
        self.project_data["image_folder"] = sourcepath

        project_txt_path = self.save_project()
        self.load_project_from_file(project_txt_path)

    def Merge_Project(self):
        project_txt_path = filedialog.askopenfilename(
            title="Select Project .txt file to import and Merge",
            filetypes=[("Project Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if project_txt_path:
            try:
                with open(project_txt_path, "r", encoding="utf-8") as f:
                    lines = [line.rstrip('\n') for line in f if line.strip()]
            except Exception as e:
                messagebox.showerror("Error", f"Could not read project file:\n{e}")
                return
            
        if len(lines) < 4:
            messagebox.showerror("Error", "Project file format is incorrect or incomplete.")
            return

        project_data = {
            "name": "",               # Project name (str)
            "project_folder": "",     # Project folder path (str)
            "image_folder": "",       # Folder where images are located (str)
            "images": [],             # List of image full paths (list of str)
            "rectangles": {},         # Dict of {image_path: [ (x1, y1, x2, y2), ... ] }
            "IsLocks": {},             # List of Lock boolian values for each Rectangle
            "Labels": {}           # List of Label name values for each Rectangle
        }

        # Parse header info
        if not lines[0].startswith("Project:"):
            messagebox.showerror("Error", "Project name not found in project file.")
            return
        project_data["name"] = lines[0][len("Project:"):].strip()

        if not lines[1].startswith("Project Folder:"):
            messagebox.showerror("Error", "Project folder path not found in project file.")
            return
        project_data["project_folder"] = lines[1][len("Project Folder:"):].strip()
        check_folder = os.path.exists(project_data["project_folder"])
        if not check_folder:
            project_data["project_folder"] = os.path.abspath(os.path.dirname(project_txt_path))
            messagebox.showinfo("Caution", f"Project folder didn't exist.\nWe suppose the current folder and continue.\n\n{project_data['project_folder']}")
            
        if not lines[2].startswith("Image Folder:"):
            messagebox.showerror("Error", "Image folder path not found in project file.")
            return
        project_data["image_folder"] = lines[2][len("Image Folder:"):].strip()
        check_folder = os.path.exists(project_data["image_folder"])
        if not check_folder:
            project_data["image_folder"] = os.path.abspath(os.path.dirname(project_txt_path)) + '\\images'
            messagebox.showinfo("Caution", f"Image folder didn't exist.\nWe suppose the default folder \"images\" and continue.\n\n{project_data['image_folder']}")

        # Parse images list - starting at line 4 until an empty line or "Rectangles per image:"
        i = 3
        image_files = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("Rectangles per image:"):
            line = lines[i]
            # Expected format: [N] filename
            if line.startswith('['):
                close_bracket_idx = line.find(']')
                if close_bracket_idx != -1:
                    fname = line[close_bracket_idx+1:].strip()
                    image_files.append(fname)
            i += 1
        project_data["images"] = image_files

        # Initialize empty rectangles list for each image
        project_data["rectangles"] = {img_path: [] for img_path in project_data["images"]}
        project_data["IsLocks"] = {img_path: [] for img_path in project_data["images"]}
        project_data["Labels"] = {img_path: [] for img_path in project_data["images"]}

        # Skip empty lines and "Rectangles per image:" header
        while i < len(lines) and (not lines[i].strip() or lines[i].startswith("Rectangles per image:")):
            i += 1

        # Parse rectangles per image
        while i < len(lines) and (not lines[i].startswith("names:")):
            line = lines[i].strip()
            if line.startswith('['):  # image line
                close_bracket_idx = line.find(']')
                if close_bracket_idx == -1:
                    i += 1
                    continue
                img_name = line[close_bracket_idx+1:].strip()
                # Find matching image path:
                img_path = None
                for p in project_data["images"]:
                    if os.path.basename(p) == img_name:
                        img_path = p
                        break
                i += 1
                # Read rectangles for this image (until next image or end)
                rects = []
                isLocks = []
                recLabels = []
                while i < len(lines) and (not lines[i].startswith('[')) and (not lines[i].startswith("names:")):
                    rect_line = lines[i].strip()
                    if rect_line.lower() != "no rectangles":
                        # Expected format: Rect: (x1, y1), (x2, y2)
                        if rect_line.startswith("Rect"):
                            coords_start = rect_line.find('(')
                            coords_end = rect_line.find(')')
                            coords_start2 = rect_line.find('(', coords_end)
                            coords_end2 = rect_line.find(')', coords_start2)
                            if coords_start != -1 and coords_end != -1 and coords_start2 != -1 and coords_end2 != -1:
                                try:
                                    x1, y1 = map(float, rect_line[coords_start+1:coords_end].split(','))
                                    x2, y2 = map(float, rect_line[coords_start2+1:coords_end2].split(','))
                                    rects.append((x1, y1, x2, y2))
                                except Exception:
                                    pass  # skip malformed
                            i += 1
                            if i < len(lines):
                                prop_line = lines[i].strip()
                                if prop_line.startswith('Lock'):
                                    # استخراج وضعیت قفل
                                    lock_status = lines[i].split(':=')[1].strip()  # جدا کردن قسمت بعد از ':='
                                    lock_value = lock_status.split('(')[1].split(')')[0].strip()  # استخراج مقدار داخل پرانتز
                                    # استخراج متن داخل گیومه
                                    class_text = lines[i].split('Class :=')[1].strip()  # جدا کردن قسمت بعد از 'Class :='
                                    class_value = class_text.split('"')[1]  # استخراج متن داخل گیومه
                                    isLocks.append(lock_value.lower() == 'true')
                                    recLabels.append(class_value)
                                else:
                                    messagebox.showerror("Error", "File not compatible, Every Rectangle needs a property line after it like Lock:= () Class:=\"\"")
                                    return
                                
                    i += 1


                if img_path:
                    project_data["rectangles"][img_path] = rects
                    project_data["IsLocks"][img_path] = isLocks
                    project_data["Labels"][img_path] = recLabels
            else:
                i += 1

        # اطلاعات دو پروژه با هم مخلوط شوند
        for fname in project_data["images"]:
            # تصاویر هم اسم بررسی شوند. اگر تصویر هم اسم وجود داشت از کاربر نظر خواهی شود
            if fname in self.project_data["images"]:
                response = messagebox.askyesno(
                    title='Image file exists!',
                    message=f"File {fname} exists. Do You want to replace the BBox contents?\n\nSource Image file will not be replaced", 
                    icon='question'
                    )
                if response == True:
                    self.project_data["rectangles"][fname] = project_data["rectangles"][fname]
                    self.project_data["IsLocks"][fname] = project_data["IsLocks"][fname]
                    self.project_data["Labels"][fname] = project_data["Labels"][fname]
                else:
                    continue
            else:
                self.project_data["images"].append(fname)
                self.project_data["rectangles"][fname] = project_data["rectangles"][fname]
                self.project_data["IsLocks"][fname] = project_data["IsLocks"][fname]
                self.project_data["Labels"][fname] = project_data["Labels"][fname]

                # Copy image files to the main project folder
                image_full_path = os.path.join(project_data["image_folder"], fname).replace("\\",  "/")
                # اگر فولدر مقصد وجود ندارد، ایجادش کن
                image_destination_path = self.project_data["image_folder"].replace("\\", "/")
                image_destination_path = os.path.abspath(image_destination_path)
                os.makedirs(image_destination_path, exist_ok=True)
                # تبدیل مسیرها به فرم استاندارد و مقایسه
                source_abs = os.path.abspath(project_data['image_folder'])

                if source_abs != image_destination_path:
                    try:
                        # مسیر مقصد کامل
                        dest_file = os.path.join(image_destination_path, os.path.basename(image_full_path)).replace("\\",  "/")
                        # بررسی وجود فایل در مقصد
                        if not os.path.exists(dest_file):
                            shutil.copy2(image_full_path, image_destination_path)
                        else:
                            messagebox.showinfo("Info", f"This file exsisted in destination!!\n      {fname}.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not copy image to destination:\n{e}\n image moved is: {fname}")
                else:
                    messagebox.showinfo("Info", f"Source and destination folders for images are the same\n      {source_abs}.")

        # Retrieve the list of rectangles for the first image
        image_files = self.project_data["images"]
        if image_files:
            self.populate_image_list(image_files)
            self.img_index = 0
            self.rectangles = self.project_data["rectangles"][self.project_data["images"][self.img_index]]
            self.IsLocks = self.project_data["IsLocks"][self.project_data["images"][self.img_index]]
            self.Labels = self.project_data["Labels"][self.project_data["images"][self.img_index]]
            if self.rectangles == []:
                self.rect_index = None
                self.label_var.set("")
                self.coords = None
                self.rec_islock = None
                self.Rec_Label = None
                self.crop_canvas.delete("all")
            else:
                self.rect_index = 0
                self.coords = list(self.rectangles[self.rect_index])  # Copy for editing
                self.rec_islock = self.IsLocks[self.rect_index]  # Copy for editing
                self.Rec_Label = self.Labels[self.rect_index]  # Copy for editing

            self.populate_rectangle_list()
            
            # activate first image
            self.lb1.selection_clear(0, tk.END)    # Clear any previous selection
            self.lb1.selection_set(self.img_index)              # Select the first item (index 0)
            self.lb1.activate(self.img_index)                  # Set the active item to the first one
            self.lb1.see(self.img_index)                      # Scroll to make sure the first item is visible
            self.lb1.focus_set()                 # Set keyboard focus to the listbox for better UX                
            self.display_image() # Your method to display the image number self.img_index
            self.draw_rectamgles()
            self.update_edit_panel_and_image_crop()
            self.label_entry.icursor(tk.END)  # Move cursor to end of text

        else:
            messagebox.showerror("Error", "No image is available in the project you selected.")
            return
        
        messagebox.showinfo("Success", "New Project successfully Merged to the current Project")

    def Import_Label_Names_List(self):
        # دیکشنری برای نگاشت label به عدد
        # دریافت مسیرها از کاربر
        Label_List_txt_path = filedialog.askopenfilename(
            title="Select the file containing list of label names",
            filetypes=[("list of label names", "*.yaml"), ("All Files", "*.*")]
        )
        if Label_List_txt_path:
            self.label_to_number = {}
            # Open file of label names
            try:
                with open(Label_List_txt_path, "r", encoding="utf-8") as f:
                    lines = [line.rstrip('\n') for line in f if line.strip()]
            except Exception as e:
                messagebox.showerror("Error", f"Could not read Label names file:\n{e}")
                return
            
            if len(lines) < 2:
                messagebox.showerror("Error", "Project file format is incorrect or incomplete.")
                return

            # Skip header lines
            i = 0
            while i < len(lines) and (not lines[i].startswith("names:")):
                    i += 1
            # Read label number and name per line
            i += 1
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                # جدا کردن عدد و متن داخل ""
                if ':' in line and '"' in line:
                    parts = line.split(':', 1)  # فقط اولین : را جدا کن
                    try:
                        number = int(parts[0].strip())  # تبدیل به عدد صحیح
                    except ValueError:
                        messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                        continue
                    
                    # پیدا کردن متن داخل ""
                    text_part = parts[1].strip()
                    if text_part.count('"') >= 2:
                        start = text_part.find('"') + 1
                        end = text_part.find('"', start)
                        label = text_part[start:end]
                        if not (label in self.label_to_number):
                            # اگر label جدید است، یک عدد جدید اختصاص بده
                            self.label_to_number[label] = number
                        else:
                            messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                    else:
                        messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                else:
                    messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")

                i += 1
                    
        else:
            return  # User cancelled folder selection
        messagebox.showinfo("Success", "New label list imported successfully.")


    def Merge_Label_Names_List(self):
        # دیکشنری برای نگاشت label به عدد
        # دریافت مسیرها از کاربر
        Label_List_txt_path = filedialog.askopenfilename(
            title="Select the file containing list of label names to merge",
            filetypes=[("list of label names", "*.yaml"), ("All Files", "*.*")]
        )
        if Label_List_txt_path:
            current_number = len(self.label_to_number)
            # Open file of label names
            try:
                with open(Label_List_txt_path, "r", encoding="utf-8") as f:
                    lines = [line.rstrip('\n') for line in f if line.strip()]
            except Exception as e:
                messagebox.showerror("Error", f"Could not read Label names file:\n{e}")
                return
            
            if len(lines) < 2:
                messagebox.showerror("Error", "Project file format is incorrect or incomplete.")
                return

            # Skip header lines
            i = 0
            while i < len(lines) and (not lines[i].startswith("names:")):
                    i += 1
            # Read label number and name per line
            i += 1
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                # جدا کردن عدد و متن داخل ""
                if ':' in line and '"' in line:
                    parts = line.split(':', 1)  # فقط اولین : را جدا کن
                    try:
                        temp_number = int(parts[0].strip())  # تبدیل به عدد صحیح
                    except ValueError:
                        messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                        continue
                    
                    # پیدا کردن متن داخل ""
                    text_part = parts[1].strip()
                    if text_part.count('"') >= 2:
                        start = text_part.find('"') + 1
                        end = text_part.find('"', start)
                        label = text_part[start:end]
                        if not (label in self.label_to_number):
                            # اگر label جدید است، یک عدد جدید اختصاص بده
                            self.label_to_number[label] = current_number
                            current_number += 1
                    else:
                        messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")
                else:
                    messagebox.showerror("Error", f"خطا: فرمت نامعتبر در خط: \n{line}")

                i += 1
                    
        else:
            return  # User cancelled folder selection
        # for label in self.label_to_number:
        #     print(f"{self.label_to_number[label]:02d}: \"{label:s}\"")

        
    def Reset_Label_Names_List(self):
        self.label_to_number = {}
        messagebox.showinfo("Success", "Label names list is cleared successfully.")

    def Change_Persian_Characters_to_Label_names(self):
        for fname in self.project_data["images"]:
            for i, label in enumerate(self.project_data["Labels"][fname]):
                if label == "ي":
                    label = "ی"

                if label in self.Str_to_name:
                    new_label = self.Str_to_name[label]
                else:
                    new_label = label

                self.project_data["Labels"][fname][i] = new_label

        self.populate_rectangle_list()  # Populate the rectangle list
        self.update_edit_panel_and_image_crop()
        self.label_entry.icursor(tk.END)  # Move cursor to end of text
        messagebox.showinfo("Success", "Persian Characters changed to labels successfully.")



    def Load_deep_learning_model(self):
        response = False
        if self.project_data["path_to_AI"] != "":
            response = messagebox.askyesno(
                title="جایگزین کردن مدل هوش مصنوعی]",
                message=f"یک هوش مصنوعی قبلا انتخاب شده. \nآیا مایل هستید هوش مصنوعی جدید جایگزین قبلی شود؟",
                icon=messagebox.WARNING
            )
            
        if response or self.project_data["path_to_AI"] == "":  # Yes (جایگزینی)
            try:
                AI_file = filedialog.askopenfilename(
                    title="Select AI .pt File",
                    filetypes=[("AI deep learning model", "*.pt"), ("All Files", "*.*")]
                )
                if AI_file:
                    self.project_data["path_to_AI"] = AI_file
                    messagebox.showinfo("Success", "ّهوش مصنوعی کمکی با موفقیت به‌روزرسانی شد")
                    response = messagebox.askyesno(
                        title="انتقال مدل به فولدر پروژه",
                        message=f"آیا مایلید فایل مدل هوش مصنوعی کمکی به فولدر پروژه منتقل شود؟",
                        icon=messagebox.WARNING
                    )
                    if response:
                        try:
                            new_dst_path = os.path.join(self.project_data["project_folder"], os.path.basename(AI_file)).replace("\\",  "/")
                            shutil.copy2(self.project_data["path_to_AI"], new_dst_path)
                            self.project_data["path_to_AI"] = new_dst_path
                            messagebox.showinfo("Info", f"ّهوش مصنوعی به فولدر پروژه منتقل شد با نام\n{os.path.basename(AI_file)}")
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not add model to project folder:\n\n{e}")
                            
                else:
                    return
                
                self.model = YOLO(self.project_data["path_to_AI"])
                self.model.eval()


            except Exception as e:
                messagebox.showerror("Error", f"Could not read AI model file:\n{e}")
                return
 
        else:  # No هیچ کاری نکن
            return
        
    def Apply_deep_learning_model(self):
        do_message_flag = False
        if self.model:
            if self.img_index != None:
                fname = self.project_data["images"][self.img_index]
                image_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")

                results = self.model.predict(image_path, verbose=False)
                prediction_coords = results[0].boxes.xywhn.cpu().numpy()
                classs = results[0].boxes.cls.cpu().numpy()
                names = results[0].names
                result_file_name = fname[:-4] + '.txt'
                result_file_path = os.path.join(self.project_data["image_folder"], result_file_name).replace("\\",  "/")
                os.remove(result_file_path) if os.path.exists(result_file_path) else None
                # Save results if needed
                # results[0].save_txt(result_file_path, False)

                # مرتب‌سازی بر اساس مختصات x مرکز
                sorted_indices = np.argsort(prediction_coords[:, 0])[::-1]
                prediction_coords = prediction_coords[sorted_indices]   
                classs = classs[sorted_indices].astype(int)   
                if len(classs) > 0:
                    if self.project_data["rectangles"][fname] != []:
                        do_message_flag = True
                        response = messagebox.askyesno(
                            title="اطلاعات موجود",
                            message=f"آیا لیست اشیاء موجود برای این تصویر نگه داشته شوند؟",
                            icon=messagebox.WARNING
                        )
                        if not response:
                            self.project_data["rectangles"][fname] = []
                            self.project_data["IsLocks"][fname] = []
                            self.project_data["Labels"][fname] = []

                    for i in range(len(sorted_indices)):
                        x1 = prediction_coords[i][0] - prediction_coords[i][2] / 2
                        x2 = prediction_coords[i][0] + prediction_coords[i][2] / 2
                        y1 = prediction_coords[i][1] - prediction_coords[i][3] / 2
                        y2 = prediction_coords[i][1] + prediction_coords[i][3] / 2

                        self.project_data["rectangles"][fname].append((x1,y1,x2,y2))
                        self.project_data["IsLocks"][fname].append(False)
                        self.project_data["Labels"][fname].append(names[classs[i]])

                    self.rect_index = 0
                    self.crop_cords = list((0, 0, 1, 1))
                    self.zoom_factor = 1
                    self.refresh_image()  # Your method to display the image number self.img_index
                    self.draw_rectamgles()
                    self.populate_rectangle_list()  # Populate the rectangle list
                    self.update_edit_panel_and_image_crop()
                    self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
                    self.label_entry.icursor(tk.END)  # Move cursor to end of text
                else:
                    messagebox.showinfo("Nothing", "Nothing is found in this image.")
                    return
                if do_message_flag:
                    messagebox.showinfo("Info", f" مدل هوش مصنوعی با آدرس \n{self.project_data["path_to_AI"]}\n روی تصویر \n {fname}\n اجرا شد و نتیجه به لیست اشیا اضافه شد")
            else:
                messagebox.showinfo("No image", "No image is selected,\nnot successful.")
                return  # No image is selected
        else:
            messagebox.showinfo("No AI model", "No AI model is available,\nnot successful.")
            return  # No AI model is available

    def Apply_deep_learning_model_to_All(self):
        if self.model:
            for idx, fname in enumerate(self.project_data["images"]):
                if self.project_data["rectangles"][fname] == []:
                    try:
                        image_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")
                        results = self.model.predict(image_path, verbose=False)
                        prediction_coords = results[0].boxes.xywhn.cpu().numpy()
                        classs = results[0].boxes.cls.cpu().numpy()
                        names = results[0].names
                        result_file_name = fname[:-4] + '.txt'
                        result_file_path = os.path.join(self.project_data["image_folder"], result_file_name).replace("\\",  "/")
                        os.remove(result_file_path) if os.path.exists(result_file_path) else None
                        # Save results if needed
                        # results[0].save_txt(result_file_path, False)

                        # مرتب‌سازی بر اساس مختصات x مرکز
                        sorted_indices = np.argsort(prediction_coords[:, 0])[::-1]
                        prediction_coords = prediction_coords[sorted_indices]   
                        classs = classs[sorted_indices].astype(int)   
                        if len(classs) > 0:
                            for i in range(len(sorted_indices)):
                                x1 = prediction_coords[i][0] - prediction_coords[i][2] / 2
                                x2 = prediction_coords[i][0] + prediction_coords[i][2] / 2
                                y1 = prediction_coords[i][1] - prediction_coords[i][3] / 2
                                y2 = prediction_coords[i][1] + prediction_coords[i][3] / 2

                                self.project_data["rectangles"][fname].append((x1,y1,x2,y2))
                                self.project_data["IsLocks"][fname].append(False)
                                self.project_data["Labels"][fname].append(names[classs[i]])

                    except:
                        continue
                self.apply_ai.config(text=f"{idx}")  
                self.apply_ai.update()  # به روز رسانی فوری رابط کاربری
 

            self.apply_ai.config(text="Apply AI")                    
            self.apply_ai.update()  # به روز رسانی فوری رابط کاربری

            self.rect_index = 0
            self.crop_cords = list((0, 0, 1, 1))
            self.zoom_factor = 1
            self.refresh_image()  # Your method to display the image number self.img_index
            self.draw_rectamgles()
            self.populate_rectangle_list()  # Populate the rectangle list
            self.update_edit_panel_and_image_crop()
            self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
            self.label_entry.icursor(tk.END)  # Move cursor to end of text
        
            messagebox.showinfo("Info", f" مدل هوش مصنوعی با آدرس \n{self.project_data["path_to_AI"]}\n روی تصاویری که شیئی در آنها مشخص نشده بود اجرا شد و نتیجه به لیست اشیا اضافه شد")


    def Check_Label_Conflict(self):
        # اگر هوش مصنوعی در صفحه حاضر یک کاراکتر با لیبل متفاوت نسبت به دیتاست تشخیص دهد آنرا به لیست اضافه خواهد کرد
        self.Change_Persian_Characters_to_Label_names
        def Caculate_IoU(rec, new_rec):
            # استخراج مختصات مستطیل اول
            x1_1, y1_1, x2_1, y2_1 = rec
            # استخراج مختصات مستطیل دوم
            x1_2, y1_2, x2_2, y2_2 = new_rec
            
            # محاسبه مساحت هر مستطیل
            area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
            area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
            
            # محاسبه مختصات مستطیل مشترک
            x_left = max(x1_1, x1_2)
            y_top = max(y1_1, y1_2)
            x_right = min(x2_1, x2_2)
            y_bottom = min(y2_1, y2_2)
            
            # محاسبه مساحت مشترک
            intersection_area = 0
            if x_right > x_left and y_bottom > y_top:
                intersection_area = (x_right - x_left) * (y_bottom - y_top)
            
            # محاسبه مساحت ترکیب
            union_area = area1 + area2 - intersection_area
            # محاسبه IoU (Intersection over Union)
            IoU = intersection_area / union_area if union_area > 0 else 0
            return IoU

        if self.model:
            if self.img_index != None:
                fname = self.project_data["images"][self.img_index]
                image_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")

                results = self.model.predict(image_path, verbose=False)
                prediction_coords = results[0].boxes.xywhn.cpu().numpy()
                classs = results[0].boxes.cls.cpu().numpy()
                names = results[0].names

                # مرتب‌سازی بر اساس مختصات x مرکز
                sorted_indices = np.argsort(prediction_coords[:, 0])[::-1]
                prediction_coords = prediction_coords[sorted_indices]   
                classs = classs[sorted_indices].astype(int)  

                # تولید لیست تشخیص جدید
                new_rectangles = []
                new_IsLocks = []
                new_Labels = []
                for i in range(len(sorted_indices)):
                    x1 = prediction_coords[i][0] - prediction_coords[i][2] / 2
                    x2 = prediction_coords[i][0] + prediction_coords[i][2] / 2
                    y1 = prediction_coords[i][1] - prediction_coords[i][3] / 2
                    y2 = prediction_coords[i][1] + prediction_coords[i][3] / 2

                    new_rectangles.append((x1,y1,x2,y2))
                    new_IsLocks.append(False)
                    new_Labels.append(names[classs[i]])

                # بررسی همپوشانی‌ها با پارامتر IoU
                for idx, rec in  enumerate(self.project_data["rectangles"][fname]):
                    for idy, new_rec in enumerate(new_rectangles):
                        IoU = Caculate_IoU(rec, new_rec)

                        if IoU > 0.93 and new_Labels[idy]==self.project_data["Labels"][fname][idx]:
                            del new_rectangles[idy]
                            del new_IsLocks[idy]
                            del new_Labels[idy]
                            continue
                for idy, new_rec in enumerate(new_rectangles):
                    max_match_rec_idx = None
                    max_IoU = 0.0
                    for idx, rec in  enumerate(self.project_data["rectangles"][fname]):
                        IoU = Caculate_IoU(rec, new_rec)
                        if IoU > max_IoU:
                            max_match_rec_idx = idx
                            max_IoU = IoU
                    if max_match_rec_idx != None:
                        # self.project_data["IsLocks"][fname][max_match_rec_idx] = False
                        if max_IoU > 0.9 and new_Labels[idy]!=self.project_data["Labels"][fname][max_match_rec_idx]:
                            print(f"In {fname}, new rec {idy:>3d}: {new_Labels[idy]:<6s} has conflict with rec {max_match_rec_idx + 1:>3d}: {self.project_data["Labels"][fname][max_match_rec_idx]:<6s} IoU = {max_IoU:0.4f}")
                            self.project_data["rectangles"][fname].insert(max_match_rec_idx+1, new_rec)
                            self.project_data["IsLocks"][fname].insert(max_match_rec_idx+1, False)
                            self.project_data["Labels"][fname].insert(max_match_rec_idx+1, new_Labels[idy])

                messagebox.showinfo("Info", f" مدل هوش مصنوعی روی تصویر \n {fname}\n آزمایش شد")
            else:
                messagebox.showinfo("No image", "No image is selected,\nnot successful.")
                return  # No image is selected
            
            self.rect_index = 0
            self.crop_cords = list((0, 0, 1, 1))
            self.zoom_factor = 1
            self.refresh_image()  # Your method to display the image number self.img_index
            self.draw_rectamgles()
            self.populate_rectangle_list()  # Populate the rectangle list
            self.update_edit_panel_and_image_crop()
            self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
            self.label_entry.icursor(tk.END)  # Move cursor to end of text

        else:
            messagebox.showinfo("No AI model", "No AI model is available,\nnot successful.")
            return  # No AI model is available


    def Check_All_Label_Conflict(self):
        # اگر هوش مصنوعی در هر صفحه‌ای یک کاراکتر با لیبل متفاوت نسبت به دیتاست تشخیص دهد آنرا به لیست اضافه خواهد کرد
        self.Change_Persian_Characters_to_Label_names
        def Caculate_IoU(rec, new_rec):
            # استخراج مختصات مستطیل اول
            x1_1, y1_1, x2_1, y2_1 = rec
            # استخراج مختصات مستطیل دوم
            x1_2, y1_2, x2_2, y2_2 = new_rec
            
            # محاسبه مساحت هر مستطیل
            area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
            area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
            
            # محاسبه مختصات مستطیل مشترک
            x_left = max(x1_1, x1_2)
            y_top = max(y1_1, y1_2)
            x_right = min(x2_1, x2_2)
            y_bottom = min(y2_1, y2_2)
            
            # محاسبه مساحت مشترک
            intersection_area = 0
            if x_right > x_left and y_bottom > y_top:
                intersection_area = (x_right - x_left) * (y_bottom - y_top)
            
            # محاسبه مساحت ترکیب
            union_area = area1 + area2 - intersection_area
            # محاسبه IoU (Intersection over Union)
            IoU = intersection_area / union_area if union_area > 0 else 0
            return IoU

        if self.model:
            Count_conflicts = 0
            for image_idx, fname  in enumerate(self.project_data["images"]):
                image_path = os.path.join(self.project_data["image_folder"], fname).replace("\\",  "/")

                results = self.model.predict(image_path, verbose=False)
                prediction_coords = results[0].boxes.xywhn.cpu().numpy()
                classs = results[0].boxes.cls.cpu().numpy()
                names = results[0].names

                # مرتب‌سازی بر اساس مختصات x مرکز
                sorted_indices = np.argsort(prediction_coords[:, 0])[::-1]
                prediction_coords = prediction_coords[sorted_indices]   
                classs = classs[sorted_indices].astype(int)  

                # تولید لیست تشخیص جدید
                new_rectangles = []
                new_IsLocks = []
                new_Labels = []
                for i in range(len(sorted_indices)):
                    x1 = prediction_coords[i][0] - prediction_coords[i][2] / 2
                    x2 = prediction_coords[i][0] + prediction_coords[i][2] / 2
                    y1 = prediction_coords[i][1] - prediction_coords[i][3] / 2
                    y2 = prediction_coords[i][1] + prediction_coords[i][3] / 2

                    new_rectangles.append((x1,y1,x2,y2))
                    new_IsLocks.append(False)
                    new_Labels.append(names[classs[i]])

                # بررسی همپوشانی‌ها با پارامتر IoU
                for idx, rec in  enumerate(self.project_data["rectangles"][fname]):
                    for idy, new_rec in enumerate(new_rectangles):
                        IoU = Caculate_IoU(rec, new_rec)

                        if IoU > 0.93 and new_Labels[idy]==self.project_data["Labels"][fname][idx]:
                            del new_rectangles[idy]
                            del new_IsLocks[idy]
                            del new_Labels[idy]
                            continue
                for idy, new_rec in enumerate(new_rectangles):
                    max_match_rec_idx = None
                    max_IoU = 0.0
                    for idx, rec in  enumerate(self.project_data["rectangles"][fname]):
                        IoU = Caculate_IoU(rec, new_rec)
                        if IoU > max_IoU:
                            max_match_rec_idx = idx
                            max_IoU = IoU
                    if max_match_rec_idx != None:
                        # self.project_data["IsLocks"][fname][max_match_rec_idx] = False
                        if max_IoU > 0.9 and new_Labels[idy]!=self.project_data["Labels"][fname][max_match_rec_idx]:
                            print(f"In {fname}, new rec {idy:>3d}: {new_Labels[idy]:<6s} has conflict with rec {max_match_rec_idx + 1:>3d}: {self.project_data["Labels"][fname][max_match_rec_idx]:<6s} IoU = {max_IoU:0.4f}")
                            self.project_data["rectangles"][fname].insert(max_match_rec_idx+1, new_rec)
                            self.project_data["IsLocks"][fname].insert(max_match_rec_idx+1, False)
                            self.project_data["Labels"][fname].insert(max_match_rec_idx+1, new_Labels[idy])
                            Count_conflicts += 1
            
                self.apply_ai.config(text=f"{Count_conflicts}/{image_idx}")  
                self.apply_ai.update()  # به روز رسانی فوری رابط کاربری
 
            self.apply_ai.config(text="Apply AI")                    
            self.apply_ai.update()  # به روز رسانی فوری رابط کاربری

            messagebox.showinfo("Info", f"در مجموع تصاویر {Count_conflicts} اختلاف دیده شد. موارد جدید به صورت قفل نشده در لیست اضافه شده اند.")

        else:
            messagebox.showinfo("No AI model", "No AI model is available,\nnot successful.")
            return  # No AI model is available

        if (self.rect_index != None) and (self.img_index != None):
            self.crop_cords = list((0, 0, 1, 1))
            self.zoom_factor = 1
            self.refresh_image()  # Your method to display the image number self.img_index
            self.draw_rectamgles()
            self.populate_rectangle_list()  # Populate the rectangle list
            self.update_edit_panel_and_image_crop()
            self.label_entry.focus_set()                 # Set keyboard focus to the labeling box for better UX                
            self.label_entry.icursor(tk.END)  # Move cursor to end of text

def main():
    app = ProjectViewerApp()
    app.state('zoomed')
    app.mainloop()

if __name__ == "__main__":
    main()
