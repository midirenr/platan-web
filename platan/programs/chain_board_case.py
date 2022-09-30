import pyodbc


def update_table(board_serial_number, case_serial_number):
    connect_to_database = pyodbc.connect(
        'Driver={SQL Server};'
        'Server=DESKTOP-9615O5F\SQLEXPRESS;'
        'Database=work;'
        'Trusted_Connection=yes;'
    )

    connect_to_database.execute(f"INSERT INTO chain_board_case VALUES('{board_serial_number}', '{case_serial_number}')").commit()
