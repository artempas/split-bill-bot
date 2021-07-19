from pyzbar import pyzbar #pyzbar
import cv2 #opencv-python
import datetime

start=datetime.datetime.now()
def draw_barcode(decoded, image):
    # n_points = len(decoded.polygon)
    # for i in range(n_points):
    #     image = cv2.line(image, decoded.polygon[i], decoded.polygon[(i+1) % n_points], color=(0, 255, 0), thickness=5)
    # раскомментируйте выше и закомментируйте ниже, если хотите нарисовать многоугольник, а не прямоугольник
    image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top),
                            (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
                            color=(0, 255, 0),
                            thickness=5)
    return image


def decode(image):
    # decodes all barcodes from an image
    decoded_objects = pyzbar.decode(image)
    for obj in decoded_objects:
        # draw the barcode
        print(f"Обнаружен штрих-код:\n{obj}")
        image = draw_barcode(obj, image)
        # print barcode type & data
        print("Тип:", obj.type)
        print("Данные:", obj.data.decode('utf-8'))
        print()
    return image


if __name__=="__main__":
    imgc=cv2.imread("C:/Users/artem/Downloads/Telegram Desktop/photo_2021-07-19_16-30-39.jpg")
    imgc=decode(imgc)
    cv2.imshow('img',imgc)
    print(datetime.datetime.now()-start)
    cv2.waitKey(0)
