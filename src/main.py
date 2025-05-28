from camera import get_camera_feed
from gui import display_feed

def main():
    cap = get_camera_feed()
    display_feed(cap)

if __name__ == "__main__":
    main()
