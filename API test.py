import unittest
from models import Product
from tools import request_bill
from dotenv import load_dotenv


class ProductRetrieveTest(unittest.TestCase):
    correct_bill_raw_mock = [
        {
            "itemsQuantityMeasure": 0,
            "name": "ПАКЕТ БИОРАЗЛАГ 8КГ",
            "nds": 1,
            "paymentType": 4,
            "price": 1500,
            "productType": 1,
            "quantity": 2,
            "sum": 3000
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ПАКЕТ 60Х54 АШАН 50М",
            "price": 1200,
            "quantity": 1,
            "sum": 1200,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 11,
            "name": "БАНАНЫ ВЕСОВЫЕ",
            "price": 10949,
            "quantity": 0.892,
            "sum": 9767,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ПИВ.НАП.GARAGE 0,4",
            "price": 6990,
            "quantity": 1,
            "sum": 6990,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ВИНО ИОНОС БЕЛ.0,75Л",
            "price": 58099,
            "quantity": 1,
            "sum": 58099,
            "nds": 1,
            "paymentType": 4,
            "productType": 2
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ПИВО 0,75 С-БУТ BUD",
            "price": 10490,
            "quantity": 1,
            "sum": 10490,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ХОЛОДНЫЙ ЧАЙ TI ЛИМО",
            "price": 4990,
            "quantity": 1,
            "sum": 4990,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "САЙДЕР CHESTERS 0,45",
            "price": 10949,
            "quantity": 1,
            "sum": 10949,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ЙО-ЙО БАНАН 0,24 Л",
            "price": 6499,
            "quantity": 1,
            "sum": 6499,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "НАП FAHRENHEIT ЛИМЛ",
            "price": 7799,
            "quantity": 1,
            "sum": 7799,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ФАРШ ИЗ ГРУДКИ",
            "price": 11990,
            "quantity": 1,
            "sum": 11990,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ГОЛУБИКА ИМПОРТНАЯ ШТ",
            "price": 21999,
            "quantity": 1,
            "sum": 21999,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "З/П ШАМПИНЬОНЫ КОРОЛ 400Г",
            "price": 13999,
            "quantity": 1,
            "sum": 13999,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "БЕКОН С/К НАРЕЗ.200Г",
            "price": 16990,
            "quantity": 1,
            "sum": 16990,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "СОСИСКИ КЛИНСКИЕ МГА 460Г",
            "price": 17990,
            "quantity": 1,
            "sum": 17990,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ВЕТЧИНА Д/ТОСТОВ 120Г НАР",
            "price": 8990,
            "quantity": 1,
            "sum": 8990,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "productCodeNew": {
                "gs1m": {
                    "rawProductCode": "0104660043858806215)fvgd",
                    "productIdType": 6,
                    "gtin": "04660043858806",
                    "sernum": "5)fvgd"
                }
            },
            "labelCodeProcesMode": 0,
            "name": "СЫРОК ГЛАЗ КАРТ 50Г",
            "price": 4590,
            "quantity": 1,
            "sum": 4590,
            "nds": 2,
            "paymentType": 4,
            "productType": 33,
            "checkingProdInformationResult": 0
        },
        {
            "itemsQuantityMeasure": 0,
            "productCodeNew": {
                "gs1m": {
                    "rawProductCode": "0104660043858790215AluMa",
                    "productIdType": 6,
                    "gtin": "04660043858790",
                    "sernum": "5AluMa"
                }
            },
            "labelCodeProcesMode": 0,
            "name": "СЫРОК ГЛ СГУЩ МОЛ50Г",
            "price": 4590,
            "quantity": 1,
            "sum": 4590,
            "nds": 2,
            "paymentType": 4,
            "productType": 33,
            "checkingProdInformationResult": 0
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "КОЛБ.С/К KABANOS CLA",
            "price": 8990,
            "quantity": 1,
            "sum": 8990,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "productCodeNew": {
                "gs1m": {
                    "rawProductCode": "0104810268035265212mU3dknd",
                    "productIdType": 6,
                    "gtin": "04810268035265",
                    "sernum": "2mU3dknd"
                }
            },
            "labelCodeProcesMode": 0,
            "name": "СЫР РОССИЙСК.50%",
            "price": 20949,
            "quantity": 1,
            "sum": 20949,
            "nds": 2,
            "paymentType": 4,
            "productType": 33,
            "checkingProdInformationResult": 0
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "КОЛБ.САЛЯМИ С/К 250Г",
            "price": 33499,
            "quantity": 1,
            "sum": 33499,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 11,
            "name": "КАБАЧКИ КГ ВЕС",
            "price": 13990,
            "quantity": 0.99,
            "sum": 13850,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ФАРШ ГОВЯЖ АНГУС400Г",
            "price": 17990,
            "quantity": 1,
            "sum": 17990,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "CТЕЙК ПИКАНЬЯ ИЗ ГОВ",
            "price": 52399,
            "quantity": 1,
            "sum": 52399,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "КОТЛЕТЫ СЛИВОЧ ПЕТЕЛ",
            "price": 12990,
            "quantity": 1,
            "sum": 12990,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "КОЛБАСКИ К ПИВУ ЛОТОК 400Г",
            "price": 14990,
            "quantity": 1,
            "sum": 14990,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 11,
            "name": "СЫР МОЦАРЕЛЛА ПИЦЦА",
            "price": 101699,
            "quantity": 0.676,
            "sum": 68749,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ЛЕЙЗ ЧИПСЫ СМЕТ ЛУК",
            "price": 11949,
            "quantity": 1,
            "sum": 11949,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 11,
            "name": "КРЫЛЫШКО КУРИН.ОХЛ.1",
            "price": 33199,
            "quantity": 0.834,
            "sum": 27688,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "GM SNICKERS 50.5Г",
            "price": 4899,
            "quantity": 1,
            "sum": 4899,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ХЛ.ТОСТ.В УП.НАР.170Г.",
            "price": 3699,
            "quantity": 1,
            "sum": 3699,
            "nds": 2,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "name": "ПАКЕТ-МАЙКА БЕЛЫЙ",
            "price": 700,
            "quantity": 1,
            "sum": 700,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        }
    ]
    correct_bill_mock_short = [
        Product(
            name="БАНАНЫ ВЕСОВЫЕ",
            price=109.49,
            quantity=0.892,
            sum=97.67,
        ),
        Product(
            name='СЫРОК ГЛАЗ КАРТ 50Г',
            price=45.9,
            quantity=1,
            sum=45.90
        )
    ]
    correct_bill_raw_mock_short = [
        {
            "itemsQuantityMeasure": 11,
            "name": "БАНАНЫ ВЕСОВЫЕ",
            "price": 10949,
            "quantity": 0.892,
            "sum": 9767,
            "nds": 1,
            "paymentType": 4,
            "productType": 1
        },
        {
            "itemsQuantityMeasure": 0,
            "productCodeNew": {
                "gs1m": {
                    "rawProductCode": "0104660043858806215)fvgd",
                    "productIdType": 6,
                    "gtin": "04660043858806",
                    "sernum": "5)fvgd"
                }
            },
            "labelCodeProcesMode": 0,
            "name": "СЫРОК ГЛАЗ КАРТ 50Г",
            "price": 4590,
            "quantity": 1,
            "sum": 4590,
            "nds": 2,
            "paymentType": 4,
            "productType": 33,
            "checkingProdInformationResult": 0
        }
    ]

    def setUp(self) -> None:
        load_dotenv()

    def test_correct_bill(self):
        ans = request_bill("t=20230422T1916&s=5142.62&fn=7281440500036082&i=52785&fp=1311112988&n=1")
        self.assertEqual(ans, self.correct_bill_raw_mock)

    def test_incorrect_format(self):
        self.assertRaises(ValueError, request_bill,"MOCK_DATA")

    def test_parsing(self):
        parsed=[]
        for product in self.correct_bill_raw_mock_short:
            parsed.append(Product.from_dict(product))
        self.assertEqual(parsed, self.correct_bill_mock_short)


if __name__ == '__main__':
    unittest.main()
