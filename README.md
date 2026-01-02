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
