
def convert_to_blob(pic_name):
    with open(pic_name, 'rb') as trip_pic:
        blob_pic = trip_pic.read()
    return blob_pic


def convert_to_pic(data, filename):
    with open(filename, 'wb') as trip_pic:
        trip_pic.write(data)


def get_display_link(pics):
    links = ['application/temp_files' + p + '.jpg' for p in pics]
    return links