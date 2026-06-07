from ultralytics import YOLO
import cv2
import os


def detect_objects(image_path, confidence_threshold=0.8):
    model = YOLO("yolov8n.pt")

    results = model.predict(
        source=image_path,
        conf=confidence_threshold
    )

    image = cv2.imread(image_path)

    for r in results:
        boxes = r.boxes

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            text = f"{label}: {conf:.2f}"

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(
                image,
                text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

    os.makedirs("outputs", exist_ok=True)

    output_path = "outputs/object_detection_output.jpg"
    cv2.imwrite(output_path, image)

    print(f"Detection complete. Saved to {output_path}")