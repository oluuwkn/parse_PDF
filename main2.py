import pdfplumber #точное извлечение текста, табилц и метаданныъ из PDF
import os #для работы с ос
import re #моджуль для работы с регулярными выражениями. поиск, измнение и проверка текста по сложным шаблонам
import pandas as pd #таблицы и текст
from pydantic import BaseModel #строгая структура данных. проверка данных для питона. basmodel - базовый класс для создания, проверки и преобразования структур. данных


#структура данных
class GearModel(BaseModel):
    model_name: str    #имя
    voltage_v: float   #напряжение
    torque_nm: float   #крутящий момент

#сохраненеие в Excel

def save_to_excel(gear_list: list[GearModel], output_file: str = "gears_catalog.xlsx"):    #список объектов pandas в эксель таблицу
    "Список объектов преобразуется в Excel-таблицу"
    if not gear_list:
        print("Нечего сохранять!")
        return

    data = [gear.model_dump() for gear in gear_list]   #преобразование списка объектов в список обычных словарей. model_dump() берет каждый объект gearsmodel и превращает
                                                                                                                                                        #его в обычгый словарь

    df = pd.DataFrame(data)   #создание таблицы

    #переименовывание колонок на русский язык для удобства

    df.rename(columns={ 
        'model_name': 'Модель привода',
        'voltage_v': 'Напряжение (В)',
        'torque_nm': 'Крутящий момент (Нм)'
    }, inplace=True)

    #сохранение в эксель 
    df.to_excel(output_file, index=False)
    full_path = os.path.abspath(output_file) #полный путь к файлу
    print(f"Данные сохранены в файл: {full_path}")


#основная функция. текстовый парсинг
def parse_gear_text(pdf_path: str, page_number: int):
    print(f"Открывается файл {pdf_path}, страница {page_number + 1}")
    #открытие файла и извлечение текста
    try:
        with pdfplumber.open(pdf_path) as pdf: 
            page = pdf.pages[page_number]
            text = page.extract_text()

            if not text:
                print("ОШИБКА: Текст не найден!")
                return
            
            #регулярное выражение - RegEx. поиск строго по шаблону. формула по моему примерному PDF-файлу
            #(PDF или PDS) + пробел + (2 цифры момента) + слеш + (2 или 3 цифры напряжения) + точка + (буквы)
            pattern = r'(PDF|PDS)\s+(\d{2})/(\d{2,3})\.([A-Z\-]+)'
            
            #поиск совпадений в тексте
            matches = re.finditer(pattern, text)

            #парсинг сведений и заполнение списка
            results = []
            
            for match in matches:
                full_model = match.group(0) 
                torque_str = match.group(2) 
                voltage_str = match.group(3) 
                
                try:
                    drive = GearModel( #экземпляр модели GearModel
                        model_name=full_model,
                        voltage_v=float(voltage_str),
                        torque_nm=float(torque_str) 
                    )
                    results.append(drive)
                except Exception as e:
                    print(f"Сбой на модели {full_model}: {e}")

            return results
            
    #обработка ошибок
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")

#запуск
if __name__ == "__main__":
    my_file = "catalog.pdf" 
    target_page = 0  #начальная страница
    
    #запуск парсера
    gears = parse_gear_text(my_file, target_page)

    #сохранение в эксель
    if gears:
        save_to_excel(gears)
    else: 
        print("Список пуст, файл не создан!")