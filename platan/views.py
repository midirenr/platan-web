import datetime
from zipfile import ZipFile

from django.http import FileResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from .tests import group_required

from platan.programs.db_2000 import write_serial_num_router

from .models import *
from .forms import *
from .programs import generate_serial_number
from .programs import stand_package
from .programs import psql_chain_board_case
from .programs import stand_visual_inspection
from .programs.db_2000 import *
from .programs.db_history import *
from .programs import stand_diagnostic
from .programs import stand_pci
from .programs.get_host_ip import get_ip

# Create your views here.


def index(request):
    return render(
        request,
        'index.html',
        context=
        {

        },
    )

def hisory_page(request):
    form = HistoryForm()
    if request.method == "POST" and 'submit_btn' in request.POST:
        form = HistoryForm(data=request.POST)
        serial_number = request.POST.get('serial_number')
        history = [(1, 'СТЕНД_ПСИ, плата закончиала работу с неизвестной ошибкой!','25-2-2022 14:23:54'), (2, 'СТЕНД_ПСИ, плата закончиала работу с ошибкой: 999','25-2-2022 15:55:21')]#get_history(serial_number)
        return render(request, 'history.html', context={'history': history, 'form': form})
    return render(request, 'history.html', context={'form': form})

@group_required('Техническое Бюро')
def generate_serial_numbers_page(request):
    form = GenerateSerialNumbersForm()

    if 'submit_btn' in request.POST and request.method == 'POST':
        form = GenerateSerialNumbersForm(data=request.POST)

        if form.is_valid():
            device_type = form.cleaned_data['device_type']
            modification_type = form.cleaned_data['modification_type']
            detail_type = form.cleaned_data['detail_type']
            place_of_production = form.cleaned_data['place_of_production']
            count = form.cleaned_data['count']
            current_time = str(datetime.now())[:-7].replace(' ', '_').replace(':', '-')

            generate_serial_number.generate_serial_numbers(device_type, modification_type, detail_type, place_of_production, count, current_time)

            filename1 = f'SerialNumbers/{device_type}/{modification_type}/{detail_type}/serial_number_for_{modification_type}/{detail_type}({current_time}).txt'
            """
            filename2 = f'QRcode/{device_type}/{modification_type}/{detail_type}/qrcode-{detail_type}-{current_time}/qrcode-{detail_type}-{current_time}.pdf'

            zipObject = ZipFile('СерийныеНомера+QRкоды.zip', 'w')
            zipObject.write(filename1)
            zipObject.write(filename2)
            zipObject.close()
            """

            return FileResponse(open(filename1, 'rb'), as_attachment=True)

    return render(
        request,
        'generate_serial_numbers.html',
        context=
        {
            'form': form,
        },
    )


def load_modifications(request):
    device_type_id = request.GET.get('device_type_id')
    modification_type = ModificationType.objects.filter(device_type_id=device_type_id).all()
    return render(
        request,
        'ajax/modification_dropdown_list_options.html',
        context=
        {
            'modifications': modification_type,
        },
    )


@group_required('Стенд слата-корпус')
def stand_board_case_page(request):
    form = ChainBoardCase()

    if 'submit_btn' in request.POST and request.method == 'POST':
        form = ChainBoardCase(request.POST)

        if form.is_valid():
            print('FORM IS VALID!')
            print(form.cleaned_data['board_serial_number'])
            print(form.cleaned_data['case_serial_number'])

            write_serial_num_router(engine, form.cleaned_data['board_serial_number'], form.cleaned_data['case_serial_number'])

            return redirect('stand-board-case')

    return render(
        request,
        'stand_board_case.html',
        context=
        {
            'form': form,
        },
    )


@group_required('Стенд упаковки')
def stand_package_page(request):
    form = StandPackage()

    if 'submit_btn' in request.POST and request.method == 'POST':
        form = StandPackage(request.POST)

        if form.is_valid():
            print('VALID')
            stickers = stand_package.start_package_process(form.cleaned_data['device_serial_number'])

            return render(request, 'stand-package', context=stickers)

    return render(
        request,
        'stand_package.html',
        context=
        {
            'form': form,
        },
    )


@group_required('Стенд визуального осмотра')
def stand_visual_inspection_page(request):
    form = StandVisualInspection()

    if 'submit_btn_valid' in request.POST and request.method == 'POST':
        form = StandVisualInspection(request.POST)

        if form.is_valid():
            stand_visual_inspection.stand_visual_inspection_valid(form.cleaned_data['board_serial_number'], request.user)

            return redirect('stand-visual-inspection')

    if 'submit_btn_defect' in request.POST and request.method == 'POST':
        form = StandVisualInspection(request.POST)

        if form.is_valid():
            stand_visual_inspection.stand_visual_inspection_defect(form.cleaned_data['board_serial_number'], request.user)

            return redirect('stand-visual-inspection')

    return render(
        request,
        'stand_visual_inspection.html',
        context=
        {
            'form': form,
        },
    )


@group_required('Стенд диагностики')
def stand_diagnostic_page(request):
    form = StandDiagnostic()

    if 'diagnostic_start' in request.POST and request.method == 'POST':
        form = StandDiagnostic(request.POST)

        if form.is_valid():
            board_count = form.cleaned_data['board_count']
            board_serial_number = form.cleaned_data['board_serial_number_1']
            os_modification = 'SP'
            modification_split = board_serial_number[2:4]
            modification_serial_number_os = modification_split + os_modification

            modification_dictionary = {
                '20SP': 'КРПГ.465614.001',
                '31SP': 'КРПГ.465614.001-02',
                '30SP': 'КРПГ.465614.001-03',
                '10SP': 'КРПГ.465614.001-05',
                '41SP': 'КРПГ.465614.001-06',
                '40SP': 'КРПГ.465614.001-07',
                '32SP': 'КРПГ.465614.001-09',
                '33SP': 'КРПГ.465614.001-10',
                '34SP': 'КРПГ.465614.001-11',
                '35SP': 'КРПГ.465614.001-12',
                '42SP': 'КРПГ.465614.001-14',
                '43SP': 'КРПГ.465614.001-15',
                '44SP': 'КРПГ.465614.001-16',
                '45SP': 'КРПГ.465614.001-17',
            }
            modification = modification_dictionary.get(modification_serial_number_os)

            board_serial_number_list = [form.cleaned_data['board_serial_number_1'],
                                        form.cleaned_data['board_serial_number_2'],
                                        form.cleaned_data['board_serial_number_3'],
                                        form.cleaned_data['board_serial_number_4'],
                                        form.cleaned_data['board_serial_number_5']]

            ip = get_ip(request)
            stand_diagnostic.run(board_count, modification, board_serial_number_list, ip)

            return redirect('stand-diagnostic')

    return render(
        request,
        'stand-diagnostic.html',
        context=
        {
            'form': form,
        },
    )


def diagnostic_load_output(request):

    return render(
        request,
        'ajax/diagnostic_output.html',
        context=
        {

        },
    )


@group_required('Стенд ПСИ')
def stand_pci_page(request):
    form = StandPCI()

    if 'pci_start' in request.POST and request.method == 'POST':
        form = StandPCI(request.POST)

        if form.is_valid():
            router_count = form.cleaned_data['router_count']
            router_serial_number = form.cleaned_data['router_serial_number_1']
            os_modification = 'SP'
            modification_split = router_serial_number[2:4]
            modification_serial_number_os = modification_split + os_modification

            modification_dictionary = {
                '20SP': 'КРПГ.465614.001',
                '31SP': 'КРПГ.465614.001-02',
                '30SP': 'КРПГ.465614.001-03',
                '10SP': 'КРПГ.465614.001-05',
                '41SP': 'КРПГ.465614.001-06',
                '40SP': 'КРПГ.465614.001-07',
                '32SP': 'КРПГ.465614.001-09',
                '33SP': 'КРПГ.465614.001-10',
                '34SP': 'КРПГ.465614.001-11',
                '35SP': 'КРПГ.465614.001-12',
                '42SP': 'КРПГ.465614.001-14',
                '43SP': 'КРПГ.465614.001-15',
                '44SP': 'КРПГ.465614.001-16',
                '45SP': 'КРПГ.465614.001-17',
            }
            modification = modification_dictionary.get(modification_serial_number_os)

            router_serial_number_list = [form.cleaned_data['router_serial_number_1'],
                                        form.cleaned_data['router_serial_number_2'],
                                        form.cleaned_data['router_serial_number_3'],
                                        form.cleaned_data['router_serial_number_4'],
                                        form.cleaned_data['router_serial_number_5']]
            ip = get_ip(request)
            stand_pci.run(router_count, modification, router_serial_number_list, ip)

            return redirect('stand-pci')

    return render(
        request,
        'stand-pci.html',
        context=
        {
            'form': form,
        },
    )


def pci_load_output(request):

    return render(
        request,
        'ajax/pci_output.html',
        context=
        {

        },
    )
