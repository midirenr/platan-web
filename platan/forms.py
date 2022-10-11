from django import forms
from .models import DeviceType, ModificationType, GenerateSerialNumbers
from django.core.exceptions import ValidationError
from .programs.db_2000 import *
from .programs.db_history import *


class HistoryForm(forms.Form):
    serial_number = forms.CharField(label='', max_length=14)
    
    def clean(self):
        super(HistoryForm, self).clean()

        serial_number = self.cleaned_data['serial_number']

        if len(serial_number) != 14:
            self.errors['serial_number'] = self.error_class(['Некорректный серийный номер'])
            return self.cleaned_data

        if not check_sn(engine, serial_number):
            self.errors['device_serial_number'] = self.error_class([f'{serial_number} отсутствует в Базе Данных"'])
            return self.cleaned_data
        return self.cleaned_data

class GenerateSerialNumbersForm(forms.ModelForm):
    """
    def __init__(self):
        super(GenerateSerialNumbersForm, self).__init__()
        self.fields['device_type'].label = 'Тип устройства'
        self.fields['device_type'].empty_label = 'Выберите устройство'

        self.fields['modification_type'].label = 'Тип модификации'
        self.fields['modification_type'].empty_label = 'Выберите модификацию'

        self.fields['detail_type'].label = 'Тип детали'
        self.fields['detail_type'].empty_label = 'Выберите деталь'

        self.fields['place_of_production'].label = 'Место производства'
        self.fields['place_of_production'].empty_label = 'Выберите место'

        self.fields['count'].label = 'Количество'

        self.fields['modification_type'].queryset = ModificationType.objects.none()
    """

    class Meta:
        model = GenerateSerialNumbers
        fields = '__all__'

        labels = {
            'device_type': 'Тип устройства',
            'modification_type': 'Тип модификации',
            'detail_type': 'Тип детали',
            'place_of_production': 'Место производства',
            'count': 'Количество',
        }


class ChainBoardCase(forms.Form):
    board_serial_number = forms.CharField(label='', max_length=14)
    case_serial_number = forms.CharField(label='', max_length=14)

    def clean(self):
        super(ChainBoardCase, self).clean()

        board_serial_number = self.cleaned_data.get('board_serial_number')
        case_serial_number = self.cleaned_data.get('case_serial_number')

        board_list = []
        case_list = []
        cut_board = board_serial_number[4:6]
        cut_case = case_serial_number[4:6]

        """if len(board_serial_number) < 14:
            self._errors['board_serial_number'] = self.error_class(['Неправильно указан серийный номер платы'])
        elif 'RS' not in board_serial_number[0:2:]:
            self._errors['board_serial_number'] = self.error_class(['Неправильно указан серийный номер платы'])"""

        if cut_board == '20':
            if cut_case == '10':
                if board_serial_number == case_serial_number:
                    self.errors['case_serial_number'] = self.error_class([f'Серийные номера платы и корпуса одинаковые!\nОтсканируйте заново'])
                else:
                    if len(board_serial_number) == 14:
                        check = check_sn_b(engine, board_serial_number)
                        if check:
                            self._errors['board_serial_number'] = self.error_class([f'Серийного номера {board_serial_number} нет в Базе Данных.\nОтсканируйте заново, в проивном случае верните плату на стенд диагностики.'])
                        else:
                            status = check_diag(engine, board_serial_number)
                            if str(status) == 'False':
                                self._errors['board_serial_number'] = self.error_class([f'Плата с серийным номером {board_serial_number} не прошла дигностику!\nВерните плату на стенд диагностики!'])
                            else:
                                board_list.append(board_serial_number)
                    else:
                        self._errors['board_serial_number'] = self.error_class([f'Серийный номер платы {board_serial_number} некорректный!\nОтсканируйте заново!'])

                    if len(board_list) == 1:
                        if len(case_serial_number) == 14:
                            check = check_sn_r(engine, case_serial_number)
                            if not check:
                                self.errors['case_serial_number'] = self.error_class([f'Серийный номер корпуса {case_serial_number} уже есть в БД!\nОтсканируйте заново!'])
                            else:
                                case_list.append(case_serial_number)
                        else:
                            self.errors['case_serial_number'] = self.error_class([f'Серийный номер корпуса {case_serial_number} некорректный! Отсканируйте заново!'])
                    else:
                        pass
            else:
                self.errors['case_serial_number'] = self.error_class([f'Серийный номер корпуса {case_serial_number} не соответствует серийному номеру корпуса!'])
        else:
            self.errors['board_serial_number'] = self.error_class([f'Серийный номер платы {board_serial_number} не соответствует серийному номеру платы!'])

        return self.cleaned_data


class StandPackage(forms.Form):
    device_serial_number = forms.CharField(label='', max_length=14)

    def clean(self):
        super(StandPackage, self).clean()

        device_serial_number = self.cleaned_data['device_serial_number']

        cut_device = device_serial_number[4:6]

        if cut_device == '10':
            if len(device_serial_number) == 14:
                check = check_sn_r(engine, device_serial_number)
                if check:
                    self.errors['device_serial_number'] = self.error_class([f'Серийный номер устройства {device_serial_number} отсутствует в Базе Данных"\nОтсканируйте заново.'])
                else:
                    date = check_date_time_pci(engine, device_serial_number)
                    if date == 'No':
                        self.errors['device_serial_number'] = self.error_class([f'Устройство с серийным номером {device_serial_number} не прошло ПСИ!\nПередайте устройство на стенд ПСИ!'])
            else:
                self.errors['device_serial_number'] = self.error_class([f'Серийный номер устройства некорректный!\nОтсканируйте заново!'])
        else:
            self.errors['device_serial_number'] = self.error_class([f'Серийный номер устройства {device_serial_number} не соответствует серийному номеру устройства!\nОтсканируйте повторно!'])

        return self.cleaned_data


class StandVisualInspection(forms.Form):
    board_serial_number = forms.CharField(label='', max_length=14)

    def clean(self):
        super(StandVisualInspection, self).clean()

        board_serial_number = self.cleaned_data['board_serial_number']

        if len(board_serial_number) == 14:
            if board_serial_number[4:6] == '20':
                if check_board_count(engine, board_serial_number):
                    self.errors['board_serial_number'] = self.error_class([f'Плата с серийным номером {board_serial_number} уже есть в Базе Данных!'])
            else:
                self.errors['board_serial_number'] = self.error_class([f'Серийный номер указан неправильно! Отсканируйте повторно.'])
        else:
            self.errors['board_serial_number'] = self.error_class([f'Серийный номер указан неправильно! Отсканируйте повторно.'])

        return self.cleaned_data


class StandDiagnostic(forms.Form):
    CHOICES_COUNT = zip(range(1,6), range(1, 6))
    CHOICES_TYPE = (
        ('RS', 'Сервисный маршрутизатор'),
        ('RB', 'Граничный маршрутизатор'),
    )

    diagnostic_device_type = forms.ChoiceField(choices=CHOICES_TYPE)
    board_count = forms.ChoiceField(choices=CHOICES_COUNT)
    # board_serial_number_1 = forms.CharField(max_length=14)
    board_serial_number_1 = forms.CharField(widget=forms.TextInput(), max_length=14)
    board_serial_number_2 = forms.CharField(widget=forms.TextInput(
        attrs={
            'maxlength': '14',
        }), required=False)
    board_serial_number_3 = forms.CharField(widget=forms.TextInput(
        attrs={
            'maxlength': '14',
        }), required=False)
    board_serial_number_4 = forms.CharField(widget=forms.TextInput(
        attrs={
            'maxlength': '14',
        }), required=False)
    board_serial_number_5 = forms.CharField(widget=forms.TextInput(
        attrs={
            'maxlength': '14',
        }), required=False)

    output = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'resize:none;',
        'readonly': True,
    }), required=False)

    def clean(self):
        super(StandDiagnostic, self).clean()

        board_count = self.cleaned_data['board_count']

        board_serial_number_1 = self.cleaned_data['board_serial_number_1']
        board_serial_number_2 = self.cleaned_data['board_serial_number_2']
        board_serial_number_3 = self.cleaned_data['board_serial_number_3']
        board_serial_number_4 = self.cleaned_data['board_serial_number_4']
        board_serial_number_5 = self.cleaned_data['board_serial_number_5']

        if board_count == '1':
            if len(board_serial_number_1) == 14:
                if board_serial_number_1[4:6] == '20':
                    if check_board_in_db(engine, board_serial_number_1) == 0:
                        self.errors['board_serial_number_1'] = self.error_class([f'Плата с серийным номером {board_serial_number_1} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                else:
                    self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        elif board_count == '2':
            if len(board_serial_number_1) == 14:
                if board_serial_number_1[4:6] == '20':
                    if check_board_in_db(engine, board_serial_number_1) == 0:
                        self.errors['board_serial_number_1'] = self.error_class([f'Плата с серийным номером {board_serial_number_1} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                else:
                    self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_2) == 14:
                if board_serial_number_1 != board_serial_number_2:
                    if board_serial_number_2[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_2) == 0:
                            self.errors['board_serial_number_2'] = self.error_class([f'Плата с серийным номером {board_serial_number_2} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        elif board_count == '3':
            if len(board_serial_number_1) == 14:
                if board_serial_number_1[4:6] == '20':
                    if check_board_in_db(engine, board_serial_number_1) == 0:
                        self.errors['board_serial_number_1'] = self.error_class([f'Плата с серийным номером {board_serial_number_1} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                else:
                    self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_2) == 14:
                if board_serial_number_2 != board_serial_number_1:
                    if board_serial_number_2[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_2) == 0:
                            self.errors['board_serial_number_2'] = self.error_class([f'Плата с серийным номером {board_serial_number_2} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_3) == 14:
                if board_serial_number_3 != board_serial_number_1 and board_serial_number_3 != board_serial_number_2:
                    if board_serial_number_3[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_3) == 0:
                            self.errors['board_serial_number_3'] = self.error_class([f'Плата с серийным номером {board_serial_number_3} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_3'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        elif board_count == '4':
            if len(board_serial_number_1) == 14:
                if board_serial_number_1[4:6] == '20':
                    if check_board_in_db(engine, board_serial_number_1) == 0:
                        self.errors['board_serial_number_1'] = self.error_class([f'Плата с серийным номером {board_serial_number_1} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                else:
                    self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_2) == 14:
                if board_serial_number_2 != board_serial_number_1:
                    if board_serial_number_2[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_2) == 0:
                            self.errors['board_serial_number_2'] = self.error_class([f'Плата с серийным номером {board_serial_number_2} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_3) == 14:
                if board_serial_number_3 != board_serial_number_1 and board_serial_number_3 != board_serial_number_2:
                    if board_serial_number_3[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_3) == 0:
                            self.errors['board_serial_number_3'] = self.error_class([f'Плата с серийным номером {board_serial_number_3} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_3'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_4) == 14:
                if board_serial_number_4 != board_serial_number_1 and board_serial_number_4 != board_serial_number_2 and board_serial_number_4 != board_serial_number_3:
                    if board_serial_number_4[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_4) == 0:
                            self.errors['board_serial_number_4'] = self.error_class([f'Плата с серийным номером {board_serial_number_4} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_4'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_4'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_4'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        elif board_count == '5':
            if len(board_serial_number_1) == 14:
                if board_serial_number_1[4:6] == '20':
                    if check_board_in_db(engine, board_serial_number_1) == 0:
                        self.errors['board_serial_number_1'] = self.error_class([f'Плата с серийным номером {board_serial_number_1} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                else:
                    self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['board_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_2) == 14:
                if board_serial_number_2 != board_serial_number_1:
                    if board_serial_number_2[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_2) == 0:
                            self.errors['board_serial_number_2'] = self.error_class([f'Плата с серийным номером {board_serial_number_2} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_3) == 14:
                if board_serial_number_3 != board_serial_number_1 and board_serial_number_3 != board_serial_number_2:
                    if board_serial_number_3[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_3) == 0:
                            self.errors['board_serial_number_3'] = self.error_class([f'Плата с серийным номером {board_serial_number_3} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_3'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_3'] = self.error_class(
                    [f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_4) == 14:
                if board_serial_number_4 != board_serial_number_1 and board_serial_number_4 != board_serial_number_2 and board_serial_number_4 != board_serial_number_3:
                    if board_serial_number_4[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_4) == 0:
                            self.errors['board_serial_number_4'] = self.error_class([f'Плата с серийным номером {board_serial_number_4} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_4'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_4'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_4'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(board_serial_number_5) == 14:
                if board_serial_number_5 != board_serial_number_1 and board_serial_number_5 != board_serial_number_2 and board_serial_number_5 != board_serial_number_3 and board_serial_number_5 != board_serial_number_4:
                    if board_serial_number_5[4:6] == '20':
                        if check_board_in_db(engine, board_serial_number_5) == 0:
                            self.errors['board_serial_number_5'] = self.error_class([f'Плата с серийным номером {board_serial_number_5} отсутствует в Базе Данных!\nПередайте плату на стенд визуального осмотра.'])
                    else:
                        self.errors['board_serial_number_5'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['board_serial_number_5'] = self.error_class([f'Серийный номер платы совпадает с другим серийным номером!'])
            else:
                self.errors['board_serial_number_5'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        return self.cleaned_data


class StandPCI(forms.Form):
    CHOICES_COUNT = zip(range(1,6), range(1, 6))
    CHOICES_TYPE = (
        ('RS', 'Сервисный маршрутизатор'),
        ('RB', 'Граничный маршрутизатор'),
    )

    pci_device_type = forms.ChoiceField(choices=CHOICES_TYPE)
    router_count = forms.ChoiceField(choices=CHOICES_COUNT)
    router_serial_number_1 = forms.CharField(widget=forms.TextInput(), max_length=14)
    router_serial_number_2 = forms.CharField(widget=forms.TextInput(
        attrs={
            'maxlength': '14',
        }), required=False)
    router_serial_number_3 = forms.CharField(widget=forms.TextInput(
        attrs={
            'maxlength': '14',
        }), required=False)
    router_serial_number_4 = forms.CharField(widget=forms.TextInput(
        attrs={
            'maxlength': '14',
        }), required=False)
    router_serial_number_5 = forms.CharField(widget=forms.TextInput(
        attrs={
            'maxlength': '14',
        }), required=False)

    output = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'resize:none;',
        'readonly': True,
    }), required=False)

    def clean(self):
        super(StandPCI, self).clean()

        router_count = self.cleaned_data['router_count']

        router_serial_number_1 = self.cleaned_data['router_serial_number_1']
        router_serial_number_2 = self.cleaned_data['router_serial_number_2']
        router_serial_number_3 = self.cleaned_data['router_serial_number_3']
        router_serial_number_4 = self.cleaned_data['router_serial_number_4']
        router_serial_number_5 = self.cleaned_data['router_serial_number_5']

        if router_count == '1':
            if len(router_serial_number_1) == 14:
                if router_serial_number_1[4:6] == '10':
                    if check_sn_r(engine, router_serial_number_1) == True:
                        self.errors['router_serial_number_1'] = self.error_class([f'Устройство с серийным номером {router_serial_number_1} отсутствует в Базе Данных!\nОтсканируйте заново.'])
                else:
                    self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        elif router_count == '2':
            if len(router_serial_number_1) == 14:
                if router_serial_number_1[4:6] == '10':
                    if check_sn_r(engine, router_serial_number_1) == 0:
                        self.errors['router_serial_number_1'] = self.error_class([f'Устройство с серийным номером {router_serial_number_1} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_2) == 14:
                if router_serial_number_1 != router_serial_number_2:
                    if router_serial_number_2[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_2) == 0:
                            self.errors['router_serial_number_2'] = self.error_class([f'Устройство с серийным номером {router_serial_number_2} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер устройства совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        elif router_count == '3':
            if len(router_serial_number_1) == 14:
                if router_serial_number_1[4:6] == '10':
                    if check_sn_r(engine, router_serial_number_1) == 0:
                        self.errors['router_serial_number_1'] = self.error_class([f'Устройство с серийным номером {router_serial_number_1} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_2) == 14:
                if router_serial_number_2 != router_serial_number_1:
                    if router_serial_number_2[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_2) == 0:
                            self.errors['router_serial_number_2'] = self.error_class([f'Устройство с серийным номером {router_serial_number_2} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер устройства совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_3) == 14:
                if router_serial_number_3 != router_serial_number_1 and router_serial_number_3 != router_serial_number_2:
                    if router_serial_number_3[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_3) == 0:
                            self.errors['router_serial_number_3'] = self.error_class([f'Устройство с серийным номером {router_serial_number_3} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_3'] = self.error_class([f'Серийный номер устройства совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        elif router_count == '4':
            if len(router_serial_number_1) == 14:
                if router_serial_number_1[4:6] == '10':
                    if check_sn_r(engine, router_serial_number_1) == 0:
                        self.errors['router_serial_number_1'] = self.error_class([f'Устройство с серийным номером {router_serial_number_1} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_2) == 14:
                if router_serial_number_2 != router_serial_number_1:
                    if router_serial_number_2[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_2) == 0:
                            self.errors['router_serial_number_2'] = self.error_class([f'Устройство с серийным номером {router_serial_number_2} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер устройства совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_3) == 14:
                if router_serial_number_3 != router_serial_number_1 and router_serial_number_3 != router_serial_number_2:
                    if router_serial_number_3[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_3) == 0:
                            self.errors['router_serial_number_3'] = self.error_class([f'Устройство с серийным номером {router_serial_number_3} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_3'] = self.error_class([f'Серийный номер устройства совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_4) == 14:
                if router_serial_number_4 != router_serial_number_1 and router_serial_number_4 != router_serial_number_2 and router_serial_number_4 != router_serial_number_3:
                    if router_serial_number_4[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_4) == 0:
                            self.errors['router_serial_number_4'] = self.error_class([f'Устройство с серийным номером {router_serial_number_4} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_4'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_4'] = self.error_class([f'Серийный номер устройства совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_4'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        elif router_count == '5':
            if len(router_serial_number_1) == 14:
                if router_serial_number_1[4:6] == '10':
                    if check_sn_r(engine, router_serial_number_1) == 0:
                        self.errors['router_serial_number_1'] = self.error_class([f'Устройство с серийным номером {router_serial_number_1} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
            else:
                self.errors['router_serial_number_1'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_2) == 14:
                if router_serial_number_2 != router_serial_number_1:
                    if router_serial_number_2[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_2) == 0:
                            self.errors['router_serial_number_2'] = self.error_class([f'Устройство с серийным номером {router_serial_number_2} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер устройства совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_2'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_3) == 14:
                if router_serial_number_3 != router_serial_number_1 and router_serial_number_3 != router_serial_number_2:
                    if router_serial_number_3[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_3) == 0:
                            self.errors['router_serial_number_3'] = self.error_class([f'Устройство с серийным номером {router_serial_number_3} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_3'] = self.error_class([f'Серийный номер устройство совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_3'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_4) == 14:
                if router_serial_number_4 != router_serial_number_1 and router_serial_number_4 != router_serial_number_2 and router_serial_number_4 != router_serial_number_3:
                    if router_serial_number_4[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_4) == 0:
                            self.errors['router_serial_number_4'] = self.error_class([f'Устройство с серийным номером {router_serial_number_4} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_4'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_4'] = self.error_class([f'Серийный номер устройства совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_4'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

            if len(router_serial_number_5) == 14:
                if router_serial_number_5 != router_serial_number_1 and router_serial_number_5 != router_serial_number_2 and router_serial_number_5 != router_serial_number_3 and router_serial_number_5 != router_serial_number_4:
                    if router_serial_number_5[4:6] == '10':
                        if check_sn_r(engine, router_serial_number_5) == 0:
                            self.errors['router_serial_number_5'] = self.error_class([f'Устройство с серийным номером {router_serial_number_5} отсутствует в Базе Данных!\nОтсканируйте повторно.'])
                    else:
                        self.errors['router_serial_number_5'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])
                else:
                    self.errors['router_serial_number_5'] = self.error_class([f'Серийный номер устройства совпадает с другим серийным номером!'])
            else:
                self.errors['router_serial_number_5'] = self.error_class([f'Серийный номер указан неправильно!\nОтсканируйте повторно.'])

        return self.cleaned_data
