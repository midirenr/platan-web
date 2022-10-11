from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml
from datetime import datetime


yaml_file = 'db_history.yaml'
with open('platan/programs/yamls/db_history.yaml') as f:
    params = yaml.safe_load(f)
db_host, db_port, db_username, db_password, db_name = list(params['db'].values())

engine_history = create_engine(f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

Session = sessionmaker(bind=engine_history)
db_session = Session()
#cursor = connect.cursor()

def create_table(serial_number):
    Session = sessionmaker(bind=engine_history)
    db_session = Session()
    db_session.execute(f'''CREATE TABLE BOARD_{serial_number}  
         (ID INT PRIMARY KEY NOT NULL,
         MESSAGE TEXT NOT NULL,
         DATETIME TEXT NOT NULL);''')
    db_session.commit()
    db_session.close()
#create_table('RS1020011A0001')

def insert_commit(serial_number, msg):
    Session = sessionmaker(bind=engine_history)
    db_session = Session()
    date_time = str(datetime.now())[:-7].replace(':', '-').replace(' ', '_')
    db_session.execute(f"SELECT COUNT(*) FROM BOARD_{serial_number}")
    count = db_session.fetchone()[0] + 1
    db_session.execute(
      f"INSERT INTO BOARD_{serial_number} (ID, MESSAGE, DATETIME) VALUES ({count}, '{msg}', '{date_time}')"
    )
    db_session.commit()
    db_session.close()

#insert_commit('RS1020011A0001', 'СТЕНД_ДИАГНОСТИКИ, Ошибка: 000')


def get_history(serial_number):
    Session = sessionmaker(bind=engine_history)
    db_session = Session()
    rows = db_session.execute(f"SELECT id, message, datetime from board_{serial_number}").fetchall()
    db_session.close()
    return rows

def check_sn(engine, serial_num):
    Session = sessionmaker(bind=engine)
    db_session = Session()
    try:
        sn_board_id = db_session.query(serial_num).filter(serial_num.serial_num_board == serial_num).one().id
        return True
    except:
        return False