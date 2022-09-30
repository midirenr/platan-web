from .db_2000 import *


def stand_visual_inspection_valid(serial_number, author):
    add_board_serial_number_valid(engine, serial_number, author)


def stand_visual_inspection_defect(serial_number, author):
    add_board_serial_number_defect(engine, serial_number, author)
