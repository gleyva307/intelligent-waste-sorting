import cv2

def get_camera_feed():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("No se pudo acceder a la cámara.")
    return cap
