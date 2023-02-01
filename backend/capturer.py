from datetime import datetime
import cv2


class Capturer:
    def __init__(self):
        self.capturers: dict[int, cv2.VideoCapture] = {}

    def refresh_devices(self, device_ids: list[int]):
        # initialize capturers
        try:
            for device_id in device_ids:
                self.capturers.setdefault(device_id, cv2.VideoCapture(device_id))
        except:
            pass

        if not self.capturers:
            return

        # release and remove unused capturers
        devices = list(self.capturers.items())
        for device_id, cap in devices:
            if device_id in device_ids:
                continue
            cap.release()
            self.capturers.pop(device_id)


    def get_image(self, device_id: int):
        if not device_id in self.capturers:
            return None

        cap = self.capturers[device_id]
        if not cap.isOpened():
            return None

        ret, frame = cap.read()
        if not ret:
            return None

        frame = self._write_text(image=frame, value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            return None

        return jpeg.tobytes()

    def _write_text(
        self,
        image: cv2.Mat,
        value='',
        font=cv2.FONT_HERSHEY_SIMPLEX,
        scale=2.0,
        thickness=2
    ):
        # if not value:
        #     return image
        (textWidth, textHeight), _ = cv2.getTextSize(value, font, scale, thickness)
        imgHeight, imgWidth, _ = image.shape
        x = (imgWidth - textWidth) // 2
        y = imgHeight - textHeight // 2
        shadow = cv2.putText(image, value, (x, y), font, scale, (0,0,0), thickness, cv2.LINE_AA)
        return cv2.putText(shadow, value, (x-2, y), font, scale, (255,255,255), thickness, cv2.LINE_AA)

