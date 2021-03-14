from PIL import Image


class PicFormatter(object):
    def __init__(self, img_path):
        self.img_path = img_path
        self.img_obj = Image.open(self.img_path)

    def get_resized_pic(self):
        height_percent = (640 / float(self.img_obj.size[1]))
        width_size = int((float(self.img_obj.size[0]) * float(height_percent)))
        temp_img_final = self.img_obj.resize((width_size, 640), Image.NEAREST)

        return temp_img_final

    def get_image_original(self):
        return self.img_obj
