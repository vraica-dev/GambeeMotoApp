from typing import BinaryIO, Union

from PIL import Image
from werkzeug.datastructures import FileStorage

try:
    _RESAMPLE_NEAREST = Image.Resampling.NEAREST
except AttributeError:  # Pillow < 9.1 has no Resampling enum
    _RESAMPLE_NEAREST = Image.NEAREST  # type: ignore[attr-defined]


class PicFormatter:
    def __init__(self, img_path: Union[FileStorage, BinaryIO]) -> None:
        self.img_path = img_path
        self.img_obj = Image.open(self.img_path)

    def get_resized_pic(self) -> Image.Image:
        height_percent = 640 / float(self.img_obj.size[1])
        width_size = int(float(self.img_obj.size[0]) * float(height_percent))
        temp_img_final = self.img_obj.resize((width_size, 640), _RESAMPLE_NEAREST)

        return temp_img_final

    def get_image_original(self) -> Image.Image:
        return self.img_obj
