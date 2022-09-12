from pyzbar import pyzbar  # pyzbar
from PIL import Image
import datetime

start = datetime.datetime.now()

def data_from_qr(image):
    # decodes all barcodes from an image
    img = Image.open(image)
    data = pyzbar.decode(img)
    print(data)
    return data


def check_for_format(qr):
    if type(qr) is str:
        if '&' in qr:
            if len(qr.split('&')) == 6:
                for i in qr.split('&'):
                    if '=' in i:
                        if i.split('=')[0] in ('t', 's', 'fn', 'i', 'fp', 'n'):
                            continue
                        else:
                            print("wrong key found")
                            return False
                    else:
                        print('found part without "="')
                        return False
                return True
            else:
                print("wrong amount of args in qr")
                return False
        else:
            print("there's no & in qr")
            return False
    else:
        raise TypeError(f"Expected str got {type(qr)}")



