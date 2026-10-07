from ultralytics import YOLO

model = YOLO("models/ppe.pt")

results = model.predict(
    source="videos/factory.mp4",
    conf=0.15,
    save=True,
    show=True
)

print("Done!")
print("Classes:", model.names)