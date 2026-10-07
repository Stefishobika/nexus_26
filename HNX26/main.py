from ultralytics import YOLO
import cv2
import numpy as np
import os

# =========================
# MODELS
# =========================

person_model = YOLO("models/yolo11n.pt")
ppe_model = YOLO("models/ppe.pt")

# =========================
# VIDEO
# =========================

video_path = "videos/factory.mp4"

cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

os.makedirs("output", exist_ok=True)

output_path = "output/factory_safety1.mp4"

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

out = cv2.VideoWriter(
    output_path,
    fourcc,
    fps,
    (width, height)
)

# =========================
# MACHINE DANGER ZONE
# =========================

danger_zone = np.array([
    (700, 300),
    (1500, 300),
    (1500, 1000),
    (700, 1000)
])

# =========================
# TRACKING
# =========================

person_inside_time = {}

THRESHOLD = 2.0

# =========================
# MAIN LOOP
# =========================

frame_number = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame_number += 1

    current_time = frame_number / fps

    # =====================================
    # PERSON DETECTION + TRACKING
    # =====================================

    results = person_model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        classes=[0],
        verbose=False
    )

    # =====================================
    # PPE DETECTION
    # =====================================

    ppe_results = ppe_model.predict(
        frame,
        conf=0.15,
        verbose=False
    )

    # =====================================
    # DRAW PPE EXACTLY LIKE test_ppe
    # =====================================

    if len(ppe_results) > 0:

        # Ultralytics automatically draws:
        # NO-Hardhat
        # NO-Gloves
        # Hardhat
        # Gloves
        # etc.
        frame = ppe_results[0].plot()

    # =====================================
    # DRAW MACHINE DANGER ZONE
    # =====================================

    cv2.polylines(
        frame,
        [danger_zone],
        True,
        (0, 0, 255),
        3
    )

    cv2.putText(
        frame,
        "MACHINE DANGER ZONE",
        (700, 280),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )

    # =====================================
    # PERSON TRACKING
    # =====================================

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy()

        for box, track_id in zip(boxes, track_ids):

            x1, y1, x2, y2 = map(int, box)

            track_id = int(track_id)

            # =================================
            # PERSON'S FEET POSITION
            # =================================

            center_x = int((x1 + x2) / 2)
            center_y = int(y2)

            # =================================
            # CHECK DANGER ZONE
            # =================================

            inside = cv2.pointPolygonTest(
                danger_zone,
                (center_x, center_y),
                False
            )

            if inside >= 0:

                # Start timer
                if track_id not in person_inside_time:
                    person_inside_time[track_id] = current_time

                duration = current_time - person_inside_time[track_id]

                if duration >= THRESHOLD:

                    status = "UNSAFE PROXIMITY"

                    cv2.putText(
                        frame,
                        status,
                        (x1, y1 - 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"ID {track_id} - {duration:.1f}s",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 0, 255),
                        2
                    )

                else:

                    cv2.putText(
                        frame,
                        "ENTERING DANGER ZONE",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 165, 255),
                        2
                    )

            else:

                if track_id in person_inside_time:
                    del person_inside_time[track_id]

                cv2.putText(
                    frame,
                    f"ID {track_id} SAFE",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

            # =================================
            # PERSON BOX
            # =================================

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )

            cv2.putText(
                frame,
                f"Person ID: {track_id}",
                (x1, y2 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

    # =====================================
    # DISPLAY
    # =====================================

    cv2.imshow(
        "HNX26 - Factory Safety Monitoring",
        frame
    )

    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# =========================
# CLEANUP
# =========================

cap.release()
out.release()

cv2.destroyAllWindows()

print()
print("===================================")
print("Factory Safety Analysis Completed")
print("===================================")
print("Output:", output_path)