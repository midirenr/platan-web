def generate_serial_numbers():
    test_label = '123'
    print('Debug')
    return test_label

'''
    y = self.comboType.currentText()
    h = self.comboMod.currentText()
    j = self.comboDetail.currentText()
    p = self.comboPlace.currentText()
    number = self.spinBox.value()
    y_tup = {
        'Сервисный маршрутизатор': 'RS',
        'Граничный маршрутизатор': 'RB',
        'Коммутатор доступа': 'SA',
        'Коммутатор агрегации': 'SG',
        'Коммутатор ЦОД': 'SC',
    }
    h_tup = {
        'ISN41508T4': '10',
        'ISN41508T3': '20',
        'ISN41508T3-M': '30',
        'ISN41508T3-M/ISES1004': '31',
        'ISN41508T3-M/ISES0108': '32',
        'ISN41508T3-M/ISES00114': '33',
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
    j_tup = {
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
    p_tup = {
        'Исток': '01',
        'EMS Expert': '02',
        'ТМИ': '03',
        'Альт Мастер': '04',
        'ТСИ': '05',
        'Резанит': '06',
    }

    Type_of_device = y_tup.get(y)
    Modification = h_tup.get(h)
    Cod_of_detail = j_tup.get(j)
    Place = p_tup.get(p)

    import datetime
    year_now = datetime.date.today().year
    if year_now == 2022:
        Year = 1
    else:
        Year = year_now - 2022 + 1
    Y = str(hex(Year)).split('x')[-1].capitalize()

    Month = datetime.date.today().month
    M = str(hex(Month)).split('x')[-1].capitalize()

    username = os.getlogin()

    with open(f'/home/{username}/Desktop/SerialNumber/{y}/{h}/{j}/log/how_mach', 'r') as f1:
        how_mach = list(deque(f1, 1))

    last = int(how_mach[0])

    with open(f'/home/{username}/Desktop/SerialNumber/{y}/{h}/{j}/log/how_mach', 'w') as f2:
        new_last = last + number
        f2.write(str(new_last))

    delta = last + number

    current_time = str(datetime.datetime.now())[:-7].replace(' ', '_').replace(':', '-')

    serial_num = Type_of_device + Modification + Cod_of_detail + Place + Y + M
    folder = f'qrcode-{j}-{current_time}'
    os.mkdir(f'/home/{username}/Desktop/QRcode/{y}/{h}/{j}/{folder}')

    serial_namber_lst = []
    for i in range(last + 1, delta + 1):
        if i >= 1 and i < 10:
            N = '000' + str(i)
        elif i >= 10 and i < 100:
            N = '00' + str(i)
        elif i >= 100 and i < 1000:
            N = '0' + str(i)
        elif i >= 1000 and i < 10000:
            N = '' + str(i)
        serial_namber = serial_num + N
        filename = f'/home/{username}/Desktop/QRcode/{y}/{h}/{j}/{folder}/{serial_namber}.png'
        img = qrcode.make(serial_namber)
        img.save(filename)
        serial_namber_lst.append(serial_namber)

    self.plain_out.setPlainText('Processing...')

    fullname = f'serial_namber_for_{h}_{j}({current_time})'
    with open(f'/home/{username}/Desktop/SerialNumber/{y}/{h}/{j}/{fullname}.txt', "w") as file:
        for i in serial_namber_lst:
            print(i, file=file)

    pdf = FPDF()
    dirname = f'/home/{username}/Desktop/QRcode/{y}/{h}/{j}/{folder}/'
    list_png = os.listdir(dirname)
    imagelist = []

    for i in list_png:
        pdf_l = f'/home/{username}/Desktop/QRcode/{y}/{h}/{j}/{folder}/{i}'
        imagelist.append(pdf_l)

    list_png.sort()
    imagelist.sort()

    pdf.add_page()
    for image in imagelist:
        image_split = image.split('/')[-1] + '\n\n\n'
        pdf.set_margin(1)
        pdf.image(image, None, None, 10, 10)
        pdf.set_font("Arial", size=5)
        pdf.write(1, txt=image_split)

    pdf.output(f'/home/{username}/Desktop/QRcode/{y}/{h}/{j}/{folder}/{folder}.pdf', 'F')

    output_text = f'Программа завершена!!!!\n\n[+] Фaйл {fullname}.txt co сгенерированными серийными номеров на рабочем столе в папке SerialNumber/{y}/{h}/{j}/[+] Папка {folder} co сгенерированными QR-кодами на рабочем столе в папке QRcode/{y}/{h}/{j}/\n[+] Файл {folder}.pdf co сгенерированными QR-кодами на рабочем столе в папке QRcode/{y}/{h}/{j}/{folder}\n\n'

    self.plain_out.setPlainText(output_text)
'''
