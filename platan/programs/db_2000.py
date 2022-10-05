#!/usr/bin/python3.8
from this import d
from webbrowser import get
import yaml
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, String, Integer, Text, Boolean, UniqueConstraint, ForeignKey
# from scanwidget_router import *

# читаем yaml
yaml_file = 'devices.yaml'
with open(f'yamls/{yaml_file}') as f:
    params = yaml.safe_load(f)
db_host, db_port, db_username, db_password, db_name = list(params['db'].values())
# serial_num_pcb = input('Отсканируйте qr снизу платы: ')
# serial_num_board = input('Отсканируйте qr сверху платы: ')
# serial_num_case = input('Отсканируйте qr Корпуса: ')
# serial_num_package = input('Отсканируйте qr Упаковки: ')
# serial_num_bp = input('Отсканируйте qr Блока Питания: ')
# serial_num_pki = input('Отсканируйте qr ПКИ: ')
# serial_num_router = input('Отсканируйте qr Маршрутизатора: ')

engine = create_engine(f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

Session = sessionmaker(bind=engine)
db_session = Session()
Base = declarative_base()


class Devices(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True, unique=True)
    serial_num_pcb_id = Column(Integer, ForeignKey('serial_num_pcb.id'), unique=True)
    serial_num_board_id = Column(Integer, ForeignKey('serial_num_board.id'), unique=True)
    diag = Column(Boolean, default = False)
    serial_num_case_id = Column(Integer, ForeignKey('serial_num_case.id'), unique=True)
    date_time_pci = Column(String(), nullable=False, default='No')
    serial_num_package_id = Column(Integer, ForeignKey('serial_num_package.id'), unique=True)
    serial_num_bp_id = Column(Integer, ForeignKey('serial_num_bp.id'), unique=True)
    serial_num_pki_id = Column(Integer, ForeignKey('serial_num_pki.id'), unique=True)
    serial_num_router_id = Column(Integer, ForeignKey('serial_num_router.id'), unique=True)
    ethaddr_id = Column(Integer, ForeignKey('macs.id'), unique=True)
    eth1addr_id = Column(Integer, ForeignKey('macs.id'), unique=True)
    eth2addr_id = Column(Integer, ForeignKey('macs.id'), unique=True)
    date_time_package = Column(String(), nullable=False, default='No')
    serial_num_pcb = relationship('SerialNumPCB', foreign_keys=[serial_num_pcb_id])
    serial_num_board = relationship('SerialNumBoard', foreign_keys=[serial_num_board_id])
    serial_num_case = relationship('SerialNumCase', foreign_keys=[serial_num_case_id])
    serial_num_package = relationship('SerialNumPackage', foreign_keys=[serial_num_package_id])
    serial_num_bp = relationship('SerialNumBP', foreign_keys=[serial_num_bp_id])
    serial_num_pki = relationship('SerialNumPKI', foreign_keys=[serial_num_pki_id])
    serial_num_router = relationship('SerialNumRouter', foreign_keys=[serial_num_router_id])
    ethaddr = relationship('Macs', foreign_keys=[ethaddr_id])
    eth1addr = relationship('Macs', foreign_keys=[eth1addr_id])
    eth2addr = relationship('Macs', foreign_keys=[eth2addr_id])


date_time = str(datetime.now())[:-7].replace(':', '-')


class SerialNumPCB(Base):
    __tablename__ = 'serial_num_pcb'
    id = Column(Integer, primary_key=True, unique=True)
    serial_num_pcb = Column(String, unique=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    device = relationship('Devices', foreign_keys=[device_id])


class SerialNumBoard(Base):
    __tablename__ = 'serial_num_board'
    id = Column(Integer, primary_key=True, unique=True)
    serial_num_board = Column(String, unique=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    device = relationship('Devices', foreign_keys=[device_id])


class SerialNumCase(Base):
    __tablename__ = 'serial_num_case'
    id = Column(Integer, primary_key=True, unique=True)
    serial_num_case = Column(String, unique=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    device = relationship('Devices', foreign_keys=[device_id])


class SerialNumPackage(Base):
    __tablename__ = 'serial_num_package'
    id = Column(Integer, primary_key=True, unique=True)
    serial_num_package = Column(String, unique=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    device = relationship('Devices', foreign_keys=[device_id])


class SerialNumBP(Base):
    __tablename__ = 'serial_num_bp'
    id = Column(Integer, primary_key=True, unique=True)
    serial_num_bp = Column(String, unique=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    device = relationship('Devices', foreign_keys=[device_id])


class SerialNumPKI(Base):
    __tablename__ = 'serial_num_pki'
    id = Column(Integer, primary_key=True, unique=True)
    serial_num_pki = Column(String, unique=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    device = relationship('Devices', foreign_keys=[device_id])


class SerialNumRouter(Base):
    __tablename__ = 'serial_num_router'
    id = Column(Integer, primary_key=True, unique=True)
    serial_num_router = Column(String, unique=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    device = relationship('Devices', foreign_keys=[device_id])


class Macs(Base):
    __tablename__ = 'macs'
    id = Column(Integer, primary_key=True, unique=True)
    mac = Column(String, unique=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    # reserved = Column(Boolean, default=False)
    device = relationship('Devices', foreign_keys=[device_id])


'''
    class ScanSNB1(QtWidgets.QWidget, Ui_Form_R1):
        def __init__(self, parent=None):
            super(ScanSNB1, self).__init__(parent)
            self.setupUi(self)

'''

# Создание бд
# Base.metadata.create_all(engine)


def check_sn_b(engine, serial_num_board):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    try:
        sn_board_id = db_session.query(SerialNumBoard).filter(SerialNumBoard.serial_num_board == serial_num_board).one().id
        return False
    except:
        return True


def check_sn_r(engine, serial_num_router):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    try:
        sn_router_id = db_session.query(SerialNumRouter).filter(SerialNumRouter.serial_num_router == serial_num_router).one().id
        return False
    except:
        return True


def create_device_and_write_serial_num_pcb_and_reserve_macs(engine, serial_num_board):
    """
    Функция предназначена для запуска в отдельном треде. Создает сессию подключения к БД, создает новое устройство в БД,
    и создает ссылки, соотносящие первые три свободнных мака с созданным устройством
    :return: возвращает список МАС адресов
    """
    Session = sessionmaker(bind=engine)
    db_session = Session()
    # Создаем новое устройство
    device = Devices()
    #serial_num_1 = SerialNumPCB()
    serial_num_2 = SerialNumBoard()
    db_session.add(device)
    #db_session.add(serial_num_1)
    db_session.add(serial_num_2)
    db_session.commit()
    # Рефрешим чтобы сгенерированный базой id был доступен в рамках сессии
    db_session.refresh(device)
    #db_session.refresh(serial_num_1)
    db_session.refresh(serial_num_2)
    # create pcb sn
    #serial_num_1.serial_num_pcb = serial_num_pcb
    #serial_num_1.device_id = device.id
    #db_session.commit()
    #db_session.refresh(serial_num_1)
    #serial_num_pcb_id = serial_num_1.id
    # create board sn
    serial_num_2.serial_num_board = serial_num_board
    serial_num_2.device_id = device.id
    db_session.commit()
    db_session.refresh(serial_num_2)
    serial_num_board_id = serial_num_2.id
    # Отсканированные sn записываем в свои таблицы присваиваем им id 
    #device.serial_num_pcb_id = serial_num_pcb_id
    device.serial_num_board_id = serial_num_board_id
    db_session.commit()
    # Читаем три первых записи со свободными МАСами, блокируя их после чтения, затем прописываем ссылки
    # на маки в таблице devices
    snmac_list = [] # первый в списке будет серийный номер
    #snmac_list.append(serial_num_1.serial_num_pcb)
    snmac_list.append(serial_num_2.serial_num_board)
    ethaddr_id_list = []
    macs = db_session.query(Macs).with_for_update().filter(Macs.device_id.is_(None)).limit(3).all()
    for item in macs:
        snmac_list.append(item.mac)
        item.device_id = device.id
        ethaddr_id_list.append(item.id)
    device.ethaddr_id = ethaddr_id_list[0]
    device.eth1addr_id = ethaddr_id_list[1]
    device.eth2addr_id = ethaddr_id_list[2]
    db_session.commit()
    db_session.close()
    return snmac_list


# create_device_and_write_serial_num_pcb_and_reserve_macs(engine, 'RS1020011A0118')


def update_diag(engine, serial_num_board):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    sn_board_id = db_session.query(SerialNumBoard).filter(SerialNumBoard.serial_num_board == serial_num_board).one().id
    db_session.query(Devices).filter(Devices.serial_num_board_id == sn_board_id).update({"diag": True})
    db_session.commit()
    db_session.close()


def check_diag(engine, serial_num_board):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    try:
        sn_board_id = db_session.query(SerialNumBoard).filter(SerialNumBoard.serial_num_board == serial_num_board).one().id
        diag_status = db_session.query(Devices).filter(Devices.serial_num_board_id == sn_board_id).one().diag
        print(diag_status)
        return diag_status
    except:
        scansnB1 = ScanSNB1()
        scansnB1.eror_win.setText(f'Плата с серийным номером {serial_num_board} нет в базе\nОтнесите её на стенд диагностики')
        scansnB1.eror_win.exec_()


def write_serial_num_router(engine, serial_num_board, serial_num_router):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    serial_num_3 = SerialNumRouter()
    sn_board_id = db_session.query(SerialNumBoard).filter(SerialNumBoard.serial_num_board == serial_num_board).one().id
    device_id = db_session.query(Devices).filter(Devices.serial_num_board_id == sn_board_id).one().id
    db_session.add(serial_num_3)    
    serial_num_3.serial_num_router = serial_num_router
    serial_num_3.device_id = device_id   
    db_session.commit()
    db_session.refresh(serial_num_3)
    serial_num_router_id = serial_num_3.id
    db_session.query(Devices).filter(Devices.serial_num_board_id == sn_board_id).update({"serial_num_router_id": serial_num_router_id})
    db_session.commit()
    db_session.close()

# write_serial_num_router(engine, 'RS102001180001', 'RS101001190001')
    

def delete_string(engine, serial_num_board):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    sn_board_id = db_session.query(SerialNumBoard).filter(SerialNumBoard.serial_num_board == serial_num_board).one().id
    device_id = db_session.query(Devices).filter(Devices.serial_num_board_id == sn_board_id).one().id
    db_session.query(Devices).filter(Devices.id == device_id).update({"serial_num_router_id": None})
    db_session.query(Devices).filter(Devices.id == device_id).update({"serial_num_board_id": None})
    db_session.query(Devices).filter(Devices.id == device_id).update({"ethaddr_id": None})
    db_session.query(Devices).filter(Devices.id == device_id).update({"eth1addr_id": None})
    db_session.query(Devices).filter(Devices.id == device_id).update({"eth2addr_id": None})
    db_session.query(Macs).filter(Macs.device_id == device_id).update({"device_id": None})
    db_session.query(SerialNumBoard).filter(SerialNumBoard.device_id == device_id).delete()
    db_session.query(SerialNumRouter).filter(SerialNumRouter.device_id == device_id).delete()
    db_session.query(Devices).filter(Devices.id == device_id).delete()
    db_session.commit()
    db_session.close()


def get_manufacturer(engine):
    '''
    01 - Исток
    05 - ТСИ
    '''
    Session = sessionmaker(bind=engine)
    db_session = Session()
    istok_diag_count = db_session.execute("SELECT COUNT(*) FROM serial_num_board WHERE serial_num_board LIKE '%RS____01%';").fetchall()
    tsi_diag_count = db_session.execute("SELECT COUNT(*) FROM serial_num_board WHERE serial_num_board LIKE '%RS____05%';").fetchall()

    istok_device_id = db_session.execute("SELECT serial_num_board, device_id FROM serial_num_board WHERE serial_num_board LIKE '%RS____01%';").fetchall()
    tsi_device_id = db_session.execute("SELECT serial_num_board, device_id FROM serial_num_board WHERE serial_num_board LIKE '%RS____05%';").fetchall()

    istok_ids = []
    for i in istok_device_id:
        istok_ids.append(i[1])

    tsi_ids = []
    for i in tsi_device_id:
        tsi_ids.append(i[1])

    istok_pci = db_session.execute("SELECT COUNT(serial_num_board_id) FROM devices WHERE serial_num_board_id IN %s AND date_time_pci NOT IN ('No');" % str(tuple(istok_ids))).fetchall()
    tsi_pci = db_session.execute("SELECT COUNT(serial_num_board_id) FROM devices WHERE serial_num_board_id IN %s AND date_time_pci NOT IN ('No');" % str(tuple(tsi_ids))).fetchall()
    
    return istok_diag_count[0][0], istok_pci[0][0], tsi_diag_count[0][0], tsi_pci[0][0]


def write_macs_and_serial_num(engine, serial_num_router):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    sn_router_id = db_session.query(SerialNumRouter).filter(SerialNumRouter.serial_num_router == serial_num_router).one().id
    device_id = db_session.query(Devices).filter(Devices.serial_num_router_id == sn_router_id).one().id
    mac_list = []
    macs = db_session.query(Macs).with_for_update().filter(Macs.device_id == device_id).limit(3).all()
    for item in macs:
        mac_list.append(item.mac)
    return mac_list


def update_date_time_pci(engine, serial_num_router):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    sn_router_id = db_session.query(SerialNumRouter).filter(SerialNumRouter.serial_num_router == serial_num_router).one().id
    db_session.query(Devices).filter(Devices.serial_num_router_id == sn_router_id).update({"date_time_pci": date_time})
    db_session.commit()
    db_session.close()


def check_date_time_pci(engine, serial_num_router):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    sn_router_id = db_session.query(SerialNumRouter).filter(SerialNumRouter.serial_num_router == serial_num_router).one().id
    d_t = db_session.query(Devices).filter(Devices.serial_num_router_id == sn_router_id).one().date_time_pci
    return d_t


def update_date_time_package(engine, serial_num_router):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    sn_router_id = db_session.query(SerialNumRouter).filter(SerialNumRouter.serial_num_router == serial_num_router).one().id
    db_session.query(Devices).filter(Devices.serial_num_router_id == sn_router_id).update({"date_time_package": date_time})
    db_session.commit()
    db_session.close()


def check_board_count(engine, serial_num):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    board_count = db_session.execute(f"SELECT COUNT(*) FROM board_validation WHERE serial_num_board = '{serial_num}'").scalar()

    db_session.close()
    
    return board_count


def update_board_validation_valid(engine, serial_num):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    db_session.execute(f"UPDATE board_validation SET validation = True WHERE serial_num_board = '{serial_num}'")
    db_session.execute(f"UPDATE board_validation SET error_code = '000' WHERE serial_num_board = '{serial_num}'")
    db_session.commit()

    db_session.close()


def update_board_validation_defect(engine, serial_num, error_code):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    db_session.execute(f"UPDATE board_validation SET validation = False WHERE serial_num_board = '{serial_num}'")
    db_session.execute(f"UPDATE board_validation SET error_code = '{error_code}' WHERE serial_num_board = '{serial_num}'")
    db_session.commit()

    db_session.close()


def get_error_code(engine, serial_num_board):
    Session = sessionmaker(bind=engine)
    db_session = Session()    
    error_code = db_session.execute(f"SELECT error_code FROM board_validation WHERE serial_num_board = '{serial_num_board}'").scalar()
    return error_code


def update_error_code(engine, serial_num_board):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    db_session.execute(f"UPDATE board_validation SET error_code = '000' WHERE serial_num_board = '{serial_num_board}'")
    db_session.commit()

    db_session.close()


def get_errors_count(engine):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    errors_count = []
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '000'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '201'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '202'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '401'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '403'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '404'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '501'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '666'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '009'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '090'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '900'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '099'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '909'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '990'").scalar())
    errors_count.append(db_session.execute("SELECT COUNT(*) FROM board_validation WHERE error_code = '999'").scalar())

    db_session.close()

    return errors_count


def add_board_serial_number_valid(engine, board_serial_number, author):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    db_session.execute(f"INSERT INTO board_validation (serial_num_board, validation, author, datetime) VALUES('{board_serial_number}', {True}, '{author}', '{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}')")
    db_session.commit()

    db_session.close()


def add_board_serial_number_defect(engine, board_serial_number, author):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    db_session.execute(f"INSERT INTO board_validation (serial_num_board, validation, author, datetime) VALUES('{board_serial_number}', {False}, '{author}', '{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}')")
    db_session.commit()

    db_session.close()


def check_board_in_db(engine, serial_number):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    serial_num_count = db_session.execute(f"SELECT COUNT(*) FROM board_validation WHERE serial_num_board = '{serial_number}'").scalar()

    db_session.close()

    return serial_num_count


# print(check_board_validation(engine, 'RS102001180001'))


db_session.close()
