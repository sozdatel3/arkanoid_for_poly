import PyPDF2


def split_pdf(source_pdf):
    # Открыть исходный PDF файл
    with open(source_pdf, 'rb') as infile:
        reader = PyPDF2.PdfReader(infile)
        number_of_pages = len(reader.pages)

        # Перебрать страницы, начиная с третьей (индекс 2, т.к. индексация начинается с 0)
        for i in range(2, number_of_pages):
            writer = PyPDF2.PdfWriter()

            # Добавить первые две страницы (заголовочные)
            writer.add_page(reader.pages[0])
            writer.add_page(reader.pages[1])

            # Добавить текущую страницу
            writer.add_page(reader.pages[i])

            # Сформировать имя для нового файла
            output_filename = f"{i-1}.pdf"

            # Записать новый PDF файл
            with open(output_filename, 'wb') as outfile:
                writer.write(outfile)


# Пример использования:
# Укажи путь к исходному PDF файлу
source_pdf = 'sphere.pdf'
# Укажи директорию, куда будут сохранены новые PDF файлы
# output_directory = 'path_to_your_output_directory'

split_pdf(source_pdf)
