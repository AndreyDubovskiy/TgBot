import pandas as pd
import db.database as db

# # Загрузка данных из файла Excel
# df = pd.read_excel('test.xlsx')
#
# # Проход по каждой строке
# for index, row in df.iterrows():
#     # index содержит номер строки
#     # row содержит данные строки
#     if index > 1:
#         print(f"Строка {index}:")
#         print(row.get("ЗАГАЛЬНА ІНФОРМАЦІЯ", "Нема"),
#               row.get("Unnamed: 2", "Нема"),
#               row.get("КОНТАКТНІ ДАНІ", "Нема"),
#               )
#         name = str(row.get("ЗАГАЛЬНА ІНФОРМАЦІЯ", "Нема")) +" "+ str(row.get("Unnamed: 2", "Нема"))
#         phone = str(row.get("КОНТАКТНІ ДАНІ", "Нема"))
#
#         db.create_user(name, phone)
#     if index > 1867:
#         break


