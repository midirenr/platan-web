import os
from collections import deque
import qrcode
from fpdf import FPDF
import webbrowser
from zipfile import ZipFile


def generate_serial_numbers(device_type, modification_type, detail_type, place_of_production, count, current_time):
    device_dictionary = {
        'Сервисный маршрутизатор': 'RS',
        'Граничный маршрутизатор': 'RB',
        'Коммутатор доступа': 'SA',
        'Коммутатор агрегации': 'SG',
        'Коммутатор ЦОД': 'SC',
    }

    modification_dictionary = {
        'ISN41508T4': '10',
        'ISN41508T3': '20',
        'ISN41508T3-M': '30',
        'ISN41508T3-M/ISES1004': '31',
        'ISN41508T3-M/ISES0108': '32',
        'ISN41508T3-M_ISES00114': '33',
        'ISN41508T3-M/ISES0116': '34',
        'ISN41508T3-M/ISES1009': '35',
        'ISN41508T3-M-AC': '40',
        'ISN41508T3-M-AC/ISES1004': '41',
        'ISN41508T3-M-AC/ISES0108': '42',
        'ISN41508T3-M-AC/ISES00114': '43',
        'ISN41508T3-M-AC/ISES0116': '44',
        'ISN41508T3-M-AC/ISES1009': '45',
        'ISN50600-MA': '50',
        'ISN50600-M10A': '51',
        'ISN50600-M11A': '52',
        'ISN50600-M12A': '53',
        'ISN50600-M13A': '54',
        'ISN50600-M14A': '55',
        'ISN50600-M15A': '56',
        'ISN50600-M16A': '57',
        'ISN80600-MA': '10',
        'ISN80600-M01A': '11',
        'ISN80600-M02A': '12',
        'ISN80600-M03A': '13',
        'ISN80600-M04A': '14',
        'ISN80600-M05A': '15',
        'ISN80600-M06A': '16',
        'ISN80600-M07A': '17',
        'ISN80600-M08A': '18',
        'ISN80600-M09A': '19',
        'ISN80600-M10A': '20',
        'ISN80600-MF': '50',
        'ISN80600-M01F': '51',
        'ISN80600-M02F': '52',
        'ISN80600-M03F': '53',
        'ISN80600-M04F': '54',
        'ISN80600-M05F': '55',
        'ISN80600-M06F': '56',
        'ISN80600-M07F': '57',
        'ISN80600-M08F': '58',
        'ISN80600-M09F': '59',
        'ISN80600-M10F': '60',
        'ISN42124X5': '01',
        'ISN42124T5C4 ': '02',
        'ISN42124T5P5': '03',
        'ISN42148T5P7': '04',
        'ISN42148X2': '05',
        'ISN42148T5': '06',
        'ISN43224X7': '01',
        'ISN43248X7': '02',
        'ISN64318ХB': '01',
        'ISN64348ХB': '02',
    }

    detail_dictionary = {
        'Готовое изделие в сборе': '10',
        'Плата основная': '20',
        'Плата переходная индикации и управления': '11',
        'Райзер PCI-E': '12',
        'Плата сигнализации отказов': '13',
        'Плата управления питанием': '14',
        'Плата переходная': '15',
        'Вентилятор': '40',
        'Кабель консольный': '50',
        'Корпус': '60',
        'Упаковка': '70',
        'Блок питания': '80',
        'Стандартные изделия, прочие изделия, комплект монтажных частей': '90',
        'Комплект крепежа для установки на стену': '91',
        'Комплект для монтажа в стойку': '92',
    }

    place_dictionary = {
        'Исток': '01',
        'EMS Expert': '02',
        'ТМИ': '03',
        'Альт Мастер': '04',
        'ТСИ': '05',
        'Резанит': '06',
    }

    type_of_device = device_dictionary.get(str(device_type))
    modification = modification_dictionary.get(str(modification_type))
    detail = detail_dictionary.get(str(detail_type))
    place = place_dictionary.get(str(place_of_production))

    import datetime
    year_now = datetime.date.today().year
    if year_now == 2022:
        _year = 1
    else:
        _year = year_now - 2022 + 1
    _y = str(hex(_year)).split('x')[-1].capitalize()

    _month = datetime.date.today().month
    _m = str(hex(_month)).split('x')[-1].capitalize()

    with open(f'SerialNumbers/{device_type}/{modification_type}/{detail_type}/log/how_much', 'r') as f1:
        how_much = list(deque(f1, 1))

    last = int(how_much[0])

    with open(f'SerialNumbers/{device_type}/{modification_type}/{detail_type}/log/how_much', 'w') as f2:
        new_last = last + count
        f2.write(str(new_last))

    delta = last + count

    # current_time = str(datetime.datetime.now())[:-7].replace(' ', '_').replace(':', '-')

    serial_number = type_of_device + modification + detail + place + _y + _m
    # folder = f'qrcode-{detail_type}-{current_time}'
    # os.mkdir(f'QRcode/{device_type}/{modification_type}/{detail_type}/{folder}')

    serial_number_list = []

    number = ''

    for i in range(last + 1, delta + 1):
        if i >= 1 and i < 10:
            number = '000' + str(i)
        elif i >= 10 and i < 100:
            number = '00' + str(i)
        elif i >= 100 and i < 1000:
            number = '0' + str(i)
        elif i >= 1000 and i < 10000:
            number = '' + str(i)
        _serial_number = serial_number + number
        # filename = f'QRcode/{device_type}/{modification_type}/{detail_type}/{folder}/{_serial_number}.png'
        # img = qrcode.make(_serial_number)
        # img.save(filename)
        serial_number_list.append(_serial_number)

    fullname = f'serial_number_for_{modification_type}/{detail_type}({current_time})'

    if os.path.exists(f'SerialNumbers/{device_type}/{modification_type}/{detail_type}/serial_number_for_{modification_type}'):
        pass
    else:
        os.mkdir(f'SerialNumbers/{device_type}/{modification_type}/{detail_type}/serial_number_for_{modification_type}')

    with open(f'SerialNumbers/{device_type}/{modification_type}/{detail_type}/{fullname}.txt', 'w') as file:
        for i in serial_number_list:
            print(i, file=file)
        # browser = webbrowser.get('Firefox')
        # browser.open_new_tab(f'{file}')

    """
    pdf = FPDF()
    dirname = f'QRcode/{device_type}/{modification_type}/{detail_type}/{folder}/'
    list_png = os.listdir(dirname)
    print(list_png)
    imagelist = []

    for i in list_png:
        pdf_l = f'QRcode/{device_type}/{modification_type}/{detail_type}/{folder}/{i}'
        imagelist.append(pdf_l)

    list_png.sort()
    imagelist.sort()

    pdf.add_page()
    for image in imagelist:
        image_split = image.split('/')[-1] + '\n\n\n'
        # pdf.set_margins(1, 1, 1)
        pdf.image(image, None, None, 10, 10)
        pdf.set_font("Arial", size=5)
        pdf.write(1, txt=image_split)

    pdf.output(f'QRcode/{device_type}/{modification_type}/{detail_type}/{folder}/{folder}.pdf', 'F')
    """
    # browser.open_new_tab(f'QRcode/{device_type}/{modification_type}/{detail_type}/{folder}/{folder}.pdf')
