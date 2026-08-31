import cv2
import mediapipe as mp
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk
import time


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_INDEX = 0

# Distance at which both index fingers are considered touching
TOUCH_THRESHOLD = 55

# Minimum width and height for the invisibility field
BOX_MIN_WIDTH = 60
BOX_MIN_HEIGHT = 60

# Camera resolution
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720


# ============================================================
# VOIDFRAME APPLICATION
# ============================================================

class VoidFrameApp:

    def __init__(self):

        # ======================================================
        # UI SETUP
        # ======================================================

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()

        self.root.title("VOIDFRAME")

        # Fullscreen application
        self.root.attributes("-fullscreen", True)

        # ESC exits the application
        self.root.bind("<Escape>", lambda event: self.exit_app())


        # ======================================================
        # CAMERA
        # ======================================================

        self.cap = cv2.VideoCapture(CAMERA_INDEX)

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            CAMERA_WIDTH
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            CAMERA_HEIGHT
        )


        # ======================================================
        # MEDIAPIPE HAND DETECTION
        # ======================================================

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.mp_draw = mp.solutions.drawing_utils


        # ======================================================
        # SYSTEM VARIABLES
        # ======================================================

        # Saved empty background
        self.background = None

        # Current clean camera frame
        self.current_frame = None

        # Left hand index fingertip
        self.left_index = None

        # Right hand index fingertip
        self.right_index = None

        # Gesture state
        self.gesture_armed = False

        # Invisibility state
        self.invisibility_active = False

        # Current frame dimensions
        self.frame_width = CAMERA_WIDTH
        self.frame_height = CAMERA_HEIGHT

        # FPS variables
        self.previous_time = time.time()
        self.fps = 0


        # ======================================================
        # BUILD UI
        # ======================================================

        self.build_ui()

        # Start camera loop
        self.update_camera()


    # ==========================================================
    # BUILD USER INTERFACE
    # ==========================================================

    def build_ui(self):

        self.root.grid_rowconfigure(
            1,
            weight=1
        )

        self.root.grid_columnconfigure(
            1,
            weight=1
        )


        # ======================================================
        # HEADER
        # ======================================================

        header = ctk.CTkFrame(
            self.root,
            height=80,
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


        title = ctk.CTkLabel(
            header,
            text="VOIDFRAME",
            font=("Arial", 30, "bold")
        )

        title.grid(
            row=0,
            column=0,
            padx=30,
            pady=20
        )


        subtitle = ctk.CTkLabel(
            header,
            text="GESTURE-CONTROLLED INVISIBILITY SYSTEM",
            font=("Arial", 14)
        )

        subtitle.grid(
            row=0,
            column=1
        )


        self.status_label = ctk.CTkLabel(
            header,
            text="● SYSTEM ONLINE",
            font=("Arial", 14, "bold")
        )

        self.status_label.grid(
            row=0,
            column=2,
            padx=30
        )


        # ======================================================
        # LEFT SIDEBAR
        # ======================================================

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

        sidebar.grid_propagate(False)


        sidebar_title = ctk.CTkLabel(
            sidebar,
            text="SYSTEM STATUS",
            font=("Arial", 20, "bold")
        )

        sidebar_title.pack(
            pady=(25, 30)
        )


        self.camera_status = ctk.CTkLabel(
            sidebar,
            text="● CAMERA ONLINE",
            font=("Arial", 14)
        )

        self.camera_status.pack(
            anchor="w",
            padx=25,
            pady=10
        )


        self.hand_status = ctk.CTkLabel(
            sidebar,
            text="○ WAITING FOR HANDS",
            font=("Arial", 14)
        )

        self.hand_status.pack(
            anchor="w",
            padx=25,
            pady=10
        )


        self.background_status = ctk.CTkLabel(
            sidebar,
            text="○ BACKGROUND NOT CAPTURED",
            font=("Arial", 14)
        )

        self.background_status.pack(
            anchor="w",
            padx=25,
            pady=10
        )


        self.gesture_status = ctk.CTkLabel(
            sidebar,
            text="○ WAITING FOR GESTURE",
            font=("Arial", 14)
        )

        self.gesture_status.pack(
            anchor="w",
            padx=25,
            pady=10
        )


        divider = ctk.CTkFrame(
            sidebar,
            height=2
        )

        divider.pack(
            fill="x",
            padx=20,
            pady=25
        )


        instruction_title = ctk.CTkLabel(
            sidebar,
            text="GESTURE CONTROL",
            font=("Arial", 18, "bold")
        )

        instruction_title.pack(
            pady=10
        )


        instructions = ctk.CTkLabel(
            sidebar,
            text=(
                "1. Capture empty background\n\n"
                "2. Touch LEFT and RIGHT\n"
                "   index fingertips\n\n"
                "3. Move LEFT index to\n"
                "   TOP-LEFT corner\n\n"
                "4. Move RIGHT index to\n"
                "   BOTTOM-RIGHT corner\n\n"
                "5. VOID FIELD activates"
            ),
            justify="left",
            font=("Arial", 13)
        )

        instructions.pack(
            padx=20,
            pady=10
        )


        # ======================================================
        # CAMERA CONTAINER
        # ======================================================

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


        camera_title = ctk.CTkLabel(
            camera_container,
            text="LIVE REALITY FEED",
            font=("Arial", 18, "bold")
        )

        camera_title.grid(
            row=0,
            column=0,
            pady=15
        )


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


        # ======================================================
        # RIGHT PANEL
        # ======================================================

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

        info_panel.grid_propagate(False)


        info_title = ctk.CTkLabel(
            info_panel,
            text="GESTURE ENGINE",
            font=("Arial", 18, "bold")
        )

        info_title.pack(
            pady=(30, 25)
        )


        self.distance_label = ctk.CTkLabel(
            info_panel,
            text="DISTANCE\n-- px",
            font=("Arial", 16, "bold"),
            justify="center"
        )

        self.distance_label.pack(
            pady=20
        )


        self.mode_label = ctk.CTkLabel(
            info_panel,
            text="MODE\nSTANDBY",
            font=("Arial", 16, "bold"),
            justify="center"
        )

        self.mode_label.pack(
            pady=20
        )


        self.fps_label = ctk.CTkLabel(
            info_panel,
            text="FPS\n--",
            font=("Arial", 14),
            justify="center"
        )

        self.fps_label.pack(
            pady=20
        )


        # ======================================================
        # BOTTOM CONTROLS
        # ======================================================

        controls = ctk.CTkFrame(
            self.root,
            height=100,
            corner_radius=0
        )

        controls.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew"
        )


        capture_button = ctk.CTkButton(
            controls,
            text="📸 CAPTURE BACKGROUND",
            width=230,
            height=50,
            font=("Arial", 15, "bold"),
            command=self.capture_background
        )

        capture_button.pack(
            side="left",
            padx=30,
            pady=25
        )


        reset_button = ctk.CTkButton(
            controls,
            text="↻ RESET FIELD",
            width=170,
            height=50,
            font=("Arial", 15, "bold"),
            command=self.reset_system
        )

        reset_button.pack(
            side="left",
            padx=20
        )


        exit_button = ctk.CTkButton(
            controls,
            text="✕ EXIT",
            width=150,
            height=50,
            font=("Arial", 15, "bold"),
            command=self.exit_app
        )

        exit_button.pack(
            side="right",
            padx=30
        )


    # ==========================================================
    # CAPTURE BACKGROUND
    # ==========================================================

    def capture_background(self):

        if self.current_frame is not None:

            # Save clean frame as background
            self.background = self.current_frame.copy()

            self.background_status.configure(
                text="● BACKGROUND CAPTURED"
            )

            self.status_label.configure(
                text="● BACKGROUND LOCKED"
            )


    # ==========================================================
    # RESET SYSTEM
    # ==========================================================

    def reset_system(self):

        self.gesture_armed = False

        self.invisibility_active = False

        self.gesture_status.configure(
            text="○ WAITING FOR GESTURE"
        )

        self.mode_label.configure(
            text="MODE\nSTANDBY"
        )

        self.status_label.configure(
            text="● SYSTEM ONLINE"
        )


    # ==========================================================
    # HAND DETECTION
    # ==========================================================

    def process_hands(self, frame):

        # Reset positions every frame
        self.left_index = None
        self.right_index = None


        # Convert frame for MediaPipe
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        results = self.hands.process(
            rgb_frame
        )


        # ======================================================
        # HANDS DETECTED
        # ======================================================

        if (
            results.multi_hand_landmarks
            and results.multi_handedness
        ):

            detected_hands = 0


            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):

                # Get LEFT / RIGHT label
                hand_label = (
                    handedness.classification[0].label
                )


                # Get index fingertip landmark
                index_tip = (
                    hand_landmarks.landmark[
                        self.mp_hands.HandLandmark.INDEX_FINGER_TIP
                    ]
                )


                x = int(
                    index_tip.x * self.frame_width
                )

                y = int(
                    index_tip.y * self.frame_height
                )


                # --------------------------------------------------
                # ROLE-BASED ASSIGNMENT
                # --------------------------------------------------
                #
                # LEFT HAND INDEX
                #      ALWAYS TOP-LEFT CONTROLLER
                #
                # RIGHT HAND INDEX
                #      ALWAYS BOTTOM-RIGHT CONTROLLER
                # --------------------------------------------------

                if hand_label == "Left":

                    self.left_index = (x, y)

                    detected_hands += 1


                elif hand_label == "Right":

                    self.right_index = (x, y)

                    detected_hands += 1


                # Draw MediaPipe hand skeleton
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )


            # Update hand status
            if (
                self.left_index is not None
                and self.right_index is not None
            ):

                self.hand_status.configure(
                    text="● LEFT + RIGHT DETECTED"
                )

            else:

                self.hand_status.configure(
                    text="● ONE HAND DETECTED"
                )


        else:

            self.hand_status.configure(
                text="○ WAITING FOR HANDS"
            )


    # ==========================================================
    # DRAW FINGERTIP MARKERS
    # ==========================================================

    def draw_finger_markers(self, frame):

        # LEFT INDEX = TOP-LEFT CONTROLLER
        if self.left_index is not None:

            lx, ly = self.left_index

            cv2.circle(
                frame,
                (lx, ly),
                12,
                (255, 100, 0),
                -1
            )

            cv2.putText(
                frame,
                "LEFT INDEX | TOP-LEFT",
                (lx + 15, ly - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 100, 0),
                2
            )


        # RIGHT INDEX = BOTTOM-RIGHT CONTROLLER
        if self.right_index is not None:

            rx, ry = self.right_index

            cv2.circle(
                frame,
                (rx, ry),
                12,
                (0, 255, 255),
                -1
            )

            cv2.putText(
                frame,
                "RIGHT INDEX | BOTTOM-RIGHT",
                (rx - 280, ry + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2
            )


    # ==========================================================
    # GESTURE PROCESSING
    # ==========================================================

    def process_gesture(self, frame):

        # Need both hands
        if (
            self.left_index is None
            or self.right_index is None
        ):

            return frame


        # Get fingertip positions
        lx, ly = self.left_index

        rx, ry = self.right_index


        # ======================================================
        # DISTANCE BETWEEN INDEX FINGERS
        # ======================================================

        left_point = np.array(
            [lx, ly]
        )

        right_point = np.array(
            [rx, ry]
        )


        distance = np.linalg.norm(
            left_point - right_point
        )


        self.distance_label.configure(
            text=f"DISTANCE\n{int(distance)} px"
        )


        # ======================================================
        # STATE 1:
        # INDEX FINGERS TOUCH
        #
        # This ARMS the invisibility field.
        # ======================================================

        if distance < TOUCH_THRESHOLD:

            self.gesture_armed = True

            self.invisibility_active = False

            self.gesture_status.configure(
                text="⚡ FINGERS TOUCHING"
            )

            self.mode_label.configure(
                text="MODE\nARMED"
            )

            self.status_label.configure(
                text="⚡ VOID FIELD ARMED"
            )


            # Visual connection
            cv2.line(
                frame,
                (lx, ly),
                (rx, ry),
                (255, 255, 255),
                3
            )


            return frame


        # ======================================================
        # STATE 2:
        # FIELD ARMED
        # ======================================================

        if self.gesture_armed:


            # --------------------------------------------------
            # YOUR EXACT APPROACH
            #
            # LEFT INDEX
            #      = TOP-LEFT CORNER
            #
            # RIGHT INDEX
            #      = BOTTOM-RIGHT CORNER
            # --------------------------------------------------

            x1 = lx
            y1 = ly

            x2 = rx
            y2 = ry


            # ==================================================
            # ORIENTATION VALIDATION
            #
            # LEFT INDEX must actually be:
            #
            # LEFT OF right index
            # AND
            # ABOVE right index
            # ==================================================

            valid_orientation = (
                lx < rx
                and ly < ry
            )


            if not valid_orientation:

                self.invisibility_active = False

                self.gesture_status.configure(
                    text="⚠ POSITION LEFT ↖ / RIGHT ↘"
                )

                self.mode_label.configure(
                    text="MODE\nPOSITIONING"
                )

                self.status_label.configure(
                    text="○ INVALID FIELD ORIENTATION"
                )


                return frame


            # ==================================================
            # CALCULATE BOX SIZE
            # ==================================================

            box_width = x2 - x1

            box_height = y2 - y1


            valid_size = (
                box_width >= BOX_MIN_WIDTH
                and box_height >= BOX_MIN_HEIGHT
            )


            if not valid_size:

                self.invisibility_active = False

                self.gesture_status.configure(
                    text="○ EXPAND FIELD"
                )

                self.mode_label.configure(
                    text="MODE\nEXPANDING"
                )

                return frame


            # ==================================================
            # STATE 3:
            # VOID FIELD ACTIVE
            # ==================================================

            if self.background is None:

                self.gesture_status.configure(
                    text="⚠ CAPTURE BACKGROUND FIRST"
                )

                self.mode_label.configure(
                    text="MODE\nNO BACKGROUND"
                )

                return frame


            self.invisibility_active = True


            self.gesture_status.configure(
                text="🫥 INVISIBILITY ACTIVE"
            )

            self.mode_label.configure(
                text="MODE\nVOID FIELD"
            )

            self.status_label.configure(
                text="🫥 REALITY FIELD ACTIVE"
            )


            # ==================================================
            # BACKGROUND REPLACEMENT
            #
            # Replace ONLY the area inside:
            #
            # LEFT INDEX      → TOP-LEFT
            # RIGHT INDEX     → BOTTOM-RIGHT
            # ==================================================

            frame[
                y1:y2,
                x1:x2
            ] = self.background[
                y1:y2,
                x1:x2
            ]


            # ==================================================
            # DRAW FIELD BORDER
            # ==================================================

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                3
            )


            cv2.putText(
                frame,
                "VOID FIELD ACTIVE",
                (x1, max(35, y1 - 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )


        return frame


    # ==========================================================
    # FPS CALCULATION
    # ==========================================================

    def update_fps(self):

        current_time = time.time()

        elapsed = (
            current_time - self.previous_time
        )


        if elapsed > 0:

            self.fps = 1 / elapsed


        self.previous_time = current_time


        self.fps_label.configure(
            text=f"FPS\n{int(self.fps)}"
        )


    # ==========================================================
    # CAMERA LOOP
    # ==========================================================

    def update_camera(self):

        success, frame = self.cap.read()


        if not success:

            self.status_label.configure(
                text="✕ CAMERA ERROR"
            )

            self.root.after(
                100,
                self.update_camera
            )

            return


        # Mirror camera
        frame = cv2.flip(
            frame,
            1
        )


        # Update actual dimensions
        self.frame_height, self.frame_width = (
            frame.shape[:2]
        )


        # Save CLEAN frame before drawings
        self.current_frame = frame.copy()


        # ======================================================
        # PROCESS HANDS
        # ======================================================

        self.process_hands(
            frame
        )


        # ======================================================
        # PROCESS GESTURE
        # ======================================================

        frame = self.process_gesture(
            frame
        )


        # Draw fingertip indicators after invisibility effect
        self.draw_finger_markers(
            frame
        )


        # Update FPS
        self.update_fps()


        # ======================================================
        # CONVERT FOR UI
        # ======================================================

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        image = Image.fromarray(
            rgb_frame
        )


        # Get available display area
        display_width = max(
            self.video_label.winfo_width(),
            640
        )

        display_height = max(
            self.video_label.winfo_height(),
            480
        )


        # Keep aspect ratio
        image.thumbnail(
            (
                display_width,
                display_height
            )
        )


        photo = ImageTk.PhotoImage(
            image=image
        )


        self.video_label.configure(
            image=photo
        )


        # Prevent garbage collection
        self.video_label.image = photo


        # Next frame
        self.root.after(
            10,
            self.update_camera
        )


    # ==========================================================
    # EXIT APPLICATION
    # ==========================================================

    def exit_app(self):

        if self.cap.isOpened():

            self.cap.release()


        self.hands.close()

        self.root.destroy()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app = VoidFrameApp()

    app.root.mainloop()