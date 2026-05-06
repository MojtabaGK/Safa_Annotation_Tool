![Downloads](https://img.shields.io/github/downloads/MojtabaGK/Labeling_App_OCR/total.svg)


# Labeling_App_OCR
An App in python for labeling and managing annotation of small objects, optimized for OCR purposes.

Good for:
- Small object annotation,
- Textual image annotation,
- Character detection,
- Layout Parsing purposes,
- Modification of datasets compatible with YOLO or similar object detection models,
- ....

Options:
- Open source and easy to personalize,
- zoom in the image
- Use of keyboard for easy labeling (needs personalization),
- project splitting,
- precisely modifiying annotaions,
- personal Artificial Inteligence Assistant,
- Generation and modification of a YOLO compatible dataset, 
- ....

<img width="1199" height="751" alt="1" src="https://github.com/user-attachments/assets/4cff4c84-4e20-42ac-ac08-0ab2d0c30054" />


***
## User Guide:
***
### "New Project"

#### Access Path:
  - File → New Project

#### Description:
  - This feature creates a new project and imports image data from a source folder.

#### Step-by-Step Process:
- **1. Select Project Location:**
  + A file dialog opens asking you to choose the parent directory for your new project.
  + Navigate to your desired location and click "Select Folder".
  + To cancel, close the dialog or click "Cancel".

- **2. Name Your Project:**
  + An input dialog prompts you to enter a name for your new project.
  + Type your project name and click "OK".
  + To cancel, close the dialog or click "Cancel".

- **3. Select Image Source:**
  + Another file dialog opens asking you to select the folder containing your JPG images.
  + Navigate to your image folder and click "Select Folder".
  + To cancel, close the dialog or click "Cancel".
  + Only JPG images from the selected source folder will be available in your project (You can modify the source code).
  + The project is now ready with your image data imported.

***
---
### "Open Project"

#### Access Path:
  + File → Open Project

#### Description:
  + Opens an existing project from a saved project file (.txt).

#### Step-by-Step Process:
- **1. Select Project file:**
  + Select the project's .txt file when prompted.
  + The system loads all project settings and paths automatically.
  + **What gets loaded from the .txt file?:**
  + Project name and folder
  + Image folder location
  + AI model path (if included and valid)
  + List of images in the project (By default availabele in "images" folder besides the .txt project file)
  + List of annotations for each image
  + Label names (if available)

- **2. Load the AI assistant model if you want:**
  + You'll be asked whether to load the AI assistant model if one is specified in the project file.
  + To cancel loading, close the dialog or click "Cancel".
    
- **Important Notes:**
  + If you see an error about file format, check that the .txt project file contains all required sections.

***
---
### "Add New Image to the Project"

#### Access Path:
  + File → Add New Image to the Project

#### Description:
  + Adds one or more new images (and their corresponding annotation files) to an existing project.

#### Step-by-Step Process:
- **1. Select Image Files:**
  + A file dialog opens where you can select multiple JPG images to add.
  + Select the desired image files and click "Open".
  + If an image with the same name exists in the project, system asks whether you want to replace it or rename it or neglect it. 
  + To cancel, close the dialog or click "Cancel".

- **2. Choose Annotation Import Option:**
  + A dialog asks if you want to check for corresponding annotation files (.txt files with same name as images).
  + Select "Yes" to import existing annotations, or "No" to add images without annotations.

- **3. Process Each Image:**
  + For each selected image, the system checks if a corresponding .txt annotation file exists in the same folder.
  + If found and you chose to import annotations, you'll be asked separately for each file whether to import its content.
  + The images (and optionally their annotations) are added to your project.

#### Important Notes:
  + Only JPG images are supported by default (you can modify the source code to support other formats).
  + Annotation files must have the exact same name as the image files (except with .txt extension).
  + If you choose not to import annotations, you can add them manually later within the application.

***
---
### "Save Project As"

#### Access Path:
  + File → Save Project As

#### Description:
  + Saves the current project with all its data (images, annotations, labels, and AI model path) to a new `.txt` project file.

#### Step-by-Step Process:
- **1. Choose Save Location:**
  + A file dialog opens asking where to save the project file.
  + Select the desired location and filename, then click "Save". By default, the filename is based on the project name.
  + To cancel, close the dialog or click "Cancel".

- **2. Automatic File Creation:**
  + The system creates a `.txt` file containing all project information:
  + The system copies all project images to an `images` folder next to the saved project file.

#### Important Notes:
  + After saving with "Save Project As", **you must open the newly saved project file** to continue editing that version. If you don't open the new file, you'll continue editing the original project.
  + If an image already exists in the destination, you'll receive a warning.
  + If an image is missing from the source, you'll be notified.

***
---
### "Find Persian Character Sequence"

#### Access Path:
  + Edit → Find Persian Character Sequence

#### Description:
  + Searches through all annotations in the project to find a specific sequence of Persian characters in labels.

#### Step-by-Step Process:
- **1. Enter Search Text:**
  + A dialog box appears asking you to enter the Persian character sequence you want to find.
  + The previously searched text (if any) is shown as the default.
  + Type your search text and click "OK", or click "Cancel" to abort.

- **2. Automatic Search:**
  + The system searches through all images and annotations starting from your current position.
  + It looks for labels that match your entered character sequence exactly.
  + The search wraps around to the beginning if it reaches the end of the project.

- **3. Result Handling:**
  + **If found:** The view automatically jumps to the first matching annotation.
  + **If not found:** The search returns to your starting point without changing the view.

#### Important Notes:
  + The character `'ي'` (Arabic Yeh) is automatically converted to `'ی'` (Persian Yeh) for compatibility.
  + Only characters that exist in the application's Persian character list can be searched (You can personalize this option).
  + This feature only searches through **existing labels** in your annotations.
  + If a character in your search text isn't in the Persian character list, you'll see an error message.
  + After finding a match, you can continue searching for the same sequence by running the command again.


***
---
### Lock/Unlock/Clear Functions

#### Access Path:
  + Edit → [Lock All/unLock All/Lock This Image/unLock This Image/Clear Bounding Box for the Current Image]

#### Description:
  + These functions allow you to lock or unlock annotations to prevent accidental modifications.

#### "Lock All"
  + Locks **all annotations** across **all images** in the entire project.
  + All bounding boxes become non-editable.
  + Prevents accidental changes to annotations throughout the project.

#### "unLock All"
  + Unlocks **all annotations** across **all images** in the entire project.
  + All bounding boxes become editable again.
  + Use this when you need to make widespread changes to annotations.

#### "Lock This Image"
  + Locks **all annotations** only in the **currently displayed image**.
  + All bounding boxes in the current image become non-editable.
  + Annotations in other images remain unaffected.

#### "unLock This Image"
  + Unlocks **all annotations** only in the **currently displayed image**.
  + All bounding boxes in the current image become editable again.
  + Annotations in other images remain unaffected.

#### "Clear Bounding Box for the Current Image"
  + Removes **all annotations** from the **currently displayed image**.
  + Deletes all bounding boxes and their labels from the current image.
  + The image becomes completely unannotated.
  + **Warning:** This action cannot be undone through the interface (consider saving your project first).

#### Important Notes:
  + It's recommended to save your project before using "Clear" to avoid accidental data loss.
  + Locked annotations are protected from accidental deletion or modification.
  + Use locking when you're satisfied with annotations and want to prevent changes.
  + Use unlocking when you need to correct or improve annotations.
  + The "Clear" function works even on locked annotations in the current image.

***
---
## Export Functions

#### Access Path:
  + Export → [Various Export Options]

#### Description:
  + These functions allow you to export annotated images and data in different formats for various purposes.
---
#### "Split Images by BBoxes"
  + Creates individual cropped images for **every bounding box** across **all images** in the project.
  + One image file per bounding box, cropped to the annotation boundaries.
  + Useful for creating datasets for object classification or analysis.

#### "Split Images by BBoxes and Label"
  + Creates individual cropped images for **every bounding box** with **specified  label**.
  + Ideal for training classification models where each class needs separate folders.
  + Useful to see how many patterns correspond to each class/label.

#### "Export to YAML Format"
  + Exports **all project annotations** to a structured YAML file.
  + An image_name.txt file is created for every image_name.jpg to keep the annotations.
  + A `.yaml` file containing label names in machine-readable format is created.
  + Suitable for use with various machine learning frameworks and data pipelines.

#### "Split Current Image by BBoxes"
  + Creates individual cropped images for **every bounding box** in the **currently displayed image only**.
  + One image file per bounding box from the current image.
  + Useful for exporting annotations from specific images.

#### "Export Current Image to YAML Format"
  + Exports annotations from the **currently displayed image only** to a YAML file.
  + An image_name.txt file is created for every image_name.jpg to keep the annotations.
  + A `.yaml` file containing label names for the current image is created.
  + Useful for exporting single image annotations.

#### "Split Current Image by BBoxes and Label"
  + Creates individual cropped images for **every bounding box** with **specified  label** in the **currently displayed image only**.
  + Ideal for training classification models where each class needs separate folders.
  + Useful to see how many patterns correspond to each class/label.

#### "Split Project by Current Image"
  + Creates a new project containing **only the currently displayed image** and its annotations.
  + A new project file with a single image and its corresponding annotations.
  + Useful for isolating specific images for testing or sharing.

#### Important Notes:
  + Export functions create new files/folders and do not modify your original project.
  + Ensure your labels are consistent and valid.
  + YAML exports maintain all annotation details including coordinates, labels, and image references.
  + Always check the output location as files may be saved in different directories based on the function.
  + You can modify the source code to generate other image formats than ".jpg"

***
---
### Import Functions

#### Access Path:
  + Import → [Various Import Options]

#### Description:
  + These functions allow you to import external data and annotations into your current project.

---

### "Import YOLO Database"
  + Imports annotations from a YOLO-format dataset into your current project.
  + Select the YOLO dataset folder when prompted.
  + The system reads YOLO annotation files (.txt) and matches them with corresponding images.
  + Annotations are converted to the project's internal format and added to your project.
  + Remember to "Save Project As" if you want.

#### Requirements:
  + Label files must have the same name as image files with `.txt` extension.
  + YOLO dataset must be like: image_name.txt and image_name.jpg in the same folder.
  + YOLO format: `class_id x_center y_center width height` (normalized coordinates).
  + Class names should be imported with the exsisting .YAML file.

### "Merge with another Project"
  + Combines annotations and images from another project file into your current project.
  + Select another project's `.txt` file when prompted.
  + The system reads the project file and imports its data.
  + Images and annotations are added to your current project (duplicates may be handled based on implementation).

#### Important Notes:
  + Label names from both projects will be preserved and merged.
  + The merged project retains the current project's settings and AI model path.
  + Consider backing up your current project before merging.

#### Use Cases:
  + Combining annotations from multiple team members.
  + Adding new images and annotations from another project version.
  + Creating larger datasets from smaller projects.

***
---
### Label Management Functions

#### Access Path:
  + Labels → [Various Label Management Options]

#### Description:
  + These functions help you manage and modify the label_ID/label_name pairs used in your project annotations.
---
### "Import Label Names List"
  + Replaces the current project's label_ID/label_name pairs with a list imported from an external .YAML file.
  + Annotations of the project are not changed.

### "Merge Label Names List"
  + Adds new label names from an external file to your existing label_ID/label_name pairs list without removing current list.
  + Select a .YAML file containing additional label names.
  + Adds new labels with new IDs at the end of the list.
  + "Merge" if you want to keep a default label_ID/label_name pairs list.
  + Annotations of the project are not changed.

### "Reset Label Names List"
  + Clears all custom label_ID/label_name pairs.
  + Annotations of the project are not changed.

### "Change Persian Characters to Label Names"
  + Converts annotations labeled with a default character/label name list for Persian characters
  + You can modify this list for your language:
        chars_per = [1570, 1575, 1576, 1662, 1578, 1579, 1580, 1670, 1581, 1582, 1583,
                    1584, 1585, 1586, 1688, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594,
                    1601, 1602, 1705, 1711, 1604, 1605, 1606, 1608, 1607, 1740, 1569, 1571,
                    1572, 1574, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785,
                    40, 41, 91, 93, 1567, 33, 46, 1548, 58, 1563, 171, 187, 43, 45, 47,
                    215, 247, 60, 61, 62, 1643, 8204, 32,
                    48, 49, 50, 51, 52, 53, 54, 55, 56, 57]

        Char_labels=["Aaa", "Alf", "Beh", "Peh", "Teh", "Seh", "Jim", "Che", "Hej",
        "khe", "Dal", "Zal", "Reh", "Zeh", "Zhe", "Sin", "Shin", "Sad",
        "Zad", "Taa", "Zaa", "Ein", "Ghein", "Feh", "Ghaf", "Kaf", "Gaf",
        "Lam", "Mim", "Nun", "Vav", "Heh", "Yeh", "Hmz", "Ahmz", "Vhmz",
        "Ehmz", "#0", "#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8", "#9",
        "())", "(()", "[]]", "[[]", "؟", "!", ".", "،", ":", "؛", "«»»", "««»",
        "+", "-", "/", "×", "÷", "<>>", "=", "<<>", "MMYZ", "HSPC", "SPC",
        "#0", "#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8", "#9"]

  + Updates the annotation to use the character/label name instead of the character.
  + Makes annotations more readable and descriptive.
  + Improves compatibility with export formats that expect named labels.

#### Important Notes:
  + **Backup your project** before using "Import" or "Reset" functions.


***
---
### AI Assistant Functions

#### Access Path:
  + AI Assist → [Various AI Assistant Options]

#### Description:
  + These functions integrate a deep learning model to assist with annotation tasks, from automatic detection to conflict resolution.
---
### "Load Deep Learning Model for Assistance"
  + Loads a pre-trained deep learning model (YOLO format) to use for AI-assisted annotation.
  + Select a model file when prompted (typically `.pt` or similar format).
  + The model is loaded and set to evaluation mode.
  + Once loaded, you can use other AI functions for assistance.

#### Requirements:
  + Compatible model file (trained for your annotation task).
  + Sufficient system memory for the model.

### "Apply Deep Learning Model to the Current Image"
  + Runs the loaded AI model on the **currently displayed image** to automatically generate annotations.
  + The AI detects objects and creates bounding boxes with suggested labels.
  + You can decide to replace the new annotations to the existing ones or delete the existing annotations.
  + New annotations are added to the current image (you can review and edit them).
  + New annotations are sorted from right to left. You can resort them as you want.

### "Apply Deep Learning Model to All Images with No BBox"
  + Automatically runs the AI model on **all images in the project that have no existing annotations**.
  + Scans the entire project for images without bounding boxes.
  + Applies the AI model to each unannotated image.
  + Adds AI-generated annotations to these images.
  + New annotations are sorted from right to left. You can resort them as you want.

#### Use Case:
  + Quickly bootstrap annotation for a large dataset.
  + Fill in missing annotations for incomplete projects.

### "Check Label Conflict with the Current Image"
  + It is suggested that you Lock all existing annotations before Check Label Conflict.
  + Compares AI model predictions with your existing annotations in the **current image** to identify inconsistencies.
  + Highlights potential conflicts between your manual annotations and AI predictions.
  + Helps identify possible mislabeling or missing annotations.

### "Check Label Conflict with All Images"
  + It is suggested that you Lock all existing annotations before Check Label Conflict.
  + Runs conflict checking on **all images in the project** to ensure annotation consistency.
  + Compares AI predictions with existing annotations.
  + Highlights discrepancies across the entire dataset.

#### Use Case:
  + Quality assurance for large annotation projects.
  + Identifying systematic labeling errors.

#### Important Notes:
  + **Load a model first** before using other AI functions.
  + AI-generated annotations are **suggestions** and are presented unLocked - always review and verify them.
  + Conflict checking helps improve annotation quality but doesn't automatically correct errors.
  + The accuracy of AI assistance depends on the quality and relevance of the loaded model.
  + Consider the AI as an assistant, not a replacement for human verification.
