# import os
# from PyPDF2 import PdfReader, PdfWriter


# def do_pdf(new_names):
#     # Путь к файлу предисловия и папке с PDF-файлами
#     preface_file = "firs.pdf"
#     folder_path = "ilovepdf_split"

#     # Чтение файла предисловия
#     preface = PdfReader(preface_file)

#     # Обход всех PDF-файлов в папке
#     i = 0
#     right_list_of_files = os.listdir(folder_path)
#     # Сортируем сначала по длине строки, затем лексикографически
#     sorted_files = sorted(right_list_of_files, key=lambda x: (len(x), x))
#     print(sorted_files)
#     for pdf_file in sorted_files:
#         if pdf_file.endswith(".pdf") and pdf_file != "предисловие.pdf":
#             # Создание объекта для нового PDF
#             new_pdf = PdfWriter()

#             # Добавление предисловия
#             for page in range(len(preface.pages)):
#                 new_pdf.add_page(preface.pages[page])

#             # Чтение и добавление оригинального файла
#             original_pdf = PdfReader(os.path.join(folder_path, pdf_file))
#             for page in range(len(original_pdf.pages)):
#                 new_pdf.add_page(original_pdf.pages[page])

#             # Запись нового файла
#             # with open(os.path.join(folder_path, f"new_{pdf_file}"), "wb") as new_file:
#             with open(os.path.join(folder_path, f"{new_names[i]}"), "wb") as new_file:
#                 i += 1
#                 new_pdf.write(new_file)


# def get_filenames(folder_path, file_list):
#     """
#     Функция для заполнения списка file_list названиями файлов из папки folder_path.

#     Args:
#     folder_path (str): Путь к папке.
#     file_list (list): Список для заполнения названиями файлов.
#     """
#     # Проверка, что указанный путь действительно является папкой
#     if not os.path.isdir(folder_path):
#         print(f"Путь '{folder_path}' не является папкой.")
#         return

#     # Получение и добавление названий файлов в список
#     for filename in os.listdir(folder_path):
#         # Полный путь к файлу
#         full_path = os.path.join(folder_path, filename)
#         # Добавляем только если это файл, не папка
#         if os.path.isfile(full_path) and full_path.endswith("pdf"):
#             file_list.append(filename)


# import re


# def extract_number(filename):
#     """
#     Извлекает число из начала имени файла.

#     Args:
#     filename (str): Имя файла.

#     Returns:
#     int: Извлеченное число или очень большое число, если число отсутствует.
#     """
#     match = re.match(r"\d+", filename)
#     return int(match.group()) if match else float("inf")


# # filenames = ['17_ЗВЕЗДА.pdf', '7_КОЛЕСНИЦА.pdf', 'firs.pdf', '22_ШУТ.pdf', '9_ОТШЕЛЬНИК.pdf',
# #              '5_ИЕРОФАНТ.pdf', '16_БАШНЯ.pdf', '3_ИМПЕРАТРИЦА.pdf', '11_СИЛА.pdf', '14_УМЕРЕННОСТЬ.pdf',
# #              '10_КОЛЕСО_ФОРТУНЫ.pdf', '15_ДЬЯВОЛ.pdf', '13_СМЕРТЬ.pdf', '2_ЖРИЦА.pdf', '12_ПОВЕШЕННЫЙ.pdf',
# #              '19_СОЛНЦЕ.pdf', '20_СУД.pdf', '18_ЛУНА.pdf', '4_ИМПЕРАТОР.pdf', '1_МАГ.pdf', '21_МИР.pdf',
# #              '8_СПРАВЕДЛИВОСТЬ.pdf', '6_ВЛЮБЛЕННЫЕ.pdf']


# # print(sorted_filenames)
# def make_dirty_names():
#     list = []
#     get_filenames("./", list)
#     print(list)
#     sorted_filenames = sorted(list, key=extract_number)
#     print(sorted_filenames)
#     modified_list = [
#         f"{filename.split('.')[0]}_{i}.pdf"
#         for filename in sorted_filenames
#         for i in range(3)
#     ]
#     print(modified_list)
#     do_pdf(modified_list)


# make_dirty_names()
import os
from PyPDF2 import PdfReader, PdfWriter

# Путь к папке с файлами PDF
directory = "misk"

# Путь к файлу, страницу из которого нужно вставить
second_page_file = "second_page.pdf"

# Чтение страницы, которую нужно вставить
second_page_reader = PdfReader(second_page_file)
second_page = second_page_reader.pages[0]

# Проход по всем PDF-файлам в папке
for filename in os.listdir(directory):
    if filename.endswith(".pdf"):
        file_path = os.path.join(directory, filename)

        # Создание объекта PdfReader для чтения текущего файла
        pdf_reader = PdfReader(file_path)
        pdf_writer = PdfWriter()

        # Копирование всех страниц, кроме второй, в новый файл
        for page in range(len(pdf_reader.pages)):
            if page == 1:  # Вторая страница в PDF имеет индекс 1
                pdf_writer.add_page(second_page)
            else:
                pdf_writer.add_page(pdf_reader.pages[page])

        # Сохранение изменённого файла
        with open(file_path, "wb") as output_file:
            pdf_writer.write(output_file)
