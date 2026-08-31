# VOIDFRAME

### Gesture-Controlled Computer Vision Invisibility Interface

VoidFrame is an interactive computer vision application that creates a real-time visual invisibility effect using hand gestures.

The system captures the user's environment as a background reference and uses MediaPipe hand tracking to identify the index fingers of both hands. The left index finger controls the top-left corner of an invisibility region, while the right index finger controls the bottom-right corner.

When the user positions and separates both index fingers, VoidFrame creates a dynamic rectangular field. The content inside the field is replaced with the previously captured background, producing the illusion that the selected portion of the scene has become invisible.

---

## Project Concept

VoidFrame follows a simple interaction model:

```text
CAPTURE BACKGROUND
        |
        v
DETECT BOTH HANDS
        |
        v
LEFT INDEX  ----------------> TOP-LEFT
RIGHT INDEX ----------------> BOTTOM-RIGHT
        |
        v
CALCULATE BOUNDING BOX
        |
        v
REPLACE REGION WITH BACKGROUND
        |
        v
REAL-TIME INVISIBILITY EFFECT
```

The project combines computer vision, gesture interaction, image processing, and an interactive desktop interface into a single application.

---

## Key Features

* Real-time webcam processing
* Two-hand tracking using MediaPipe
* Left-hand index finger as the top-left controller
* Right-hand index finger as the bottom-right controller
* Finger-distance based gesture activation
* Dynamic bounding-box generation
* Background capture and replacement
* Real-time invisibility effect
* Full-screen interactive interface
* Live FPS monitoring
* Gesture and system status indicators
* Reset and background recapture controls
* Dark-themed modern desktop UI

---

## Gesture Interaction

### 1. Capture Background

The application first captures a clean frame of the environment.

This frame becomes the reference background used to create the invisibility effect.

### 2. Activate Gesture

Bring the left and right index fingertips close together.

```text
LEFT INDEX  --->  <---  RIGHT INDEX
                    |
                 ACTIVATE
```

The system recognizes the fingers as touching and arms the VoidFrame field.

### 3. Create the Field

After activation, move the fingers apart.

The application uses the following coordinate system:

```text
LEFT INDEX
     |
     v
  (x1, y1)
      ┌──────────────────────────────┐
      │                              │
      │        INVISIBILITY          │
      │           FIELD              │
      │                              │
      └──────────────────────────────┘
                            ^
                            |
                       (x2, y2)
                    RIGHT INDEX
```

The left index finger defines the **top-left corner**.

The right index finger defines the **bottom-right corner**.

### 4. Invisibility Effect

The rectangular region is replaced with the corresponding region from the captured background.

This makes the person or object inside the selected region appear to disappear.

---

## Technology Stack

| Technology    | Purpose                                        |
| ------------- | ---------------------------------------------- |
| Python        | Core application                               |
| OpenCV        | Webcam capture and image processing            |
| MediaPipe     | Real-time hand landmark detection              |
| NumPy         | Coordinate calculations and image manipulation |
| CustomTkinter | Modern desktop interface                       |
| Pillow        | Image conversion and UI rendering              |

---

## Project Structure

```text
Voidframe/
│
├── app.py
├── requirements.txt
├── README.md
├── hand_landmarker.task
│
├── assets/
│   └── ...
│
└── .gitignore
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/hashanfr/Voidframe.git
```

Move into the project directory:

```bash
cd Voidframe
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

---

## Requirements

The project requires:

```text
opencv-python
mediapipe
numpy
customtkinter
Pillow
```

A webcam is required for real-time hand tracking.

---

## System Workflow

VoidFrame processes the camera feed continuously.

```text
Webcam
  |
  v
Frame Acquisition
  |
  v
Hand Detection
  |
  v
Index Finger Extraction
  |
  +--------------------+
  |                    |
  v                    v
Left Index          Right Index
Top-Left            Bottom-Right
  |                    |
  +---------+----------+
            |
            v
     Distance Calculation
            |
            v
      Gesture Validation
            |
            v
      Bounding Box
            |
            v
 Background Region Replacement
            |
            v
     Invisibility Effect
```

---

## Coordinate-Based Field Generation

VoidFrame intentionally assigns different responsibilities to each hand.

### Left Hand

The left index fingertip determines:

```text
x1 = left_index.x
y1 = left_index.y
```

This becomes the top-left corner.

### Right Hand

The right index fingertip determines:

```text
x2 = right_index.x
y2 = right_index.y
```

This becomes the bottom-right corner.

The resulting field is:

```text
width  = x2 - x1
height = y2 - y1
```

The field is activated only when the coordinates satisfy the required orientation and minimum size.

---

## Background Replacement

The captured background is stored before the gesture interface is drawn.

When the VoidFrame becomes active, only the selected rectangular region is replaced:

```python
frame[y1:y2, x1:x2] = background[y1:y2, x1:x2]
```

This preserves the rest of the live camera feed while creating the localized invisibility effect.

---

## User Interface

The application is designed as a full-screen computer vision interface.

The interface provides:

* Live camera feed
* System status
* Camera status
* Hand detection status
* Background capture status
* Gesture status
* Finger distance
* Current operating mode
* FPS counter
* Background capture control
* Field reset control
* Application exit control

---

## Application Modes

VoidFrame operates through several states:

```text
STANDBY
   |
   v
BACKGROUND CAPTURED
   |
   v
GESTURE ARMED
   |
   v
POSITIONING
   |
   v
VOID FIELD
   |
   v
INVISIBILITY ACTIVE
```

If the fingers are positioned incorrectly or the field is too small, the system returns to a positioning state instead of creating an invalid field.

---

## Controls

| Control            | Function                               |
| ------------------ | -------------------------------------- |
| Capture Background | Saves the current camera frame         |
| Reset Field        | Disables the active invisibility field |
| ESC                | Exits the application                  |
| Left Index         | Controls top-left corner               |
| Right Index        | Controls bottom-right corner           |

---

## Use Cases

VoidFrame is primarily an experimental computer vision project, but the interaction concept can be extended to:

* Gesture-controlled interfaces
* Interactive art installations
* Augmented reality experiments
* Computer vision demonstrations
* Human-computer interaction research
* Educational computer vision projects
* Creative camera effects
* Touchless UI systems

---

## Future Improvements

Potential future versions could introduce:

* Multiple simultaneous invisibility fields
* Circular and custom-shaped masks
* Face-aware invisibility
* Body segmentation
* Object-aware masking
* Gesture-based field locking
* Smooth bounding-box animation
* Motion stabilization
* Background restoration
* Voice commands
* Recording and screenshot functionality
* GPU acceleration
* Web-based interface
* AR-style visual effects

---

## Important Technical Note

VoidFrame does not physically remove the person from the camera image.

The invisibility effect is produced through background substitution. The application captures the environment before the user enters the scene and later replaces the selected region of the live frame with the corresponding pixels from that captured background.

The result is a visual illusion created through real-time image processing.

---

## Development

VoidFrame was developed as an exploration of:

* Computer Vision
* Hand Landmark Detection
* Gesture Recognition
* Image Processing
* Human-Computer Interaction
* Real-Time Video Processing

The project demonstrates how simple hand landmarks and coordinate geometry can be transformed into an interactive visual computing experience.

---

## License

This project is intended for educational, experimental, and research purposes.

You may modify and extend the project for your own learning and experimentation.
