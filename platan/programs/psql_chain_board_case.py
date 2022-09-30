from .db_2000 import *


def chain_board_case(board_serial_number, case_serial_number):
    write_serial_num_router(engine, board_serial_number, case_serial_number)

    """
    Session = sessionmaker(bind=engine)
    db_session = Session()
    db_session.execute(f"INSERT INTO chain_board_case(board_serial_number, case_serial_number) VALUES('{board_serial_number}', '{case_serial_number}')")
    db_session.commit()

    
    db_session.close()
    """