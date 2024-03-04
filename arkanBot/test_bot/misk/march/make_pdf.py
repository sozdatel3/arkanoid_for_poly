from PIL import Image
from reportlab.pdfgen import canvas
import os

# Путь к папке с изображениями
image_folder = './'

# Названия для PDF файлов
pdf_names = ['карьера', 'финансы', 'отношения']

# Функция для создания PDF
def create_pdf(image_paths, pdf_name):
    c = canvas.Canvas(pdf_name, pagesize=(595.27, 841.89))  # Размер страницы A4 в точках
    for image_path in image_paths:
        c.drawImage(image_path, 0, 0, 595.27, 841.89)  # Размер изображения подогнан под размер страницы A4
        c.showPage()
    c.save()

# Основной цикл для создания PDF файлов
for i in range(3, 69):  # Перебираем все изображения начиная с 3.png до 68.png
    base_images = [os.path.join(image_folder, '1.png'), os.path.join(image_folder, '2.png')]
    current_image = os.path.join(image_folder, f'{i}.png')
    image_paths = base_images + [current_image]
    pdf_index = (i - 3) // 3 + 1
    pdf_name = f"{pdf_index}_{pdf_names[(i - 3) % 3]}.pdf"
    create_pdf(image_paths, pdf_name)

print("PDF файлы успешно созданы!")