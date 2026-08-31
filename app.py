import os
import time
import urllib.request

import cv2
import numpy as np
import mediapipe as mp
import customtkinter as ctk

from PIL import Image, ImageTk

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# VOIDFRAME
# Gesture-Controlled Reality Mask
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_INDEX = 0

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

TOUCH_THRESHOLD = 55

BOX_MIN_WIDTH = 60
BOX_MIN_HEIGHT = 60

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/"
    "hand_landmarker.task"
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "hand_landmarker.task"
)


# ============================================================
# DOWNLOAD MEDIAPIPE HAND MODEL
# ============================================================

def ensure_hand_model():

    if os.path.exists(MODEL_PATH):

        print("MediaPipe hand model found.")

        return

    print("MediaPipe hand model not found.")
    print("Downloading hand_landmarker.task...")

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    try:

        urllib.request.urlretrieve(
            MODEL_URL,
            MODEL_PATH
        )

        print(
            "Hand model downloaded successfully."
        )

    except Exception as error:

        print(
            "Failed to download MediaPipe hand model."
        )

        print(error)

        raise


# ============================================================
# VOIDFRAME APPLICATION
# ============================================================

class VoidFrameApp:

    def __init__(self):

        # ====================================================
        # USER INTERFACE
        # ====================================================

        ctk.set_appearance_mode(
            "dark"
        )

        ctk.set_default_color_theme(
            "blue"
        )

        self.root = ctk.CTk()

        self.root.title(
            "VOIDFRAME"
        )

        # Fullscreen
        self.root.attributes(
            "-fullscreen",
            True
        )

        # ESC exits
        self.root.bind(
            "<Escape>",
            lambda event: self.exit_app()
        )


        # ====================================================
        # CAMERA
        # ====================================================

        self.cap = cv2.VideoCapture(
            CAMERA_INDEX,
            cv2.CAP_DSHOW
        )

        if not self.cap.isOpened():

            print(
                "ERROR: Unable to open camera."
            )

            self.root.destroy()

            raise RuntimeError(
                "Camera could not be opened."
            )


        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            CAMERA_WIDTH
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            CAMERA_HEIGHT
        )


        # ====================================================
        # MEDIAPIPE HAND LANDMARKER
        # ====================================================

        ensure_hand_model()

        base_options = python.BaseOptions(
            model_asset_path=MODEL_PATH
        )

        options = vision.HandLandmarkerOptions(

            base_options=base_options,

            running_mode=(
                vision.RunningMode.VIDEO
            ),

            num_hands=2,

            min_hand_detection_confidence=0.6,

            min_hand_presence_confidence=0.6,

            min_tracking_confidence=0.6
        )

        self.hands = (
            vision.HandLandmarker
            .create_from_options(
                options
            )
        )


        # ====================================================
        # SYSTEM VARIABLES
        # ====================================================

        self.background = None

        self.current_frame = None

        # Visual LEFT hand
        # Controls TOP-LEFT
        self.left_index = None

        # Visual RIGHT hand
        # Controls BOTTOM-RIGHT
        self.right_index = None

        self.gesture_armed = False

        self.invisibility_active = False

        self.frame_width = CAMERA_WIDTH

        self.frame_height = CAMERA_HEIGHT

        self.video_timestamp = 0

        self.previous_time = time.time()

        self.fps = 0


        # ====================================================
        # BUILD INTERFACE
        # ====================================================

        self.build_ui()


        # ====================================================
        # START CAMERA LOOP
        # ====================================================

        self.update_camera()


    # ========================================================
    # BUILD USER INTERFACE
    # ========================================================

    def build_ui(self):

        # ----------------------------------------------------
        # GRID CONFIGURATION
        # ----------------------------------------------------

        self.root.grid_rowconfigure(
            1,
            weight=1
        )

        self.root.grid_columnconfigure(
            1,
            weight=1
        )


        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(

            self.root,

            height=75,

            corner_radius=0
        )

        header.grid(

            row=0,

            column=0,

            columnspan=3,

            sticky="ew"
        )

        header.grid_columnconfigure(
            1,
            weight=1
        )


        # TITLE

        title = ctk.CTkLabel(

            header,

            text="VOIDFRAME",

            font=(
                "Arial",
                30,
                "bold"
            )
        )

        title.grid(

            row=0,

            column=0,

            padx=30
        )


        # SUBTITLE

        subtitle = ctk.CTkLabel(

            header,

            text=(
                "GESTURE-CONTROLLED "
                "REALITY MASK"
            ),

            font=(
                "Arial",
                14
            )
        )

        subtitle.grid(

            row=0,

            column=1
        )


        # SYSTEM STATUS

        self.status_label = ctk.CTkLabel(

            header,

            text="SYSTEM ONLINE",

            font=(
                "Arial",
                14,
                "bold"
            )
        )

        self.status_label.grid(

            row=0,

            column=2,

            padx=30
        )


        # ====================================================
        # LEFT SIDEBAR
        # ====================================================

        sidebar = ctk.CTkFrame(

            self.root,

            width=280,

            corner_radius=15
        )

        sidebar.grid(

            row=1,

            column=0,

            sticky="ns",

            padx=20,

            pady=20
        )

        sidebar.grid_propagate(
            False
        )


        # SIDEBAR TITLE

        ctk.CTkLabel(

            sidebar,

            text="SYSTEM STATUS",

            font=(
                "Arial",
                20,
                "bold"
            )
        ).pack(

            pady=(
                25,
                30
            )
        )


        # CAMERA STATUS

        self.camera_status = ctk.CTkLabel(

            sidebar,

            text="CAMERA ONLINE",

            font=(
                "Arial",
                14
            )
        )

        self.camera_status.pack(

            anchor="w",

            padx=25,

            pady=10
        )


        # HAND STATUS

        self.hand_status = ctk.CTkLabel(

            sidebar,

            text="WAITING FOR HANDS",

            font=(
                "Arial",
                14
            )
        )

        self.hand_status.pack(

            anchor="w",

            padx=25,

            pady=10
        )


        # BACKGROUND STATUS

        self.background_status = ctk.CTkLabel(

            sidebar,

            text="BACKGROUND NOT CAPTURED",

            font=(
                "Arial",
                14
            )
        )

        self.background_status.pack(

            anchor="w",

            padx=25,

            pady=10
        )


        # GESTURE STATUS

        self.gesture_status = ctk.CTkLabel(

            sidebar,

            text="WAITING FOR GESTURE",

            font=(
                "Arial",
                14
            )
        )

        self.gesture_status.pack(

            anchor="w",

            padx=25,

            pady=10
        )


        # DIVIDER

        ctk.CTkFrame(

            sidebar,

            height=2

        ).pack(

            fill="x",

            padx=20,

            pady=25
        )


        # CONTROL TITLE

        ctk.CTkLabel(

            sidebar,

            text="CONTROL SCHEME",

            font=(
                "Arial",
                18,
                "bold"
            )

        ).pack(

            pady=10
        )


        instructions = (

            "CAPTURE\n"
            "Capture an empty background.\n\n"

            "ARM\n"
            "Touch both index fingers.\n\n"

            "LEFT HAND\n"
            "Index finger = TOP-LEFT\n\n"

            "RIGHT HAND\n"
            "Index finger = BOTTOM-RIGHT\n\n"

            "VOID\n"
            "Move fingers apart."
        )


        ctk.CTkLabel(

            sidebar,

            text=instructions,

            justify="left",

            font=(
                "Arial",
                13
            )

        ).pack(

            padx=20,

            pady=10
        )


        # ====================================================
        # CAMERA CONTAINER
        # ====================================================

        camera_container = ctk.CTkFrame(

            self.root,

            corner_radius=15
        )

        camera_container.grid(

            row=1,

            column=1,

            sticky="nsew",

            padx=10,

            pady=20
        )

        camera_container.grid_rowconfigure(

            1,

            weight=1
        )

        camera_container.grid_columnconfigure(

            0,

            weight=1
        )


        # CAMERA TITLE

        ctk.CTkLabel(

            camera_container,

            text="LIVE REALITY FEED",

            font=(
                "Arial",
                18,
                "bold"
            )

        ).grid(

            row=0,

            column=0,

            pady=15
        )


        # VIDEO DISPLAY

        self.video_label = ctk.CTkLabel(

            camera_container,

            text=""
        )

        self.video_label.grid(

            row=1,

            column=0,

            sticky="nsew",

            padx=15,

            pady=15
        )


        # ====================================================
        # RIGHT INFORMATION PANEL
        # ====================================================

        info_panel = ctk.CTkFrame(

            self.root,

            width=240,

            corner_radius=15
        )

        info_panel.grid(

            row=1,

            column=2,

            sticky="ns",

            padx=20,

            pady=20
        )

        info_panel.grid_propagate(
            False
        )


        # TITLE

        ctk.CTkLabel(

            info_panel,

            text="GESTURE ENGINE",

            font=(
                "Arial",
                18,
                "bold"
            )

        ).pack(

            pady=(
                30,
                25
            )
        )


        # DISTANCE

        self.distance_label = ctk.CTkLabel(

            info_panel,

            text="DISTANCE\n-- px",

            font=(
                "Arial",
                16,
                "bold"
            ),

            justify="center"
        )

        self.distance_label.pack(
            pady=20
        )


        # MODE

        self.mode_label = ctk.CTkLabel(

            info_panel,

            text="MODE\nSTANDBY",

            font=(
                "Arial",
                16,
                "bold"
            ),

            justify="center"
        )

        self.mode_label.pack(
            pady=20
        )


        # FIELD SIZE

        self.box_label = ctk.CTkLabel(

            info_panel,

            text="FIELD\n-- × --",

            font=(
                "Arial",
                14
            ),

            justify="center"
        )

        self.box_label.pack(
            pady=20
        )


        # FPS

        self.fps_label = ctk.CTkLabel(

            info_panel,

            text="FPS\n--",

            font=(
                "Arial",
                14
            ),

            justify="center"
        )

        self.fps_label.pack(
            pady=20
        )


        # ====================================================
        # BOTTOM CONTROLS
        # ====================================================

        controls = ctk.CTkFrame(

            self.root,

            height=90,

            corner_radius=0
        )

        controls.grid(

            row=2,

            column=0,

            columnspan=3,

            sticky="ew"
        )


        # CAPTURE BUTTON

        ctk.CTkButton(

            controls,

            text="CAPTURE BACKGROUND",

            width=230,

            height=50,

            font=(
                "Arial",
                15,
                "bold"
            ),

            command=self.capture_background

        ).pack(

            side="left",

            padx=30,

            pady=20
        )


        # RESET BUTTON

        ctk.CTkButton(

            controls,

            text="RESET FIELD",

            width=170,

            height=50,

            font=(
                "Arial",
                15,
                "bold"
            ),

            command=self.reset_system

        ).pack(

            side="left",

            padx=20
        )


        # EXIT BUTTON

        ctk.CTkButton(

            controls,

            text="EXIT",

            width=150,

            height=50,

            font=(
                "Arial",
                15,
                "bold"
            ),

            command=self.exit_app

        ).pack(

            side="right",

            padx=30
        )


    # ========================================================
    # CAPTURE BACKGROUND
    # ========================================================

    def capture_background(self):

        if self.current_frame is None:

            return


        self.background = (
            self.current_frame.copy()
        )


        self.background_status.configure(

            text="BACKGROUND CAPTURED"
        )


        self.status_label.configure(

            text="BACKGROUND LOCKED"
        )


    # ========================================================
    # RESET SYSTEM
    # ========================================================

    def reset_system(self):

        self.gesture_armed = False

        self.invisibility_active = False


        self.gesture_status.configure(

            text="WAITING FOR GESTURE"
        )


        self.mode_label.configure(

            text="MODE\nSTANDBY"
        )


        self.distance_label.configure(

            text="DISTANCE\n-- px"
        )


        self.box_label.configure(

            text="FIELD\n-- × --"
        )


        self.status_label.configure(

            text="SYSTEM ONLINE"
        )


    # ========================================================
    # HAND DETECTION
    # ========================================================

    def process_hands(self, frame):

        # Reset positions
        self.left_index = None

        self.right_index = None


        # ----------------------------------------------------
        # BGR -> RGB
        # ----------------------------------------------------

        rgb = cv2.cvtColor(

            frame,

            cv2.COLOR_BGR2RGB
        )


        # ----------------------------------------------------
        # MediaPipe Image
        # ----------------------------------------------------

        rgb_image = mp.Image(

            image_format=(
                mp.ImageFormat.SRGB
            ),

            data=rgb
        )


        # ----------------------------------------------------
        # VIDEO TIMESTAMP
        # ----------------------------------------------------

        self.video_timestamp += 1


        # ----------------------------------------------------
        # DETECT HANDS
        # ----------------------------------------------------

        result = (
            self.hands.detect_for_video(

                rgb_image,

                self.video_timestamp
            )
        )


        # ----------------------------------------------------
        # NO HANDS
        # ----------------------------------------------------

        if not result.hand_landmarks:

            self.hand_status.configure(

                text="WAITING FOR HANDS"
            )

            return


        # ====================================================
        # PROCESS EACH HAND
        # ====================================================

        for landmarks, handedness in zip(

            result.hand_landmarks,

            result.handedness
        ):

            if not landmarks:

                continue


            # ------------------------------------------------
            # MediaPipe handedness
            # ------------------------------------------------

            label = (
                handedness[0].category_name
            )


            # ------------------------------------------------
            # INDEX FINGERTIP
            #
            # MediaPipe landmark 8
            # ------------------------------------------------

            index_tip = landmarks[8]


            x = int(

                index_tip.x *
                self.frame_width
            )

            y = int(

                index_tip.y *
                self.frame_height
            )


            # ------------------------------------------------
            # CLAMP COORDINATES
            # ------------------------------------------------

            x = max(

                0,

                min(

                    self.frame_width - 1,

                    x
                )
            )


            y = max(

                0,

                min(

                    self.frame_height - 1,

                    y
                )
            )


            # =================================================
            # IMPORTANT
            #
            # The camera image is mirrored:
            #
            # cv2.flip(frame, 1)
            #
            # Therefore MediaPipe's handedness is interpreted
            # relative to the original camera image.
            #
            # We intentionally swap the assignment:
            #
            # MediaPipe RIGHT -> VISUAL LEFT
            # MediaPipe LEFT  -> VISUAL RIGHT
            #
            # Result:
            #
            # VISUAL LEFT HAND  -> TOP LEFT
            # VISUAL RIGHT HAND -> BOTTOM RIGHT
            # =================================================

            if label == "Right":

                self.left_index = (

                    x,

                    y
                )


            elif label == "Left":

                self.right_index = (

                    x,

                    y
                )


        # ====================================================
        # UPDATE HAND STATUS
        # ====================================================

        if (

            self.left_index is not None

            and

            self.right_index is not None

        ):

            self.hand_status.configure(

                text="LEFT + RIGHT DETECTED"
            )


        elif (

            self.left_index is not None

            or

            self.right_index is not None

        ):

            self.hand_status.configure(

                text="ONE HAND DETECTED"
            )


        else:

            self.hand_status.configure(

                text="WAITING FOR HANDS"
            )


    # ========================================================
    # DRAW FINGERTIP CONTROLLERS
    # ========================================================

    def draw_finger_markers(self, frame):

        # ----------------------------------------------------
        # VISUAL LEFT HAND
        # TOP-LEFT CONTROLLER
        # ----------------------------------------------------

        if self.left_index is not None:

            x, y = self.left_index


            cv2.circle(

                frame,

                (x, y),

                12,

                (255, 100, 0),

                -1
            )


            cv2.putText(

                frame,

                "LEFT INDEX | TOP-LEFT",

                (
                    x + 15,

                    max(
                        20,
                        y - 15
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (255, 100, 0),

                2
            )


        # ----------------------------------------------------
        # VISUAL RIGHT HAND
        # BOTTOM-RIGHT CONTROLLER
        # ----------------------------------------------------

        if self.right_index is not None:

            x, y = self.right_index


            cv2.circle(

                frame,

                (x, y),

                12,

                (0, 255, 255),

                -1
            )


            cv2.putText(

                frame,

                "RIGHT INDEX | BOTTOM-RIGHT",

                (
                    max(
                        10,
                        x - 280
                    ),

                    min(
                        self.frame_height - 10,
                        y + 30
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (0, 255, 255),

                2
            )


    # ========================================================
    # GESTURE PROCESSING
    # ========================================================

    def process_gesture(self, frame):

        # ====================================================
        # BOTH HANDS REQUIRED
        # ====================================================

        if (

            self.left_index is None

            or

            self.right_index is None

        ):

            self.distance_label.configure(

                text="DISTANCE\n-- px"
            )

            return frame


        # ====================================================
        # GET FINGERTIP POSITIONS
        #
        # LEFT  = TOP LEFT
        # RIGHT = BOTTOM RIGHT
        # ====================================================

        lx, ly = self.left_index

        rx, ry = self.right_index


        # ====================================================
        # CALCULATE DISTANCE
        # ====================================================

        left_point = np.array(

            [lx, ly],

            dtype=np.float32
        )

        right_point = np.array(

            [rx, ry],

            dtype=np.float32
        )


        distance = np.linalg.norm(

            left_point -

            right_point
        )


        self.distance_label.configure(

            text=(
                f"DISTANCE\n"
                f"{int(distance)} px"
            )
        )


        # ====================================================
        # STATE 1
        #
        # INDEX FINGERS TOUCH
        #
        # This arms the system.
        # ====================================================

        if distance <= TOUCH_THRESHOLD:

            self.gesture_armed = True

            self.invisibility_active = False


            self.gesture_status.configure(

                text="FINGERS CONNECTED"
            )


            self.mode_label.configure(

                text="MODE\nARMED"
            )


            self.status_label.configure(

                text="VOID FIELD ARMED"
            )


            # Draw connection
            cv2.line(

                frame,

                (lx, ly),

                (rx, ry),

                (255, 255, 255),

                3
            )


            return frame


        # ====================================================
        # NOT ARMED
        # ====================================================

        if not self.gesture_armed:

            return frame


        # ====================================================
        # BOUNDING BOX
        #
        # LEFT INDEX
        #      |
        #      V
        #   (x1,y1)
        #      +----------------+
        #      |                |
        #      |   VOID FIELD   |
        #      |                |
        #      +----------------+
        #                       ^
        #                       |
        #                  (x2,y2)
        #                  RIGHT INDEX
        # ====================================================

        x1 = lx

        y1 = ly

        x2 = rx

        y2 = ry


        # ====================================================
        # ORIENTATION VALIDATION
        #
        # LEFT INDEX MUST BE:
        #
        #   LEFT OF right index
        #
        # AND
        #
        #   ABOVE right index
        # ====================================================

        valid_orientation = (

            lx < rx

            and

            ly < ry
        )


        if not valid_orientation:

            self.invisibility_active = False


            self.mode_label.configure(

                text="MODE\nPOSITIONING"
            )


            self.gesture_status.configure(

                text="MOVE LEFT ↖ AND RIGHT ↘"
            )


            self.box_label.configure(

                text="FIELD\nINVALID"
            )


            return frame


        # ====================================================
        # BOX SIZE
        # ====================================================

        box_width = x2 - x1

        box_height = y2 - y1


        self.box_label.configure(

            text=(
                f"FIELD\n"
                f"{box_width} × {box_height}"
            )
        )


        # ====================================================
        # MINIMUM SIZE
        # ====================================================

        if (

            box_width < BOX_MIN_WIDTH

            or

            box_height < BOX_MIN_HEIGHT

        ):

            self.invisibility_active = False


            self.mode_label.configure(

                text="MODE\nEXPANDING"
            )


            self.gesture_status.configure(

                text="EXPAND FIELD"
            )


            return frame


        # ====================================================
        # BACKGROUND REQUIRED
        # ====================================================

        if self.background is None:

            self.invisibility_active = False


            self.mode_label.configure(

                text="MODE\nNO BACKGROUND"
            )


            self.gesture_status.configure(

                text="CAPTURE BACKGROUND FIRST"
            )


            return frame


        # ====================================================
        # VOID FIELD ACTIVE
        # ====================================================

        self.invisibility_active = True


        self.mode_label.configure(

            text="MODE\nVOID FIELD"
        )


        self.gesture_status.configure(

            text="INVISIBILITY ACTIVE"
        )


        self.status_label.configure(

            text="REALITY FIELD ACTIVE"
        )


        # ====================================================
        # BACKGROUND REPLACEMENT
        #
        # Replace only the area between:
        #
        # LEFT INDEX  -> TOP LEFT
        # RIGHT INDEX -> BOTTOM RIGHT
        # ====================================================

        frame[
            y1:y2,
            x1:x2
        ] = self.background[
            y1:y2,
            x1:x2
        ]


        # ====================================================
        # DRAW FIELD BORDER
        # ====================================================

        cv2.rectangle(

            frame,

            (x1, y1),

            (x2, y2),

            (0, 255, 0),

            3
        )


        # ====================================================
        # FIELD LABEL
        # ====================================================

        cv2.putText(

            frame,

            "VOID FIELD",

            (

                x1,

                max(
                    30,
                    y1 - 12
                )
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 255, 0),

            2
        )


        return frame


    # ========================================================
    # FPS
    # ========================================================

    def update_fps(self):

        current_time = time.time()


        elapsed = (

            current_time -

            self.previous_time
        )


        if elapsed > 0:

            self.fps = 1 / elapsed


        self.previous_time = current_time


        self.fps_label.configure(

            text=(
                f"FPS\n"
                f"{int(self.fps)}"
            )
        )


    # ========================================================
    # CAMERA LOOP
    # ========================================================

    def update_camera(self):

        success, frame = self.cap.read()


        # ====================================================
        # CAMERA ERROR
        # ====================================================

        if not success:

            self.camera_status.configure(

                text="CAMERA ERROR"
            )


            self.status_label.configure(

                text="CAMERA ERROR"
            )


            self.root.after(

                100,

                self.update_camera
            )

            return


        # ====================================================
        # MIRROR WEBCAM
        # ====================================================

        frame = cv2.flip(

            frame,

            1
        )


        # ====================================================
        # UPDATE FRAME DIMENSIONS
        # ====================================================

        self.frame_height, self.frame_width = (

            frame.shape[:2]
        )


        # ====================================================
        # SAVE CLEAN FRAME
        #
        # This MUST happen before:
        #
        # MediaPipe processing
        # Gesture processing
        # Drawings
        # ====================================================

        self.current_frame = (

            frame.copy()
        )


        # ====================================================
        # HAND DETECTION
        # ====================================================

        self.process_hands(

            frame
        )


        # ====================================================
        # GESTURE PROCESSING
        # ====================================================

        frame = self.process_gesture(

            frame
        )


        # ====================================================
        # DRAW CONTROLLERS
        # ====================================================

        self.draw_finger_markers(

            frame
        )


        # ====================================================
        # FPS
        # ====================================================

        self.update_fps()


        # ====================================================
        # CONVERT FRAME FOR TKINTER
        # ====================================================

        rgb_frame = cv2.cvtColor(

            frame,

            cv2.COLOR_BGR2RGB
        )


        image = Image.fromarray(

            rgb_frame
        )


        # ====================================================
        # DISPLAY SIZE
        # ====================================================

        display_width = max(

            self.video_label.winfo_width(),

            640
        )


        display_height = max(

            self.video_label.winfo_height(),

            480
        )


        # ====================================================
        # KEEP ASPECT RATIO
        # ====================================================

        image.thumbnail(

            (

                display_width,

                display_height
            )
        )


        # ====================================================
        # DISPLAY IMAGE
        # ====================================================

        photo = ImageTk.PhotoImage(

            image=image
        )


        self.video_label.configure(

            image=photo
        )


        # Prevent garbage collection

        self.video_label.image = photo


        # ====================================================
        # NEXT FRAME
        # ====================================================

        self.root.after(

            10,

            self.update_camera
        )


    # ========================================================
    # EXIT APPLICATION
    # ========================================================

    def exit_app(self):

        print(
            "Shutting down VOIDFRAME..."
        )


        # ----------------------------------------------------
        # Stop camera
        # ----------------------------------------------------

        if self.cap.isOpened():

            self.cap.release()


        # ----------------------------------------------------
        # Close MediaPipe
        # ----------------------------------------------------

        if self.hands:

            self.hands.close()


        # ----------------------------------------------------
        # Destroy UI
        # ----------------------------------------------------

        self.root.destroy()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        app = VoidFrameApp()

        app.root.mainloop()

    except KeyboardInterrupt:

        print(
            "Application interrupted."
        )

    except Exception as error:

        print(
            "\nVOIDFRAME ERROR:"
        )

        print(error)

        raise