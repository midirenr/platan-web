from .db_2000 import *
from .docx_pdf_module import *


def start_package_process(serial_number):
    modification_dictionary = {
        '20': 'ISN41508T3',
        '31': 'ISN41508T3-M/ISES1004',
        '30': 'ISN41508T3-M',
        '10': 'ISN41508T4',
        '41': 'ISN41508T3-M-AC/ISES1004',
        '40': 'ISN41508T3-M-AC!',
        '32': 'ISN41508T3-M/ISES0108',
        '33': 'ISN41508T3-M/ISES0114',
        '34': 'ISN41508T3-M/ISES0116',
        '35': 'ISN41508T3-M/ISES1009',
        '42': 'ISN41508T3-M-AC/ISES0108',
        '43': 'ISN41508T3-M-AC/ISES0114',
        '44': 'ISN41508T3-M-AC/ISES0116',
        '45': 'ISN41508T3-M-AC/ISES1009',
    }
    modification = modification_dictionary.get(serial_number[2:4])

    update_date_time_package(engine, serial_number)
    stickers = [print_sticker(serial_number, modification), print_sticker_passport(serial_number)]
    return stickers
