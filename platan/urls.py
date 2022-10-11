from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-serial-numbers/', views.generate_serial_numbers_page, name='generate-serial-numbers'),
    path('stand-board-case/', views.stand_board_case_page, name='stand-board-case'),
    path('stand-package/', views.stand_package_page, name='stand-package'),
    path('stand-visual-inspection/', views.stand_visual_inspection_page, name='stand-visual-inspection'),
    path('stand-diagnostic/', views.stand_diagnostic_page, name='stand-diagnostic'),
    path('stand-pci/', views.stand_pci_page, name='stand-pci'),
    path('history/', views.hisory_page, name='history'),

    # ajax
    path('ajax/load-modifications/', views.load_modifications, name='ajax_load_modifications'),
    path('ajax/diagnostic-output/', views.diagnostic_load_output, name='ajax_diag_output'),
    path('ajax/pci-output/', views.pci_load_output, name='ajax_pci_output')
]
