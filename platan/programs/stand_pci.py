import subprocess
import sys
import logging
import traceback
import re

import yaml
import os
from .db_2000 import *
import concurrent.futures
import time
import telnetlib
from telnetlib import Telnet
from .docx_pdf_module import *
import paramiko
from .db_history import *


def run(board_count, modification, board_serial_number_list, host_ip):
    class CustomError(Exception):
        pass

    class CustomErrorExtended(Exception):
        pass

    def logger_debag(msg, sn, stend, place):
        if place == 1:
            logger_debag_1.debug(f'{msg}', extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        elif place == 2:
            logger_debag_2.debug(f'{msg}', extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        elif place == 3:
            logger_debag_3.debug(f'{msg}', extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        elif place == 4:
            logger_debag_4.debug(f'{msg}', extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        elif place == 5:
            logger_debag_5.debug(f'{msg}', extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        else:
            logger_debag_5.debug(f'{msg}', extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})

    def countdown(t):
        """
        Функция для обратного отсчета времени, не задействуется, но можно использовать вместо
        прогрессбара
        :param t: время в секундах
        :return: ничего
        """
        while t:
            mins, secs = divmod(t, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            time.sleep(1)
            t -= 1

    def verify_yaml_name(yaml_file):
        """
        Ищет файл с введенным именем в текущем каталоге
        :param yaml_file: имя файла конфигурации
        :return: возвращает также имя файла конфигурации. Может отличаться от изначально введенного пользователем
        """
        os.chdir('yamls/')
        while True:
            if not yaml_file in filter(os.path.isfile, os.listdir(os.curdir)):
                output_file.write('Отсутствует конфигурационный файл!\n')
                output_file.flush()
                raise CustomError(f'Отсутствует конфигурационный файл!')
            else:
                os.chdir('..')
                break
        return yaml_file

    def update_history_db(serial_number, msg):
        """
        Добавление в базу данных информации о статусе прохождении стенда
        """
        try:
            insert_commit(serial_number, msg)
        except:
            create_table(serial_number)
            insert_commit(serial_number, msg)

    def tcp_to_serial_bridge_restart(board_count):
        """
        Функция перезапускает tcp-to-serial мост
        :param board_count: номер устройства, он же номер моста
        :return: ничего
        """
        subprocess.run(['sudo', 'systemctl', 'restart', f'tcp-to-serial-bridge-router{board_count}'])
        time.sleep(2)
        if not 'active (running)' in subprocess.run(
                ['systemctl', 'status', f'tcp-to-serial-bridge-router{board_count}'],
                stdout=subprocess.PIPE).stdout.decode('utf-8'):
            logger_stend.error(f'Не удается запустить сервис tcp-to-serial-bridge-router{board_count}, \
                            выполнение программы невозможно', extra={'stend': f'{stend}'})
            sys.exit()
        logger_stend.info(f'Cервис tcp-to-serial-bridge-router{board_count} запущен', extra={'stend': f'{stend}'})
        output_file.write(f'Cервис tcp-to-serial-bridge-router{board_count} запущен\n')
        output_file.flush()

    def tcp_to_serial_bridge_restart_ssh(board_count):
        """
        Функция перезапускает tcp-to-serial мост по ssh
        :param dev_count: номер устройства, он же номер моста
        :return: ничего
        """
        try:
            host_config = {
                'device_type': 'linux',
                'host': host_ip,
                'username': 'istok',
                'password': 'istok',
                'secret': 'istok',
                'port': '22',
            }
            ssh = ConnectHandler(**host_config)
            ssh.enable()
            ssh.send_command('sudo systemctl restart tcp-to-serial-bridge-router1.service')
            command_status = ssh.send_command('sudo systemctl status tcp-to-serial-bridge-router1.service')
            if not 'active (running)' in command_status:
                logger_stend.error(f'Не удается запустить сервис tcp-to-serial-bridge-router{board_count}, \
                            выполнение программы невозможно', extra={'stend': f'{stend}'})
                output_file.write(f'Не удается запустить сервис tcp-to-serial-bridge-router_ssh')
                output_file.flush()
            else:
                logger_stend.info(f'Cервис tcp-to-serial-bridge-router{board_count} запущен',
                                  extra={'stend': f'{stend}'})
                output_file.write(f'Cервис tcp-to-serial-bridge-router{board_count} запущен\n')
                output_file.flush()
            ssh.disconnect()
        except:
            raise CustomError('Что пошло не так! Проверьте подключение')

    def host_service_check(service):
        """
        Проверка состояния сервисов на хосте. Если сервис не запущен, выполнение скрипта заканчивается
        :param service: имя сервиса
        :return: ничего
        """
        output_file.write('Проверка сервиса {}...\n'.format(service))
        output_file.flush()
        try:
            if subprocess.run(['pgrep', service]).returncode == 0:
                output_file.write('Сервис {} включен\n'.format(service))
                logger_stend.info('Сервис {} включен'.format(service), extra={'stend': f'{stend}'})
            else:
                raise CustomError(f'Проверьте состояние сервиса {service}, выполнение программы невозможно')
        except CustomError as e:
            logger_stend.error(e)
            sys.exit()
        except:
            logger_stend.error(f'Ошибка при проверке состояния сервиса {service} \n %s' % traceback.format_exc(),
                               extra={'stend': f'{stend}'})
            sys.exit()

    def host_service_check_ssh(service):
        """
        Проверка состояния сервисов на хосте. Если сервис не запущен, выполнение скрипта заканчивается
        :param service: имя сервиса
        :return: ничего
        """
        output_file.write('Проверка сервиса {}...\n'.format(service))
        output_file.flush()
        try:
            host_config = {
                'device_type': 'linux',
                'host': host_ip,
                'username': 'istok',
                'password': 'istok',
                'secret': 'istok',
                'port': '22',
            }
            ssh = ConnectHandler(**host_config)
            ssh.enable()
            command_status = ssh.send_command('sudo systemctl status {service}.service')
            if not 'active (running)' in command_status:
                ssh.send_command(f"sudo systemctl restart {service}.service ")
                command_status = ssh.send_command(f"sudo systemctl status {service}.service")
                if not 'active (running)' in command_status:
                    logger_stend.error(f'Сервис {service} не удается запустить, \
                            выполнение программы невозможно', extra={'stend': f'{stend}'})
                    output_file.write('Сервис не удается запустить\n'.format(service))
                    output_file.flush()
                else:
                    logger_stend.info(f'Cервис {service} запущен', extra={'stend': f'{stend}'})
                    output_file.write('Сервис {} запущен\n'.format(service))
                    output_file.flush()
            else:
                logger_stend.info(f'Cервис {service} запущен', extra={'stend': f'{stend}'})
                output_file.write('Сервис {} запущен\n'.format(service))
                output_file.flush()
            ssh.disconnect()
        except:
            raise CustomError('Что пошло не так! Проверьте подключение')

    def send_command(connect, command, sn, place, timeout=10, expect_string='#', just_wait=False):
        """
        Посылает одну команду на устройство
        :param just_wait: если True, то просто ждем до появления expect_string или до таймаута.
                        Если False, то проверяем, есть ли expect_string в выводе команды
        :param expect_string: ожидаемый вывод в виде текстовой строки
        :param connect: объект подключения по telnet
        :param command: команда в виде текстовой строки
        :param timeout: таймаут
        :return: возвращает вывод команды
        """
        stend = 'СТЕНД_ПСИ'
        expect_string_bytes = expect_string.encode('utf-8')
        connect.write(f'{command}\n'.encode('utf-8'))
        logger_debag(f'send: {command}', sn, stend, place)
        output = connect.read_until(expect_string_bytes, timeout).decode('utf-8', 'ignore')
        logger_debag(f'resend: {output}', sn, stend, place)
        if not just_wait:
            if expect_string not in output:
                logger_script.error('Неожиданный вывод команды:' f'ВЫВОД КОМАНДЫ: {output}',
                                    extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                raise CustomErrorExtended(['Неожиданный вывод команды', f'ВЫВОД КОМАНДЫ: {output}', '202'])
        return output

    def send_commands(connect, commands, sn, place, timeout=20, expect_string='#'):
        """
        Посылает несколько команд на устройство
        :param connect: объект подключения по telnet
        :param commands: список команд
        :param timeout: таймаут
        :param expect_string: ожидаемый вывод в виде текстовой строки
        :return: возвращает вывод всех команд в виде списка
        """
        stend = 'СТЕНД_ПСИ'
        all_output = []
        expect_string_bytes = expect_string.encode('utf-8')
        for command in commands:
            connect.write(f'{command}\n'.encode('utf-8'))
            logger_debag(f'send: {command}', sn, stend, place)
            output = connect.read_until(expect_string_bytes, timeout).decode('utf-8', 'ignore')
            all_output.append(output)
            logger_debag(f'resend: {output}', sn, stend, place)
            if 'No link.' in output:
                logger_script.error('No link. Проблема с соединением.',
                                    extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                raise CustomErrorExtended(
                    ['No link. Проблема с соединением. Проверьте кабель и SFP-модуль.', f'ВЫВОД КОМАНД: {all_output}',
                     '406'])
            if expect_string not in output:
                logger_script.error('Неожиданный вывод команды:' f'ВЫВОД КОМАНДЫ: {all_output}',
                                    extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                raise CustomErrorExtended(['Неожиданный вывод команды', f'ВЫВОД КОМАНД: {all_output}', '202'])

        return all_output

    def enter_uboot(connect, phase, sn, stend, place):
        """
        Вход в Uboot маршрутизатора
        :param connect: объект подключения по telnet
        :param phase: фаза (install или erase)
        :return: приглашение cli после входа в Uboot
        """
        # garbage = connect.read_very_eager().decode('utf-8', 'ignore')
        console_output = connect.read_until(b'Hit any key to stop autoboot', timeout=20).decode('utf-8', 'ignore')
        logger_debag(console_output, sn, stend, place)
        if phase == 'install' and 'Hit any key to stop autoboot' not in console_output:
            logger_script.error('Не удалось войти в U-BOOT...',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(
                ['Не удалось войти в Uboot. Возможно BOOT LOOP!', f'ВЫВОД В КОНСОЛЬ: {console_output}', '404'])
        if phase == 'erase' and 'Hit any key to stop autoboot' not in console_output:
            raise CustomErrorExtended(
                ['Не удалось войти в Uboot при очистке flash', f'ВЫВОД В КОНСОЛЬ: {console_output}', '404'])
        connect.write(b'a')  # отправляем символ 'a' чтобы остановить таймер
        time.sleep(1)
        connect.write(b'\x1b[B\n')
        time.sleep(1)
        connect.write(b'\x1b[B\n')
        time.sleep(1)
        connect.write(b'\r')
        time.sleep(1)
        uboot_prompt = connect.read_very_eager().decode('utf-8')
        logger_debag(uboot_prompt, sn, stend, place)
        logger_script.info('Вход в U-boot выполнен успешно',
                           extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        return uboot_prompt, console_output

    def set_bootmenu(connect, host_ip, admin_password, serviceuser_password, master_password, phase, sn, stend, place):
        """
        Настройка Bootmenu для автоматической установки ПО
        :param master_password: пароль учетки master
        :param serviceuser_password: пароль учетки serviceuser
        :param admin_password: пароль учетки admin
        :param ftp_directory: ftp директория с пакетами ПО
        :param host_ip: адрес tftp/ftp сервера
        :param connect: объект подключения по telnet
        :return:
        """
        if phase == 'install':
            initrd_file_name = 'initrd.gz'
        elif phase == 'erase':
            initrd_file_name = 'initrd_erase.gz'

        if modification == 'КРПГ.465614.001-05' or modification == 'КРПГ.465614.001-04':
            setenv_commands = [
                f'usb start ; \
                env set phy_sfp 1 ; \
                dhcp ; \
                setenv serverip {host_ip} ; \
                setenv fdt_addr_n 0x85D00000 ; \
                setenv fdt_file_name baikal.dtb ; \
                setenv initrd_addr_n 0x86000000 ; \
                setenv initrd_file_name {initrd_file_name} ; \
                setenv kernel_addr_n 0x80100000 ; \
                setenv kernel_file_name vmlinux.bin ; \
                setenv ci_installed 1 ; \
                setenv bootargs console=ttyS0,115200n8 usbcore.autosuspend=-1 \
                ei-auto_install=true ei-install_disk=/dev/sda ei-passwd_admin={admin_password} \
                ei-passwd_serviceuser={serviceuser_password} ei-passwd_master={master_password} ; \
                setenv sata_setup_disk "sata init; run sata_common_disk" ; \
                saveenv ; \
                run net_load_all_tftp ; run all_bootnr'
            ]
        else:
            setenv_commands = [
                f'usb start ; \
                dhcp ; \
                setenv serverip {host_ip} ; \
                setenv fdt_addr_n 0x85D00000 ; \
                setenv fdt_file_name baikal.dtb ; \
                setenv initrd_addr_n 0x86000000 ; \
                setenv initrd_file_name {initrd_file_name} ; \
                setenv kernel_addr_n 0x80100000 ; \
                setenv kernel_file_name vmlinux.bin ; \
                setenv bootargs console=ttyS0,115200n8 usbcore.autosuspend=-1 \
                ei-auto_install=true ei-install_disk=/dev/sda ei-passwd_admin={admin_password} \
                ei-passwd_serviceuser={serviceuser_password} ei-passwd_master={master_password} ; \
                saveenv ; \
                run net_load_all_tftp ; run all_bootnr'

            ]
        logger_script.info('Начало наcтройки BOOTMENU', extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        set_bootmenu_output = send_commands(connect, setenv_commands, sn, place, timeout=90)
        logger_script.info('BOOTMENU натсроено', extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        if 'Loading' in set_bootmenu_output[0]:
            logger_script.info('Началась загрузка файлов по TFTP',
                               extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        return set_bootmenu_output

    def init_disk(connect, sn, stend, place):
        time.sleep(10)
        sata_list = []
        for _ in range(6):
            time.sleep(3)
            sata_info = send_command(connect, 'sata init', sn, place, timeout=30)
            sata_list.append(sata_info)

        check_list = []
        for i in sata_list:
            if 'Product model number: nanoSSD 3ME3' in i:
                check_list.append(True)

        if len(check_list) >= 5:
            check_status = True
        else:
            check_status = False

        if check_status == True:
            logger_script.info(f'SSD удалось инициализировать! SSD удалось инициализировать {len(check_list)} раз из 6',
                               extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            return sata_info
        else:
            logger_script.error('SSD работает нестабильно!',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(
                ['SSD работает нестабильно!', f'SSD удалось инициализировать {len(check_list)} раз из 6', '501'])

    def install_software(connect, wait_time, phase, sn, stend, place):
        """
        Запуск установки ПО
        :param phase: фаза установки: install или erase
        :param wait_time: время установки в секундах
        :param connect: объект подключения по telnet
        :return: возвращает первые 5 секунд вывода с начала установки софта
        """
        console_output = connect.read_until(b'  No volume groups found', timeout=120).decode('utf-8')
        logger_debag(f'Вывод в консоль перед установкой файлов с флешки: {console_output}', sn, stend, place)
        if phase == 'install' and '  No volume groups found' in console_output:
            logger_script.info('Загрузка файлов по TFTP прошла успешно. Началась установка файлов с флешки',
                               extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        elif phase == 'install' and 'Error: Install disk with label: INSTALLER not found' in console_output:
            logger_script.error('Не удалось обнаружить флешку с LABEL: INSTALLER',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(
                ['Не удалось обнаружить флешку с LABEL: INSTALLER', f'ВЫВОД В КОНСОЛЬ: {console_output}', '403'])
        elif phase == 'install' and 'Error while generating lvm2 partitions' in console_output:
            logger_script.error('Возникли проблемы с разбиением диска на разделы',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(
                ['Возникли проблемы с разбиением диска на разделы', f'ВЫВОД В КОНСОЛЬ: {console_output}', '402'])
        elif phase == 'install' and 'Disk too small' in console_output:
            logger_script.error('Возникли проблемы с определением размера SSD',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(
                ['Возникли проблемы с определением размера SSD', f'ВЫВОД В КОНСОЛЬ: {console_output}', '408'])
        elif phase == 'install' and 'Lvm group vg0 already exists' in console_output:
            logger_script.error('На флешке/HDD найдены разделы. Необходимо отформатировать флешку/HDD',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(['На флешке/HDD найдены разделы. Необходимо отформатировать флешку/HDD',
                                       f'ВЫВОД В КОНСОЛЬ: {console_output}', '410'])
        else:
            logger_script.error('Не удалось начать установку ПО по неизвестным причинам',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(
                ['Не удалось начать установку ПО по неизвестным причинам', f'ВЫВОД В КОНСОЛЬ: {console_output}', '407'])
        start_installing_sw = connect.read_very_eager().decode('utf-8')
        countdown(wait_time)
        return start_installing_sw

    def login_to_router(connect, sn, stend, place):
        """
        Функция для залогинивания в маршрутизатор
        :param connect: объект подключения по telnet
        :return: возвращает prompt
        """
        garbage = connect.read_very_eager().decode('utf-8', 'ignore')  # вычитываем буфер для его очистки, игнорируя
        # байты, которые не декодируются utf-8
        logger_debag(garbage, sn, stend, place)
        prompt = send_command(connect, '', sn, place, timeout=8, just_wait=True)  # посылаем перевод строки
        time.sleep(10)
        if '#' in prompt:
            connect.write(b'\x03')
            send_command(connect, 'end', sn, place)
        elif 'login:' in prompt:
            send_command(connect, 'admin', sn, place, expect_string='Password')
            output = send_command(connect, f'{admin_password}', sn, place, just_wait=True)
            logger_debag(output, sn, stend, place)
        elif 'Password:' in prompt:
            send_command(connect, '', sn, place, expect_string='login')
            send_command(connect, 'admin', sn, place, expect_string='Password')
            send_command(connect, f'{admin_password}', sn, place)
        else:
            logger_script.error('Неожиданное приглашение cli после установки ПО',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(['Неожиданное приглашение cli после установки ПО', f'PROMPT: {prompt}', '401'])
        return prompt

    def post_install_check(connect, sn, stend, place):
        """
        Проверка того, что роутер загрузился после установки ПО. Пробуем логиниться 5 раз с интервалом 15 секунд
        :param connect: объект подключения по telnet
        :return: результат "show version"
        """
        output_before_check = connect.read_very_eager().decode('utf-8', 'ignore')
        output_before_check_min = output_before_check[-5800::]
        logger_debag(f'ВЫВОД ДО ПОПЫТКИ ЗАЛОГИНИВАНИЯ: {output_before_check_min}', sn, stend, place)
        if 'Kernel panic' in output_before_check:
            logger_script.error('При загрузке после установки ПО возник Kernel Panic',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(['При загрузке после установки ПО возник Kernel Panic',
                                       f'KERNEL PANIC TRACE: {output_before_check}', '409'])
        elif 'Waiting for full initialization of mprdaemon' in output_before_check:
            logger_script.info('ПО было успешно установленно',
                               extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        else:
            logger_script.warning('Возможно ПО не было установлено, либо было установлено с ошибкой',
                                  extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})

        for i in range(3):
            try:
                logger_debag(f'Попытка залогиниться №{i + 1}', sn, stend, place)
                login_to_router(connect, sn, stend, place)
                break
            except CustomErrorExtended as e:
                logger_script.error(e, extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                failed_prompt_result = e
                time.sleep(15)
        if i == 5:
            logger_script.error(
                f'Маршрутизатор не загрузился после установки ПО, не найдено приглашение cli {failed_prompt_result}',
                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            raise CustomErrorExtended(['Маршрутизатор не загрузился после установки ПО, не найдено приглашение cli',
                                       f'PROMPT: {failed_prompt_result}',
                                       '401',
                                       f'Вывод в консоль до попытки залогиниться: {output_before_check}'])
        time.sleep(5)
        version = send_command(connect, 'show version', sn, place)
        logger_script.info('Вход на устройство выполнен успешно',
                           extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        return version

    def hdd_check(connect, sn, stend, place):
        """
        Проверка наличия hdd
        :param connect: объект подключения по telnet
        :return: вывод lshw и результат проверки
        """
        login_to_router(connect, sn, stend, place)
        send_command(connect, 'root-shell', sn, place, timeout=20, expect_string='>')
        send_command(connect, master_password, sn, place)
        lshw_command = send_command(connect, 'lshw -businfo', sn, place, timeout=25)
        send_command(connect, 'exit', sn, place)
        if 'scsi@1:0.0.0' not in lshw_command:
            check_result_out = 'Внешний HDD не найден'
        else:
            check_result_out = 'Внешний HDD найден'

        if check_result_out == 'Внешний HDD найден':
            logger_script.info(check_result_out, extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        elif check_result_out == 'Внешний HDD не найден':
            logger_script.error(check_result_out, extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})

        if 'scsi@0:0.0.0' not in lshw_command:
            check_result_in = 'Внутренний HDD не найден'
        else:
            check_result_in = 'Внутренний HDD найден'

        if check_result_in == 'Внутренний HDD найден':
            logger_script.info(check_result_in, extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        elif check_result_in == 'Внутренний HDD не найден':
            logger_script.error(check_result_in, extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        return lshw_command, check_result_out, check_result_in

    def flash_check(connect, hdd_present, hdd_check_result, sn, stend, place):
        """
        Проверка наличия двух флешек
        :param connect: объект подключения по telnet
        :param hdd_present: признак наличия hdd, указывается в yaml файле
        :param hdd_check_result: результат проверки hdd
        :return: вывод lshw и результат проверки
        """
        if hdd_present:
            if hdd_check_result[1] == 'Внешний HDD найден' and hdd_check_result[2] == 'Внутренний HDD найден':
                flash1 = '/dev/sdc'
                flash2 = '/dev/sdd'
            elif hdd_check_result[1] == 'Внешний HDD не найден' and hdd_check_result[2] == 'Внутренний HDD найден':
                flash1 = '/dev/sdb'
                flash2 = '/dev/sdc'
            elif hdd_check_result[1] == 'Внешний HDD найден' and hdd_check_result[2] == 'Внутренний HDD не найден':
                flash1 = '/dev/sdb'
                flash2 = '/dev/sdc'
        else:
            flash1 = '/dev/sdb'
            flash2 = '/dev/sdc'
        login_to_router(connect, sn, stend, place)
        send_command(connect, 'root-shell', sn, place, timeout=20, expect_string='>')
        send_command(connect, master_password, sn, place)
        lshw_command = send_command(connect, 'lshw -businfo', sn, place, timeout=25)
        send_command(connect, 'exit', sn, place)
        if flash1 not in lshw_command or flash2 not in lshw_command:
            check_result = 'По крайней мере один flash накопитель не определился, возможно, USB порты неисправны'
            logger_script.error(check_result, extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        else:
            check_result = 'Flash накопители найдены'
            logger_script.info(check_result, extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        return lshw_command, check_result

    def ports_check(connect, commands, dev_num, sn, stend, place):
        """
        Проверка работоспособности портов
        :param connect: объект подключения по telnet
        :param commands: список с командами для настройки роутера
        :param dev_num: номер проверяемого устройства
        :return: результат пинга
        """
        login_to_router(connect, sn, stend, place)
        send_commands(connect, commands, sn, place, expect_string='admin@sr-be')
        third_octet = 200 + dev_num
        # отправляем 5 пакетов чтобы заполнились ARP и FDB таблицы на устройствах, потом отправляем тестовые 30 пакетов
        subprocess.run(['ping', f'192.168.{third_octet}.1', '-c', '5'],
                       stdout=subprocess.PIPE).stdout.decode('utf-8')
        ping_result = subprocess.run(['ping', f'192.168.{third_octet}.1', '-c', '30', '-i', '0,2'],
                                     stdout=subprocess.PIPE).stdout.decode('utf-8')
        logger_debag(ping_result, sn, stend, place)
        if 'Destination Host Unreachable' in ping_result:
            logger_script.error('Порты не прошли проверку',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        else:
            logger_script.info('Порты успешно прошли проверку',
                               extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
        return ping_result

    def nmc_check(connect):
        login_to_router(connect)
        send_command(connect, 'root-shell', expect_string='>')
        send_command(connect, master_password)
        lshw_command = send_command(connect, 'lshw -businfo -c network', timeout=25)
        logging.verbose(lshw_command)
        send_command(connect, 'exit')
        pci_addr = 'pci@0000:01:00'
        for port_num in range(nmc_ports_count):
            if f'{pci_addr}.{port_num}' in lshw_command:
                check_result = 'Все порты NMC модуля найдены'
            else:
                check_result = 'По крайней мере один порт NMC модуля не найден'
        logging.verbose(check_result)
        return lshw_command, check_result

    def erase_disk(connect, sn, stend, place):
        send_command(connect, 'root-shell', sn, place, timeout=20, expect_string='>')
        send_command(connect, master_password, sn, place)
        send_command(connect, 'fdisk /dev/sdb', sn, place, timeout=10, expect_string='Команда (m для справки): ')
        send_command(connect, 'd', sn, place, timeout=10, expect_string='Команда (m для справки): ')
        send_command(connect, '1', sn, place, timeout=10, expect_string='Команда (m для справки): ')
        send_command(connect, 'd', sn, place, timeout=10, expect_string='Команда (m для справки): ')
        fdisk_info = send_command(connect, 'w', sn, place, timeout=10)
        if 'Синхронизируются диски' in fdisk_info:
            send_command(connect, 'q', sn, place, timeout=5)
            send_command(connect, 'exit', sn, place, timeout=5)
            logger_script.info(f'Удаление разделов выполнено успешно',
                               extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
            return fdisk_info
        else:
            logger_script.error(f'При удалении разделов возникла ошибка',
                                extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})

    def clear_ip_pool(stend):
        host = '10.65.11.10'
        user = 'admin'
        secret = 'admin'
        port = 22
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=user, password=secret, port=port)
            stdin, stdout, stderr = client.exec_command("clear ip dhcp binding *")
            data = stdout.read() + stderr.read()
            client.close()
            logger_stend.info('Отчистка пула dhcp успешно завершена', extra={'stend': f'{stend}'})
        except:
            logger_stend.error('Ошибка при отчистки пула dhcp', extra={'stend': f'{stend}'})

    def create_protocol(device_num, serial_num_router, modification, result):
        number = serial_num_router[-5::]
        flash_result = result[f'device_num_{device_num}']['flash_check_result'][1]
        losses = re.findall(r'\d+% packet loss', result[f'device_num_{device_num}']['ping_result'])[0]
        if hdd_present:
            ext_slot_result = result[f'device_num_{device_num}']['hdd_check_result'][1]
        elif nmc_ports_count != 0:
            ext_slot_result = result[f'device_num_{device_num}']['nmc_check_result'][1]
        if hdd_present or nmc_ports_count != 0:
            if ext_slot_result in ['HDD найден',
                                   'Все порты NMC модуля найдены'] and flash_result == 'Flash накопители найдены' and losses == '0% packet loss':
                control_test_0 = 'Пройдено'
                control_test_1 = 'Пройдено'
            else:
                control_test_0 = 'Не пройдено'
                control_test_1 = 'Пройдено'
        else:
            if flash_result == 'Flash накопители найдены' and losses == '0% packet loss':
                control_test_0 = 'Пройдено'
                control_test_1 = 'Пройдено'
            else:
                control_test_0 = 'Не пройдено'
                control_test_1 = 'Пройдено'
        input_docx = fill_the_doc(number, serial_num_router, modification, control_test_0, control_test_1)
        try:
            convert_docx_to_pdf(input_docx)
            return True
        except:
            return False

    def hw_check(device):
        """
        Проверка работоспособности АП с установкой и удалением специальной версии ПО
        :param device: список параметров для подключения через tcp-to-serial мост
        :return: словарь со значениями, выдаваемыми в консоль в процессе установки ПО
        """
        device_num = str(device['port'])[2:]
        result = {f'device_num_{device_num}': {}}
        try:
            with Telnet(host_ip, device['port'], timeout=30) as connect:
                phase = 'install'

                sn = board_serial_number_list[int(device_num) - 1]
                stend = 'СТЕНД_ДИАГНОСТИКИ'
                place = board_serial_number_list.index(sn) + 1
                result[f'device_num_{device_num}']['sn'] = sn

                output_file.write(f'Вход в Uboot устройства {device_num}...\n')
                output_file.flush()
                logger_script.info(f'Вход в Uboot устройства',
                                   extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                result[f'device_num_{device_num}']['uboot_prompt'] = enter_uboot(connect, phase, sn, stend, place)

                output_file.write(f'Инициализация SSD устойства {device_num}...\n')
                output_file.flush()
                logger_script.info(f'Инициализация SSD устойства',
                                   extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                result[f'device_num_{device_num}']['sata_info'] = init_disk(connect, sn, stend, place)

                output_file.write(f'Настройка Bootmenu устройства {device_num}...\n')
                output_file.flush()
                logger_script.info(f'Настройка Bootmenu устройства',
                                   extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                result[f'device_num_{device_num}']['bootmenu_1_install'] = set_bootmenu(connect, host_ip,
                                                                                        admin_password,
                                                                                        serviceuser_password,
                                                                                        master_password, phase, sn,
                                                                                        stend, place)

                output_file.write(f'Установка ПО на устройство {device_num}...\n')
                output_file.flush()
                logger_script.info(f'Установка ПО на устройство',
                                   extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                time.sleep(5)
                install_software_timeout = 600
                result[f'device_num_{device_num}']['start_installing_sw'] = install_software(connect,
                                                                                             install_software_timeout,
                                                                                             phase, sn, stend, place)

                output_file.write(f'Вход для проведения проверок на устройство {device_num}...\n')
                output_file.flush()
                logger_script.info(f'Вход для проведения проверок на устройство',
                                   extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                result[f'device_num_{device_num}']['post_install_check_result'] = post_install_check(connect, sn, stend,
                                                                                                     place)

                if hdd_present:
                    output_file.write(f'Проверка наличия HDD на устройстве {device_num}...\n')
                    output_file.flush()
                    logger_script.info(f'Проверка наличия HDD на устройстве',
                                       extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                    result[f'device_num_{device_num}']['hdd_check_result'] = hdd_check(connect, sn, stend, place)
                else:
                    result[f'device_num_{device_num}']['hdd_check_result'] = 'Исполнение без HDD, ' \
                                                                             'проверка наличия HDD не проводилась'

                output_file.write(f'Проверка наличия 2-х Flash накопителей на устройстве {device_num}...\n')
                output_file.flush()
                logger_script.info(f'Проверка наличия 2-х Flash накопителей на устройстве',
                                   extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                result[f'device_num_{device_num}']['flash_check_result'] = flash_check(connect, hdd_present,
                                                                                       result[
                                                                                           f'device_num_{device_num}'][
                                                                                           'hdd_check_result'], sn,
                                                                                       stend, place)

                if nmc_ports_count != 0:
                    output_file.write(f'Проверка NMC модуля на устройстве {device_num}...')
                    output_file.flush()
                    result[f'device_num_{device_num}']['nmc_check_result'] = nmc_check(connect)
                else:
                    result[f'device_num_{device_num}']['nmc_check_result'] = 'Исполнение без NMC модуля, проверка ' \
                                                                             'наличия NMC модуля не проводилась '

                output_file.write(f'Проверка работоспособности портов на устройстве {device_num}...\n')
                output_file.flush()
                logger_script.info(f'Проверка работоспособности портов на устройстве',
                                   extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                result[f'device_num_{device_num}']['ping_result'] = ports_check(connect, ports_check_cmds,
                                                                                device['port'] - 230, sn, stend, place)

                output_file.write(f'Удаление разделов на устройстве {device_num}...\n')
                output_file.flush()
                logger_script.info(f'Удаление разделов на устройстве',
                                   extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                result[f'device_num_{device_num}']['erase_disk_result'] = erase_disk(connect, sn, stend, place)

                output_file.write(f'Создание протокола проверки изделия для устройства {device_num}...')
                logger_script.info(f'Создание протокола проверки изделия для устройства', extra={'sn': f'{sn}', 'stend': f'{stend}', 'place': f'{place}'})
                create_protocol(device_num, sn, modification, result)

                result[f'device_num_{device_num}']['error'] = 'False'  # признак не сработавшего исключения
                return result

        except CustomErrorExtended as e:
            result[f'device_num_{device_num}']['error'] = f'Ошибка c устройством {device_num}'  # признак сработавшего
            # исключения
            result[f'device_num_{device_num}']['error_details'] = e.args
            return result
        except:
            logger_debag(traceback.format_exc(), sn, stend, place)
            result[f'device_num_{device_num}']['error'] = f'Ошибка c устройством {device_num}: неизвестная ошибка'
            result[f'device_num_{device_num}']['error_details'] = traceback.format_exc()
            return result

    ports_check_cmds = [
        'configure terminal', 'vlan 12,34,56,78',
        'interface switchport 1', 'switchport access vlan 12', 'no shutdown', 'exit',
        'interface switchport 2', 'switchport access vlan 12', 'no shutdown', 'exit',
        'interface switchport 3', 'switchport access vlan 34', 'no shutdown', 'exit',
        'interface switchport 4', 'switchport access vlan 34', 'no shutdown', 'exit',
        'interface switchport 5', 'switchport access vlan 56', 'no shutdown', 'exit',
        'interface switchport 6', 'switchport access vlan 56', 'no shutdown', 'exit',
        'interface switchport 7', 'switchport access vlan 78', 'no shutdown', 'exit',
        'interface switchport 8', 'switchport access vlan 78', 'no shutdown', 'exit',
        'interface br112', 'include eth1', 'include eth2', 'no shutdown', 'end'
    ]

    modifications_config = {
        'КРПГ.465614.001': 'devices_sp_hdd.yaml',
        'КРПГ.465614.001-01': 'devices_sp_hdd.yaml',
        'КРПГ.465614.001-02': 'devices_sp_pci_2.yaml',
        'КРПГ.465614.001-03': 'devices_sp_pci_0.yaml',
        'КРПГ.465614.001-04': 'devices_sp_hdd.yaml',
        'КРПГ.465614.001-05': 'devices_sp_hdd.yaml',
        'КРПГ.465614.001-06': 'devices_sp_pci_2.yaml',
        'КРПГ.465614.001-07': 'devices_sp_pci_0.yaml',
        'КРПГ.465614.001-08': 'devices_sp_pci_2.yaml',
        'КРПГ.465614.001-09': 'devices_sp_pci_4.yaml',
        'КРПГ.465614.001-10': 'devices_sp_pci_4.yaml',
        'КРПГ.465614.001-11': 'devices_sp_pci_2.yaml',
        'КРПГ.465614.001-12': 'devices_sp_pci_2.yaml',
        'КРПГ.465614.001-13': 'devices_sp_pci_2.yaml',
        'КРПГ.465614.001-14': 'devices_sp_pci_4.yaml',
        'КРПГ.465614.001-15': 'devices_sp_pci_4.yaml',
        'КРПГ.465614.001-16': 'devices_sp_pci_2.yaml',
        'КРПГ.465614.001-17': 'devices_sp_pci_2.yaml',
    }

    output_file = open('platan/templates/ajax/pci_output.html', 'w', encoding='utf-8')
    y_f = modifications_config.get(modification)
    yaml_file = verify_yaml_name(y_f)

    with open(f'yamls/{yaml_file}') as f:
        params = yaml.safe_load(f)
    hdd_present = params['hdd_present']
    admin_password, serviceuser_password, master_password = list(params['passwords'].values())
    nmc_ports_count = params['nmc_ports_count']

    # log_debug
    logger_debag_1 = logging.getLogger('debag_1')
    log_d_1 = logging.FileHandler('.log/debag_log_1.log')
    logger_debag_1.setLevel(logging.DEBUG)
    format_d_script = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(stend)s -  %(sn)s  -  %(place)s  -  %(funcName)s: %(message)s",
        '%Y-%m-%d %H:%M:%S')
    log_d_1.setFormatter(format_d_script)
    logger_debag_1.addHandler(log_d_1)
    logger_debag_2 = logging.getLogger('debag_2')
    log_d_2 = logging.FileHandler('.log/debag_log_2.log')
    logger_debag_2.setLevel(logging.DEBUG)
    format_d_script = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(stend)s -  %(sn)s  -  %(place)s  -  %(funcName)s: %(message)s",
        '%Y-%m-%d %H:%M:%S')
    log_d_2.setFormatter(format_d_script)
    logger_debag_2.addHandler(log_d_2)
    logger_debag_3 = logging.getLogger('debag_3')
    log_d_3 = logging.FileHandler('.log/debag_log_3.log')
    logger_debag_3.setLevel(logging.DEBUG)
    format_d_script = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(stend)s -  %(sn)s  -  %(place)s  -  %(funcName)s: %(message)s",
        '%Y-%m-%d %H:%M:%S')
    log_d_3.setFormatter(format_d_script)
    logger_debag_3.addHandler(log_d_3)
    logger_debag_4 = logging.getLogger('debag_4')
    log_d_4 = logging.FileHandler('.log/debag_log_4.log')
    logger_debag_4.setLevel(logging.DEBUG)
    format_d_script = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(stend)s -  %(sn)s  -  %(place)s  -  %(funcName)s: %(message)s",
        '%Y-%m-%d %H:%M:%S')
    log_d_4.setFormatter(format_d_script)
    logger_debag_4.addHandler(log_d_4)
    logger_debag_5 = logging.getLogger('debag_5')
    log_d_5 = logging.FileHandler('.log/debag_log_5.log')
    logger_debag_5.setLevel(logging.DEBUG)
    format_d_script = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(stend)s -  %(sn)s  -  %(place)s  -  %(funcName)s: %(message)s",
        '%Y-%m-%d %H:%M:%S')
    log_d_5.setFormatter(format_d_script)
    logger_debag_5.addHandler(log_d_5)
    # log_info stend
    logger_stend = logging.getLogger('stend')
    log_i_stend = logging.FileHandler('.log/log_stend.log')
    logger_stend.setLevel(logging.INFO)
    format_i_stend = logging.Formatter("%(asctime)s - %(levelname)s - %(stend)s - %(message)s", '%Y-%m-%d %H:%M:%S')
    log_i_stend.setFormatter(format_i_stend)
    logger_stend.addHandler(log_i_stend)
    # log_info script
    logger_script = logging.getLogger('script')
    log_i_script = logging.FileHandler('.log/log_script.log')
    logger_script.setLevel(logging.INFO)
    format_i_script = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(stend)s -  %(sn)s  -  %(place)s  -  %(funcName)s: %(message)s",
        '%Y-%m-%d %H:%M:%S')
    log_i_script.setFormatter(format_i_script)
    logger_script.addHandler(log_i_script)
    stend = 'СТЕНД_ПСИ'

    devices = {}
    for i in range(int(board_count)):
        devices[f'device{i}'] = params['router_template'].copy()
    i = 0
    for item in devices.items():
        item[1]['port'] = 231 + i
        i += 1

    device_list = []
    for i in range(len(devices)):
        device_list.append(devices[f'device{i}'])

    try:
        logger_stend.info('Получении ip хоста...', extra={'stend': f'{stend}'})
        netplan_config_name = os.listdir('/etc/netplan')[0]
        netplan_config_file = f'/etc/netplan/{netplan_config_name}'
        with open(netplan_config_file) as f:
            params_netplan = yaml.safe_load(f)
    except CustomError as e:
        logger_stend.error(e)
        sys.exit()
    logger_stend.info('Ip хоста успешно получен...', extra={'stend': f'{stend}'})

    output_file.write('Проверка подключения к БД...\n')
    output_file.flush()
    logger_stend.info('Проверка подключения к БД...', extra={'stend': f'{stend}'})
    try:
        test_connection = engine.connect()
    except OperationalError:
        logger_stend.error(f'Не удается подключиться к базе MAC адресов, выполнение программы невозможно')
        sys.exit()
    test_connection.close()
    logger_stend.info('Подключение к БД успешно!', extra={'stend': f'{stend}'})
    output_file.write('Подключение к БД успешно!\n')
    output_file.flush()

    output_file.write('Включение tcp-to-serial мостов...\n')
    output_file.flush()
    logger_stend.info('Включение tcp-to-serial мостов...', extra={'stend': f'{stend}'})
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        bridge_restart_result = executor.map(tcp_to_serial_bridge_restart_ssh, list(range(1, int(board_count) + 1)))

    # Проверка tftp сервиса
    host_service_check_ssh('tftp')
    # Проверка ftp сервиса
    host_service_check_ssh('vsftp')

    # запуск инсталляции ПО и проверок
    result = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        hw_check_result = executor.map(hw_check, device_list)

    result_list = list(hw_check_result)
    for i in range(len(result_list)):
        result.update(result_list[i])

    # вывод результатов теста на экран
    for dev_num in range(1, len(result) + 1):
        serial_num_board = board_serial_number_list[int(dev_num) - 1]
        place = board_serial_number_list.index(serial_num_board) + 1
        output_file.write(f'\nРезультат для устройства {dev_num}:\n')
        output_file.flush()
        if 'неизвестная ошибка' in result[f'device_num_{dev_num}']['error']:
            output_file.write('>>>Неуспех. Возникла неизвестная ошибка<<<\n')
            output_file.flush()
            logger_script.error('Устройство закончило работу с неизвестной ошибкой',
                                extra={'sn': f'{serial_num_board}', 'stend': f'{stend}', 'place': f'{place}'})
            update_history_db(serial_num_board, 'СТЕНД_ПСИ, плата закончиала работу с неизвестной ошибкой!')
        elif 'Ошибка c устройством' in result[f'device_num_{dev_num}']['error']:
            error_string = result[f'device_num_{dev_num}']['error_details'][0][0]
            output_file.write(f'>>>Неуспех. ПО не было установлено/удалено: {error_string}<<<\n')
            output_file.flush()
            error_code = result[f'device_num_{dev_num}']['error_details'][0][2]
            logger_script.error(f'Устройство закончило работу с ошибкой: {error_string}',
                                extra={'sn': f'{serial_num_board}', 'stend': f'{stend}', 'place': f'{place}'})
            update_history_db(serial_num_board, f'СТЕНД_ПСИ, плата закончиала работу с ошибкой {error_code}!')

        else:
            flash_result = result[f'device_num_{dev_num}']['flash_check_result'][1]
            losses = re.findall(r'\d+% packet loss', result[f'device_num_{dev_num}']['ping_result'])[0]
            if hdd_present:
                ext_slot_out_result = result[f'device_num_{dev_num}']['hdd_check_result'][1]
                ext_slot_in_result = result[f'device_num_{dev_num}']['hdd_check_result'][2]
            elif nmc_ports_count != 0:
                ext_slot_out_result = result[f'device_num_{dev_num}']['nmc_check_result'][1]
            if hdd_present or nmc_ports_count != 0:
                if ext_slot_out_result in ['Внешний HDD найден', 'Все порты NMC модуля найдены'] and \
                        flash_result == 'Flash накопители найдены' and \
                        ext_slot_in_result == 'Внутренний HDD найден' and \
                        losses == '0% packet loss':
                    output_file.write(f'>>>ПСИ успешно пройдено<<< {dev_num}...\n')
                    output_file.flush()
                    update_date_time_pci(engine, serial_num_board)
                    update_history_db(serial_num_board, f'СТЕНД_ПСИ, плата закончиала работу без ошибок!')
                    logger_script.info('Устройство закончило работу без ошибок!',
                                       extra={'sn': f'{serial_num_board}', 'stend': f'{stend}',
                                              'place': f'{place}'})
                else:
                    if ext_slot_out_result in ['Внешний HDD не найден',
                                               'По крайней мере один порт NMC модуля не найден']:
                        error_code = '009'
                    elif flash_result == 'По крайней мере один flash накопитель не определился, возможно, USB порты неисправны':
                        error_code = '090'
                    elif losses == '100% packet loss':
                        error_code = '900'
                    elif ext_slot_out_result in ['Внешний HDD не найден',
                                                 'По крайней мере один порт NMC модуля не найден'] and flash_result == 'По крайней мере один flash накопитель не определился, возможно, USB порты неисправны':
                        error_code = '099'
                    elif ext_slot_out_result in ['Внешний HDD не найден',
                                                 'По крайней мере один порт NMC модуля не найден'] and losses == '100% packet loss':
                        error_code = '909'
                    elif flash_result == 'По крайней мере один flash накопитель не определился, возможно, USB порты неисправны' and losses == '100% packet loss':
                        error_code = '990'
                    elif ext_slot_out_result in ['Внешний HDD не найден',
                                                 'По крайней мере один порт NMC модуля не найден'] and flash_result == 'По крайней мере один flash накопитель не определился, возможно, USB порты неисправны' and losses == '100% packet loss':
                        error_code = '999'

                    output_file.write(f'>>>Неуспех. ПО было установлено, но при проверке АП возникли ошибки<<<\n')
                    output_file.write(f'Результат проверки слота расширения: {ext_slot_out_result}, {ext_slot_in_result}\n')
                    output_file.write(f'Результат проверки USB портов: {flash_result}\n')
                    output_file.write(f'Результат проверки Ethernet портов: {losses}\n')
                    update_history_db(serial_num_board, f'СТЕНД_ПСИ, плата закончиала работу с ошибкой {error_code}!')
                    logger_script.error(
                        f'Устройство закончило работу с ошибками АП: {ext_slot_out_result}, {ext_slot_in_result}, {flash_result}, {losses}', extra={'sn': f'{serial_num_board}', 'stend': f'{stend}', 'place': f'{place}'})
            else:
                if flash_result == 'Flash накопители найдены' and \
                        losses == '0% packet loss':
                    output_file.write(f'Лох\n')
                else:
                    output_file.write('>>>Неуспех. ПО было установлено, но при проверке АП возникли ошибки<<<\n')
                    output_file.write(f'Результат проверки USB портов: {flash_result}\n')
                    output_file.write(f'Результат проверки Ethernet портов: {losses}\n')
                    output_file.flush()
        # запись сырых результатов в файл
    current_time = str(datetime.now())[:-7].replace(':', '-')
    with open(f'logs_pci/raw_results-{current_time}.yaml', 'w') as f:
        f.write(yaml.dump(result, allow_unicode=True))

    logger_stend.removeHandler(log_i_stend)
    logger_script.removeHandler(log_i_script)
    logger_debag_1.removeHandler(log_d_1)
    logger_debag_2.removeHandler(log_d_2)
    logger_debag_3.removeHandler(log_d_3)
    logger_debag_4.removeHandler(log_d_4)
    logger_debag_5.removeHandler(log_d_5)

    output_file.close()
