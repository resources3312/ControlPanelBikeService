"""

    ПРАКТИЧЕСКАЯ ДЕМОНСТРАЦИЯ ПРИНЦИПА CRUD ORM SQLALCHEMY НА ПРИМЕРЕ ПРИЛОЖЕНИЯ СЕРВИСА АРЕНДЫ
    
    Автор: Дич А.А

    Дата создания: 13-06-2025

    Описание:
        
        Приложение 'Панель управления сервиса аренды' — представляет собой образец программного обеспечения
        для демонстрации студентам принципа CRUD(Create, Read, Update, Delete) с пользовательским интерфейсом,
        созданным с использованием графического фреймворка PyQt6. Архитектура данного приложения построена на
        парадигме ООП, и представляет собой модульную систему позволяющую без значительных метаморфоз вносить
        изменения в отдельные компоменты ПО, не опасаясь за его работоспособность. Также стоит отметить, что в
        исходном коде данного приложения сочетается ряд отличных подходов к написанию кода в рамках объектно-
        ориентированных языков программирования, могут встречаться как эврестические решения задач, так и
        нестандартные методы, заточенные под лаконичность и оптимизацию кода. В комбинации с демонстрацией
        ряда принципов создания качественного пользовательского интерфейса, и построением грамотной архитектуры,
        данный подход является оптимальным для ознакомления студентов с правильными подходами к разработке крупных
        приложений, а также обеспечением корректного взаимодействия ПО с системами управления базами данных.

    
        Документация к классам приложения имеет следующий вид:

        Название класса
        |
        |— Описание класса
        |
        |— Подробная логическая схема класса
        |
        |— Тело класса с пошаговым комментированием операций
        |

        Копирование, распространение и любой другой вид использования данного материала
        разрешен только при указании авторства
"""
from sys import argv
import re
from datetime import datetime
from sqlalchemy.orm import Session, DeclarativeBase, validates
from sqlalchemy import create_engine, exc
from sqlalchemy import Column, Integer, Float, String, CheckConstraint

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction
from PyQt6.QtWidgets import (

QApplication, QMainWindow, QWidget,

QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,

QLabel, QLineEdit, QPushButton, QComboBox, QDockWidget, QListWidget, QTableWidget, QTableWidgetItem,

QDialog, QToolBar, QMessageBox, QStyledItemDelegate
)

class Base(DeclarativeBase):
    """
    Описание
        Класс Base — дочерний класс DeclarativeBase, в парадигме данного приложения
        является объектом, что представляет базу данных инициализированную ниже,
        и наполненную таблицами, которые будут объявлены ниже ввиде обычных классов
        языка программирования Python. Документация данного класса будет лишена структуры,
        по причине отсутствия логики, в нашем случае он представляется
        лишь классом 'заглушкой', от которого будут наследоваться дальнейшие ORM модели
    """
    pass


class BikeModel(Base):
    """
    Описание
        Класс BikeModel — представляет собой дочерний класс Base, является моделью что описывает
        таблицу BikeModel. Данная модель несколько 'урезана' в угоду простоты понимания, однако
        с концептуальной точки зрения отражает структуру аналогичных моделей в базах данных реальных
        сервисов на подобии Yandex, Whoosh и т.д. Структура класса BikeModel представлена ниже

    Структура класса (модели) BikeModel
    |
    |— Атрибут __tablename__, модели BikeModel. Служит для указания названия текущей модели
    |  (таблицы), в нашем случае модель имеет название BikeModel
    |
    |— Атрибут id, хранящий экземпляр класса Column. Является первичным ключом (главным идентификатором модели),
    |  Имеет тип данных Integer и генерируется автоматически
    |
    |— Атрибут bikeId, хранящий экземпляр класса Column. Имеет тип данных String, является уникальным (unique=True)
    |  внутренним идентификатором транспортного средства, не может быть пропущен при добавлении записей (nullable=False)
    |  в таблицу BikeModel, а также имеет кастомный валидатор
    |
    |— Атрибут bikeType, хранящий экземпляр класса Column. Имеет тип данных String, хранит информацию о типе
    |  транспортного средства, не может быть пустым (nullable=False), имеет ограничение под названием bikeTypeValidate
    |
    |— Атрибут mode, хранящий экземпляр класса Column. Имеет тип данных String, хранит данные о текущем режиме работы ТС.
    |  Также не может быть пропущен во время добавления новых значений, и имеет ограничение modeValidate
    |
    |— Атрибут speed, хранящий экземпляр класса Column. Имеет тип данных Integer, хранит значение текущей скорости в (км/ч).
    |  Не может быть пустым (nullable=False), имеет ограничение speedValidate
    |
    |— Атрибут speedLimit, хранящий экземпляр класса Column. Имеет тип данных Integer, хранит значение текущей скорости в (км/ч).
    |  Не может быть пропущен при добавлении новых значений (nullable=False), имеет ограничение speedLimitValidate
    |
    |— Атрибут __table_args__, используется для хранения ограничений таблицы ввиде кортежа. В нашем случае содержит
    |  следующие ограничения:
    |  |
    |  |— Экземпляр класса CheckConstraint, валидирует значения принимаемые атрибутом bikeType, быть точнее на то,
    |  |  содержится ли вводимое значение в кортеже типов ТС
    |  |
    |  |— Экземпляр класса CheckConstraint, валидирует значения вводимые в атрибут mode, на то, содержится ли вводимое значение
    |  |  в кортеже режимов работы ТС
    |  |
    |  |— Экземпляр класса CheckConstraint, валидирует значения добавляемые для атрибута speed. В данном случае используется оператор
    |  |  BETWEEN, что ограничивает диапазон ввводимых значений диапазоном от 0 до 25
    |  |
    |  |— Экземпляр класса CheckConstraint, валидирует значения вводимые в атрибут speedLimit. При валидации происходит проверка на
    |  |  соответствие вводимого значения, значениям внутри кортежа ограничений скорости ТС
    |  |
    |  |— Метод validateBikeId(key: str, bikeId: str)
    |  |  |
    |  |  |— Ветвление (if len(bikeId) == 6 and re.search(...))
    |  |  |  |
    |  |  |  |— Встроенная функция len(bikeId), проверяет длину вводимого в валидатор значения, на равенство 6 символам
    |  |  |  |
    |  |  |  |— Метод search(regex: str),  содержит регулярное выражение, в случае если bikeId содержит цифровые значения (\d),
    |  |  |  |  лишен кириллических символов ([^а-яёА-ЯЁ]), и содержит символы латинского алфавита верхнего регистра ([A-Z])
    |  |  |  |
    |  |  |
    |  |  |— Ответвление (else ValueError(...))
    |  |  |  |
    |  |  |  |— Экземпляр класса исключения ValueError(text: str). В случае нессотвествия значения условиям валидатора возвращаем ValueError
    |  |  |  |
    """
    __tablename__ = "BikeModel"
    id = Column(Integer, primary_key=True, autoincrement=True) # Объявляем первичный ключ модели BikeModel c типом данных Integer
    bikeId = Column(String, nullable=False, unique=True) # Объявляем уникальный атрибут bikeId модели BikeModel c типом данных String
    bikeType = Column(String, nullable=False) # Объявляем атрибут bikeType модели BikeModel c типом данных String
    mode = Column(String, nullable=False) # Объявляем атрибут speed модели BikeModel c типом данных String
    speed = Column(Integer, nullable=False) # Объявляем атрибут speed модели BikeModel c типом данных Integer
    speedLimit = Column(Integer, nullable=False) # Объявляем атрибут speedLimit модели BikeModel c типом данных Integer
    longitude = Column(Float, nullable=False) # Объявляем атрибут longitude модели BikeModel c типом данных Float
    latitude = Column(Float, nullable=False) # Объявляем атрибут latitude модели BikeModel c типом данных Float
    
    __table_args__ = (
            
            CheckConstraint("bikeType IN ('Электросамокат', 'Электровелосипед')", name="bikeTypeValidate"), # Устанавливаем ограничение на атрибут bikeType модели BikeModel

            CheckConstraint("mode IN ('Поездка', 'Бронь', 'ТО', 'Ожидание')", name="modeValidate"), # Устанавливаем ограничение на атрибут mode модели BikeModel
            
            CheckConstraint("speed BETWEEN 0 AND 25", name="speedValidate"), # Устанавливаем ограничение на атрибут speed модели BikeModel
            
            CheckConstraint("speedLimit IN (20, 15, 10)", name="speedLimitValidate") # Устанавливаем ограничение на атрибут speedLimit модели BikeModel
                    
                    )
    
    @validates("bikeId") # Используем декоратор validates для создания кастомного валидатора атрибута bikeId
    def validateBikeId(self, key, bikeId):
        return bikeId if len(bikeId) == 6 and re.search(r'[A-Z][^а-яёА-ЯЁ]\d', bikeId) else ValueError(f"Значение {bikeId} не валидно") # Проверяем введенное значение на соответствие ограничениям, в противном случае, возвращаем ValueError

class CRUD:
    """
    Описание
        Класс CRUD — представляет собой класс для работы с ORM SQLAlchemy внутри данного ПО,
        и полностью отражает принцип CRUD(Create, Read, Update, Delete) по содержащимся методам.
        Выносить логику работы с СУБД в отдельный класс — хорошее решение к с точки зрения архитектуры,
        потому что использование подобного формата взаимодействия с API выбранной СУБД дает такие 
        преимущества как:

            — Легкое расширение функционала работы с БД
            
            — Возможность изменения логики работы с БД без затрагивания прочих модулей ПО

            — Возможность повторного использования в других проектах
       

    Структура класса CRUD
    |
    |— Конструктор (__init__(self))
    |  |
    |  |— Атрибут engine, содержит объект текущего движка СУБД, хранит результат выполнения метода
    |  |  create_engine(DBpath: str), в параметры которого передается путь до целевой БД, в формате
    |  |  '<СУБД>:///<путь до БД или адрес и порт БД>'
    |  |
    |
    |— Метод initModel(self) класса CRUD
    |  |
    |  |— Блок (try)
    |  |  |
    |  |  |— Вызов метода create_all(bind) атрибута metadata экземпляра класса Base.
    |  |  |  Метод create_all служит для инициализации всех моделей объявленных ранее
    |  |  |
    |  |  |— return True в случае успешного завершения операции возвращаем True
    |  |  |
    |  |
    |  |— Блок исключения (except exc.SQLAlchemyError)
    |  |  |
    |  |  |— return False в случае возникновения ошибки возвращаем False
    |
    |— Метод addBike(self, bikeData: list)
    |  |
    |  |— Блок (try)
    |  |  |
    |  |  |— Переменная bike хранящая экземпляр класса модели BikeModel, с атрибутами, которым
    |  |  |  были присвоены значения из списка bikeData
    |  |  |
    |  |  |— Вызов метода add(modelObj) экземпляра класса Session(bind). Служит для добавления нового экземпляра
    |  |  |  класса модели BikeModel
    |  |  |
    |  |  |— Вызов метода commit() эземпляра класса Session(bind). Иcпользуется для подтверждения изменений внесенных во время сессии
    |  |  |
    |  |  |— Возвращаем True в случае успешного завершения операции
    |  |  
    |  |— Блок исключения (except exc.SQLAlchemyError)
    |  |  |
    |  |  |— Вызов метода rollback() экземпляра класса Session. Отменяет все изменения в БД
    |  |  |  что были внесены в текущей сессии
    |  |  |
    |  |  |— return False в случае возникновения ошибки возвращаем False
    |  |  |
    |
    |— Метод getBikeList(self)
    |  |
    |  |— Блок (try)
    |  |  |
    |  |  |— Экземпляр класса Session(bind: engine) внутри контекстного менеджера
    |  |  |  |
    |  |  |  |— Вызов метода query(model) экземпляра класса Session(bind). Возвращает список экземпляров
    |  |  |  |  класса BikeModel с данными, взятыми из таблицы BikeModel. Для извлечения всех значений данной
    |  |  |  |  модели используется метод all()
    |  |  |
    |  |
    |  |— Блок исключения (except exc.SQLAlchemyError)
    |  |  |
    |  |  |— return False в случае возникновения ошибки возвращаем False
    |  |  |
    |
    |— Метод updateBikeInfo(self, bikeId: str, columnName: str, data: str)
    |  |
    |  |— Блок (try)
    |  |  |
    |  |  |— Экземпляр класса Session(bind: engine) внутри контекстного менеджера
    |  |  |
    |  |  |— Переменная bike, хранит экземпляр класса BikeModel, атрибут bikeId 
    |  |  |  которого совпадает с с переданным в метод параметром bikeId
    |  |  |
    |  |  |— Вызов встроенной функции setattr(). Служит для обновления значения переданного атрибута
    |  |  |  в экземпляре класса BikeModel.
    |  |  |  
    |  |  |— Вызов метода commit() эземпляра класса Session(bind). Иcпользуется для подтверждения изменений внесенных во время сессии
    |  |  |
    |  |  |— Возвращаем True в случае успешного завершения операции
    |  |  |
    |  | 
    |  |— Блок исключения (except exc.SQLAlchemyError)
    |  |  |
    |  |  |— Вызов метода rollback() экземпляра класса Session. Отменяет все изменения в БД
    |  |  |  что были внесены в текущей сессии
    |  |  |
    |  |  |— return False в случае возникновения ошибки возвращаем False
    |  |  |
    |  |  |
    |
    |— Метод deleteBike(self, bikeId: str)
    |  |
    |  |— Блок (try)
    |  |  |
    |  |  |— Экземпляр класса Session(bind: engine) внутри контекстного менеджера
    |  |  |
    |  |  |— Переменная bike, хранит экземпляр класса BikeModel, атрибут bikeId 
    |  |  |  которого совпадает с переданным в метод параметром bikeId
    |  |  |
    |  |  |— Вызов метода delete(modelObj) экземпляра класса Session(bind). Служит
    |  |  |  для удаления переданного экземпляра класса BikeModel из таблицы модели BikeModel
    |  |  |
    |  |  |— Вызов метода commit() эземпляра класса Session(bind). Иcпользуется для подтверждения изменений внесенных во время сессии
    |  |  |
    |  |  |— Возвращаем True в случае успешного завершения операции
    |  |
    |  |— Блок исключения (except exc.SQLAlchemyError)
    |  |  |
    |  |  |— Вызов метода rollback() экземпляра класса Session. Отменяет все изменения в БД
    |  |  |  что были внесены в текущей сессии
    |  |  |
    |  |  |— return False в случае возникновения ошибки возвращаем False 
    """
    def __init__(self, engine):
        self.engine = engine # Инициализируем атрибут engine хранящий движок базы данных

    def initModel(self) -> bool:
        try:
            Base.metadata.create_all(bind=self.engine) # Инициализируем объявленные ранее модели данных
            return True # Возвращаем True в случае успешного завершения операции

        except exc.SQLAlchemyError: return False # В случае возникновения ошибки возвращаем False

    def addBike(self, bikeData: list) -> bool:
        try:
            with Session(bind=self.engine) as db: # Инициализируем сессию работы с БД через контекстный менеджер
                bike = BikeModel(
                        bikeId = bikeData[0],
                        bikeType = bikeData[1], 
                        mode = bikeData[2], 
                        speed = bikeData[3],
                        speedLimit = bikeData[4],
                        latitude = bikeData[5],
                        longitude = bikeData[6]
                        ) # Инициализируем экземпляра класса BikeModel с значениями из переданного списка bikeData
                db.add(bike) # Добавляем новую запись о ТС в таблицу модели BikeModel
                db.commit() # Подтверждаем изменения внесенные в таблицу модели BikeModel
                return True  # Возвращаем True в случае успешного завершения операции
        
        except exc.SQLAlchemyError as e:
            db.rollback() # Отменяем внесенные изменения в случае возникновения ошибки
            return False # В случае возникновения ошибки возвращаем False

    def getBikeList(self) -> list:
        try:
            with Session(bind=self.engine) as db: # Инициализируем сессию работы с БД через контекстный менеджер
                return db.query(BikeModel).all() # Получаем все записи из таблицы модели BikeModel
        except exc.SQLAlchemyError: return False # В случае возникновения ошибки возвращаем False
    
    def updateBikeInfo(self, bikeId: str, columnName: str, data: str) -> bool:
        try:
            with Session(bind=self.engine) as db: # Инициализируем сессию работы с БД через контекстный менеджер
                bike = db.query(BikeModel).filter(BikeModel.bikeId == bikeId).first() # Получаем экземпляр класса BikeModel по значению атрибута bikeId
                setattr(bike, columnName, data) # Устанавливаем новое значение атрибута экземпляра класса BikeModel
                db.commit() # Подтверждаем изменения внесенные в таблицу модели BikeModel
                return True # Возвращаем True в случае успешного завершения операции
        
        except exc.SQLAlchemyError as e:
            db.rollback() # Отменяем внесенные изменения в случае возникновения ошибки
            return False # В случае возникновения ошибки возвращаем False

    def deleteBike(self, bikeId: str) -> bool:
        try:
            with Session(bind=self.engine) as db: # Инициализируем сессию работы с БД через контекстный менеджер
                bike = db.query(BikeModel).filter(BikeModel.bikeId == bikeId).first() # Получаем экземпляр класса BikeModel по значению атрибута bikeId
                db.delete(bike) # Удаляем запись о ТС из таблицы модели BikeModel
                db.commit() # Подтверждаем изменения внесенные в таблицу модели BikeModel
                return True # Возвращаем True в случае успешного завершения операции

        except exc.SQLAlchemyError as e:
            db.rollback() # Отменяем внесенные изменения в случае возникновения ошибки
            return False # В случае возникновения ошибки возвращаем False




class MessageBoxWindow(QMessageBox):
    """
    Описание
        Класс MessageBoxWindow — представляет собой дочерний класс QMessageBox. В рамках данного приложения
        применяется для отображения ошибок при неудачном завершении операции, однако может использоваться
        и для отображения прочих видов уведомлений. Структура класса MessageBoxWindow представлена ниже

    Структура класса MessageBoxWindow:
    |    
    |————Конструктор (__init__(self))
         |
         |— Метод super().__init__() Инициализируем родительский класс
         |
         |— Метод setWindowTitle(title: str) Устанавливаем заголовок окна уведомления
         |
         |— Метод setIcon(icon: Icon) Устанавливаем иконку из подкласса Icon которая 
         |  соответствует типу уведомления
         |
         |— Метод setText(text: str) Устанавливаем текст уведомления
         |
         |— Метод setStandardButtons При необходимости устанавливаем кнопки из подкласса StandardButton
         |  Как можно заметить, у нас есть возможность комбинировать кнопки из данного набора, передавая
         |  в качестве параметра функции результаты побитовой операции OR
         |
         |— Метод exec() Запускаем окно через базовый метод отображения окна
         |
    """
    def __init__(self, title: str, icon: QIcon, text: str, choose=False):
        super().__init__() # Инициализируем родительский класс QMessageBox
        self.setWindowTitle(title) # Устанавливаем заголовок окна
        self.setIcon(icon) # Устанавливаем эквивалентную типу иконку диалогового окна
        self.setText(text) # Устанавливаем текст диалогового окна
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No if choose else QMessageBox.StandardButton.Ok) # Устанавливаем кнопки диалогового окна
        self.exec() # Отображаем диалоговое окно


class ActionToolBar(QToolBar):
    """
    Описание
        Класс ActionToolBar — в контексте данного приложения представляет собой панель инструментов, что содержит 
        иконки инструментов (QAction) для проведения операций с транспортными средствами внутри системы.  Использование 
        виджета QToolBar для хранения инструментов внутри приложения является хорошей практикой по ряду причин,
        таких как:
            
            — Быстрый и интуитивный доступ к необходимым инструментам
            
            — Возможность позиционирования и масштабирования панели
              инструментов под нужды пользователя

    Структура класса ActionToolBar:
    |    
    |————Конструктор (__init__(self))
         |
         |— Метод super().__init__() Инициализируем родительский класс
         | 
         |— Атрибут createAction хранящий экземпляр класса QAction(action: str).
         |  Служит для инициализации инструмента добавления записи о ТС
         |
         |— Атрибут deleteAction хранящий экземпляр класса QAction(action: str).
         |  Служит для инициализации инструмента удаления записи о ТС
         |
         |— Метод setIcon(icon: Icon) экземпляра класса QAction. Служит для
         |  установки иконки инструмента добавления записи о ТС
         |
         |— Метод addAction(action: QAction) экземпляра класса QToolBar. Служит для
         |  добавления инструмента создания записи о ТС в родительскую панель инструментов
         |
         |— Метод addAction(action: QAction) экземпляра класса QToolBar. Служит для
         |  добавления инструмента создания записи о ТС в родительскую панель инструментов
         |
    """
    def __init__(self):
        super().__init__() # Инициализируем родительский класс QToolBar
        createAction = QAction("Добавить ТС", self) # Инициализируем экземпляр класса QAction
        deleteAction = QAction("Удалить ТС", self) # Инициализируем экземпляр класса QAction
        
        createAction.setIcon(QIcon("./images/add.ico")) # Устанавливаем иконку инструмента добавления ТС c помощью экземпляра класса QIcon
        deleteAction.setIcon(QIcon("./images/cross.ico"))  # Устанавливаем иконку инструмента удаления ТС c помощью экземпляра класса QIcon
        
        self.addAction(createAction) # Добавляем инструмент создания записи о ТС в панель инструментов
        self.addAction(deleteAction) # Добавляем инструмент удаления записи о ТС в панель инструментов
    

class AboutWindow(QDialog):
    """
    Описание
        Класс AboutWindow — представляет собой один из простейших классов в рамках
        данного приложения. Являясь дочерним классом QDialog, AboutWindow служит
        для отображения справочной информации, быть точнее краткого описания функционала
        и назначения данной программы
    
    Структура класса AboutWindow:
    |    
    |————Конструктор (__init__(self))
         |
         |— Метод super().__init__() Инициализируем родительский класс
         |
         |— Метод setWindowTitle(title: str ) Устанавливаем заголовок информационного окна 
         |
         |— Метод setFixedSize(width: int, height: int) Устанавливаем фиксированный размер текущего окна
         |
         |— Атрибут layout хранит экземпляр класса макета QVBoxLayout
         |
         |— Атрибут descriptionLabel хранит экземпляр класса QLabel, c справочной информацией
         |
         |— Атрибут buttonOk хранит экземпляр класса QPushButton, служит для закрытия
         |  информационного окна
         |
         |— Cигнал clicked связывающий атрибут buttonOk и метод self.close()
         |
         |— Метод addWidget(widget: QWidget) Добавляем экземпляр класса QLabel в макет QVBoxLayout
         |
         |— Метод addWidget(widget: QWidget) Добавляем экземпляр класса QPushButton в макет QVBoxLayout
         |
         |— Метод addWidget(layout: QVBoxLayout) Добавляем макет QVBoxLayout в качестве макета родительского
         |  виджета QDialog
         |
         |— Метод exec() Отображаем информационное окно
         |
    """
    def __init__(self, title: str, text: str):
        super().__init__() # Инициализируем родительский класс QDialog
        self.setWindowTitle(title) # Устанавливаем заголовок информационного окна QDialog
        self.setFixedSize(500, 250) # Устанавливаем фиксированный размер диалогового окна
        self.layout = QVBoxLayout() # Инициализируем макет QVBoxLayout
        
        self.descriptionLabel = QLabel(text) # Инициализируем атрибут descriptionLabel хранящий экземпляр класса QLabel
        self.buttonOk = QPushButton("ОК") # Инициализируем атрибут buttonOk хранящий экземпляр класса QPushButton
        self.buttonOk.clicked.connect(self.close) # Устанавливаем сигнал clicked на атрибут buttonOk
        
        self.layout.addWidget(self.descriptionLabel) # Добавляем в макет экземпляр класса QLabel
        self.layout.addWidget(self.buttonOk) # Добавляем в макет экземпляр класса QPushButton
        
        self.setLayout(self.layout) # Устанавливаем layout в качестве макета родительского виджета QDialog

        self.exec() # Отображаем диалоговое окно


class InsertBikeWindow(QDialog):
    """
    Описание
        Класс InsertBikeWindow — как можно понять из названия класса, его основная роль
        в рамках данной программы — добавление новых записей о ТС в таблицу модели BikeModel.
        Элементы графического интерфейса сконфигурированы так, чтобы формат вводимых значений
        был интуитивно понятен любому пользователю. Там где необходимо получить четко определенное
        значение, такое как режим работы ТС или скоростной режим, используется виджет QComboBox,
        в случае же, когда необходимо принять такие значения как координаты ТС, лучшим выбором будет
        виджет QLineEdit с подсказкой ввиде 'плейсхолдера'. Теперь можно перейти к структуре класса
        InsertBikeWindow, что представлена ниже

    Структура класса InsertBikeWindow:
    |    
    |————Конструктор (__init__(self))
    |    |
    |    |— Метод super().__init__() Инициализируем родительский класс QDialog
    |    |
    |    |— Метод setWindowTitle(title: str) Устанавливаем заголовок диалогового окна
    |    |
    |    |— Метод setFixedSize(width: int, height: int) Устанавливаем фиксированный размер диалогового окна
    |    |
    |    |— Атрибут layout хранит экземпляр класса макета QFormLayout
    |    |
    |    |— Атрибут bikeIdEntry хранит экземпляр класса QLineEdit, служит для получения идентификатора нового ТС
    |    |
    |    |— Атрибут bikeTypeEntry хранит экземпляр класса QComboBox, служит для получения типа нового ТС
    |    |
    |    |— Атрибут modeEntry хранит экземпляр класса QComboBox, служит для указания режима работы нового ТС
    |    |
    |    |— Атрибут speedEntry хранит экземпляр класса QLineEdit, служит для получения идентификатора нового ТС
    |    |
    |    |— Атрибут speedLimitEntry хранит экземпляр класса QLineEdit, служит для указания скорости нового ТС
    |    |  c функциональной точки зрения данный виджет не выполняет никакой роли, однако полезен для обозначения
    |    |  наличия данного атрибута
    |    |
    |    |— Атрибут latitudeEntry хранит экземпляр класса QLineEdit, служит для получения данных о широте на котором 
    |    |  находится добавляемое ТС
    |    |
    |    |— Атрибут longitudeEntry хранит экземпляр класса QLineEdit, служит для получения данных о долготе на которой 
    |    |  находится добавляемое ТС
    |    |
    |    |
    |    |— Метод setPlaceholderText(placeholderText: str) экземпляра класса QLineEdit. Служит для указания формата вводимых значений
    |    |
    |    |— Метод addItems(items: list[str]) экземпляра класса QComboBox. Добавляет в виджет QComboBox данные о типах ТС 
    |    |
    |    |— Метод setText(text: str) экземпляра класса QLineEdit. Устанавливает значение виджета QLineEdit по умолчанию
    |    |
    |    |— Метод setReadOnly(stat: bool) экземпляра класса QLineEdit. Меняет режим работы виджета QLineEdit на ReadOnly 
    |    |
    |    |— Метод addItems(items: list[str]) экземпляра класса QComboBox. Добавляет в виджет QComboBox данные о доступных режимах работы ТС 
    |    |
    |    |— Метод setPlaceholderText(placeholderText: str) экземпляра класса QLineEdit. Служит для указания формата вводимых значений
    |    |
    |    |— Метод setPlaceholderText(placeholderText: str) экземпляра класса QLineEdit. Служит для указания формата вводимых значений
    |    |
    |    |— Cигнал clicked связывающий атрибут submitButton и метод insertBike(self)
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLineEdit в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QComboBox в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QComboBox в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLineEdit в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QComboBox в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLineEdit в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLineEdit в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QPushButton в макет QFormLayout
    |    |
    |    |— Метод setLayout(layout: QFormLayout) Устанавливаем макет QFormLayout, в качестве макета родительского виджета
    |    |
    |    |— Метод exec() экземпляра класса QDialog. Служит для отображения диалового окна
    |
    |————Метод insertBike(self)
    |    |
    |    |— Переменная crud хранит экземпляр класса CRUD для работы с базой данных через ORM SQLAlchemy
    |    |
    |    |— Переменная bike содержит генератор списков, что создает список значений атрибутов модели BikeModel
    |    |  |
    |    |  |— Цикл for итерирующий внутри списка названий атрибутов, что хранят данные о новом ТС
    |    |  |  |
    |    |  |  |— Ветвление (if isinstance(getattr(self, i), QLineEdit)) проверяет экземпляр класса внутри атрибута
    |    |  |  |  | полученного через встроенную функцию getattr(class, attr: str) на соответствие типу QLineEdit
    |    |  |  |  |
    |    |  |  |  |— Вызов встроенной функции getattr(self, i).text() вызывается в случае если тип атрибута соответствует
    |    |  |  |  |  QLineEdit. Возвращает введенное значение итерируемого виджета QLineEdit
    |    |  |  |  |
    |    |  |  |
    |    |  |  |— Ответвление (else getattr(self, i).currentText())
    |    |  |  |  |
    |    |  |  |  |— Вызов встроенной функции getattr(self, i).currentText() вызывается в случае несоотвествия
    |    |  |  |  |  типа атрибута типа QLineEdit. Возвращает текущий элемент виджета QComboBox
    |    |  |  |  |
    |    |  |  |
    |    |
    |    |— Ветвление (if not crud.addBike(bike: BikeModel). Метод addBike делает INSERT запрос к таблице 
    |    |  |   модели BikeModel. 
    |    |  |
    |    |  |— Экземпляр класса MessageBoxWindow(title: str, text: str, icon: QIcon) отображает предупреждающее окно
    |    |  |  в случае возврата False методом addBike(bike: BikeModel)
    |    |  |
    |    |  
    |    |— Ответвление (else) Запускает логику в случае успешного выполнения INSERT запроса к таблице модели BikeModel
    |    |  |
    |    |  |— Отлючение сигнала cellChanged связывающий атрибут bikeTable и метод updateRow(self, bikeId, columnName, data)
    |    |  |
    |    |  |— Вызов метода pushRow(row: list) экземпляра класса BikesTableDock. Служит добавления нового ТС в виджет QTableWidget
    |    |  |
    |    |  |— Обратное подключение сигнала cellChanged связывающий атрибут bikeTable и метод updateRow(self, bikeId: str, columnName: str, data)
    |    |  |
    |    |  |— Метод infoLog(text: str) экземпляра класса BikeModelLogDock. Добавляет запись о добавлении нового ТС в журнал текущей сессии
    |    |  |  с указанием времени добавления, и внутреннего идентификатора ТС
    |    |  |
    |    |  |— Метод close() экземпляра класса QDialog. Служит для закрытия диалогового окна после проведения операции добавления нового ТС
    |    |  |
    """
    def __init__(self, logger, table):
        super().__init__() # Инициализируем родительский класс QDialog
        self.setWindowTitle("Добавить новое ТС") # Устанавливаем заголовок диалогового окна QDialog
        self.setFixedSize(500, 250) # Устанавливаем фиксированный размер текущего виджета

        self.logger = logger # Инициализируем атрибут logger хранящий экземпляр класса BikeModelLogDock
        self.table = table # Инициализируем атрибут table хранящий экземпляр класса BikesTableDock

        self.layout = QFormLayout() # Инициализируем макет QFormLayout

        self.bikeIdEntry = QLineEdit() # Инициализируем атрибут bikeIdEntry хранящий экземпляр класса QLineEdit
        self.bikeTypeEntry = QComboBox() # Инициализируем атрибут bikeTypeEntry хранящий экземпляр класса QComboBox
        self.modeEntry = QComboBox() # Инициализируем атрибут modeEntry хранящий экземпляр класса QComboBo Запускает логику в случае успешного выполнения INSERT запроса к таблице модели BikeModel
        self.speedEntry = QLineEdit() # Инициализируем атрибут speedEntry хранящий экземпляр класса QLineEdit
        self.speedLimitEntry = QComboBox() # Инициализируем атрибут speedLimitEntry хранящий экземпляр класса QComboBox
        self.latitudeEntry = QLineEdit() # Инициализируем атрибут latitudeEntry хранящий экземпляр класса QLineEdit
        self.longitudeEntry = QLineEdit() # Инициализируем атрибут longitudeEntry хранящий экземпляр класса QLineEdit
        self.submitButton = QPushButton("Добавить") # Инициализируем атрибут submitButton хранящий экземпляр класса QPushButton

        self.bikeIdEntry.setPlaceholderText("ABC000") # Устанавливаем на экземпляр класса QLineEdit placeholder с указанием формата вводимых значений
        self.bikeTypeEntry.addItems(["Электросамокат", "Электровелосипед"])
        self.modeEntry.addItems(["ТО", "Ожидание", "Бронь", "Поездка"]) # Добавляем режимы работы ТС экземпляр класса QListWidget
        self.speedEntry.setText("0") # Устанавливаем значение скорости ТС по умолчанию т.е 0
        self.speedEntry.setReadOnly(True) # Устанавливаем режим ReadOnly для экземпляра класса QLineEdit
        self.speedLimitEntry.addItems(["20", "15", "10"]) # Добавляем допустимые ограичения скорости ТС экземпляр класса QListWidget
        self.latitudeEntry.setPlaceholderText("0.000000") # Устанавливаем на экземпляр класса QLineEdit placeholder с указанием формата вводимых значений
        self.longitudeEntry.setPlaceholderText("0.000000") # Устанавливаем на экземпляр класса QLineEdit placeholder с указанием формата вводимых значений

        self.submitButton.clicked.connect(self.insertBike) # Устанавливает сигнал clicked на атрибут submitButton

        self.layout.addRow("Внутренний идентификатор", self.bikeIdEntry) # Добавляем в макет формы экземпляр класса QLineEdit 
        self.layout.addRow("Тип ТС", self.bikeTypeEntry) # Добавляем в макет формы экземпляр класса QComboBox
        self.layout.addRow("Режим работы ТС", self.modeEntry) # Добавляем в макет формы экземпляр класса QComboBox
        self.layout.addRow("Cкорость", self.speedEntry)# Добавляем в макет формы экземпляр класса QLineEdit 
        self.layout.addRow("Ограничение скорости", self.speedLimitEntry) # Добавляем в макет формы экземпляр класса QComboBox
        self.layout.addRow("Широта", self.latitudeEntry) # Добавляем в макет формы экземпляр класса QLineEdit
        self.layout.addRow("Долгота", self.longitudeEntry) # Добавляем в макет формы экземпляр класса QLineEdit
        self.layout.addRow(self.submitButton) # Добавляем в макет формы экземпляр класса QPushButton
        
        self.setLayout(self.layout) # Устанавливаем layout в качестве макета родительского виджета QDialog
         
        self.exec() # Отображаем диалоговое окно
        
    def insertBike(self) -> None:
        crud = CRUD(engine=create_engine("sqlite:///ormproto.db")) # Инициализируем переменную crud экземпляра класса CRUD, что служит для работы с ORM
        bike = [getattr(self, i).text() if isinstance(getattr(self, i), QLineEdit) else getattr(self, i).currentText() for i in list(self.__dict__.keys())[3:-1]] # Инициализируем переменную bike служащую для хранения данных о новом ТС
        if not crud.addBike(bike): MessageBoxWindow(title="Ошибка добавления ТС", text="SQLAlchemy: не удалось добавить запись о ТС", icon=QMessageBox.Icon.Warning) # Добавляем новое ТС в таблицу BikeModel с помощью метода addBike экземпляра класса CRUD
        else:
            self.table.bikeTable.cellChanged.disconnect(self.table.updateRow) # Временно отключаем сигнал cellChanged атрибута bikeTable воизбежании многократного вызова метода updateRow
            self.table.pushRow(bike) # Инкапсулируем данные о новом ТС в виджет QTableWidget
            self.table.bikeTable.cellChanged.connect(self.table.updateRow) # Повторно подключаем сигнал cellChanged атрибута bikeTable
            self.logger.infoLog(f"ТС с внутренним идентификатором {self.bikeIdEntry.text()} было добавлено") # Добавляем информационное сообщение о добавлении текущего ТС в виджет QListWidget
            self.close() # Закрываем диалоговое окно
        
        




class ReadOnlyDelegate(QStyledItemDelegate):
    """
    Описание
        Класс ReadOnlyDelegate — представляет собой дочерний класс QStyledItemDelegate,
        в рамках данного приложения используется лишь в классе BikesTableDock, для
        установки режима ReadOnly на столбец внутреннего идентификатора ТС (bikeId).
        Структура класса ReadOnlyDelegate представлена ниже

        Структура класса ReadOnlyDelegate
        |
        |— Метод createEditor(self, parent, option, index)
        |  |
        |  |— Возвращаем None при попытке создать редактор ячейки таблицы QTableWidget
        |  |
        |
    """
    def createEditor(self, parent, option, index) -> None:
        return # Возвращаем None при попытке инициализации редактора ячейки


class BikesTableDock(QDockWidget):
    """
    Описание
        Класс BikesTableDock — с концептуальной точки зрения представляет собой главный виджет
        данного приложения. Являясь таблицой, данный виджет отображает все записи о ТС, что
        содержит таблица модели BikeModel. Благодаря полной синхронизации с таблицей, данный
        класс предоставляет возможность быстрого и удобного редактирования атрибутов отдельных
        сущностей модели BikeModel, благодаря чему в полной мере соответствует принципу CRUD
        (Create, Read, Update, Delete). Структура класса BikesTableDock представлена ниже


    Структура класса BikesTableDock
    |
    |————Конструктор (__init__(self, logger))
    |    |
    |    |— Метод super().__init__() Инициализируем родительский класс QDockWidget
    |    |
    |    |— Метод setWindowTitle(title: str) Устанавливаем заголовок доквиджета
    |    |
    |    |— Атрибут crud хранит экземпляр класса CRUD для работы с базой данных через ORM SQLAlchemy 
    |    |
    |    |— Атрибут logger содержит экземпляр класса BikeModelLogDock, служит для логирования операций
    |    |  внутри класса BikesTableDock
    |    |
    |    |— Атрибут PreviousValue, служит для хранения значения ячейки перед началом редактирования,
    |    |  в случае возникновения ошибки валидации на уровне ORM устанавливается в качестве значения
    |    |  отредактированной пользователем ячейки
    |    |
    |    |— Атрибут tableAttrs хранит кортеж, что содержит список значений эквивалентных названиям атрибутов
    |    |  таблицы модели BikeModel
    |    |
    |    |— Атрибут bikeTable хранит экземпляр класса QTableWidget, представляя собой таблицу является
    |    |  центральным виджетом класса BikesTableDock
    |    |
    |    |— Вызов метода setColumnCount(columnCount: int) экземпляра класса QTableWidget. Устанавливает фиксированное
    |    |  количество столбцов виджета QTableWidget
    |    |
    |    |— Вызов метода setHorizontalHeaderLabels(headerLabels: list[str]) экземпляра класса QTableWidget. Принимая список
    |    |  строк устанавливает названия заголовков столбцов
    |    |
    |    |— Вызов метода setItemDelegateForColumn(columnIndex: int, delegate: QStyledItemDelegate) экземпляра класса QTableWidget.
    |    |  Принимает в качестве параметров индекс столбца на который необходимо установить делегат, а также сам делегат,
    |    |  т.е класс наследник QStyledItemDelegate
    |    |
    |    |— Вызов метода setBikeList(), служит для добавления данных о ТС в виджет QTableWidget в формате строк
    |    |  из таблицы модели BikeModel
    |    |
    |    |— Вызов метода resizeColumnsToContents() экземпляра класса QTableWidget. Данный метод используется для
    |    |  форматирования ширины столбцов таблицы под размер содержимого
    |    |
    |    |— Cигнал cellChanged связывающий виджет таблицы (QTableWidget) и метод updateRow(self, row, column)
    |    |
    |    |— Cигнал itemPressed связывающий атрибут bikeTable и метод setPreviousValue(self). Служит для вызова метода
    |    |  setPreviousValue(self), что будет сохранять изначальное значение редактируемой ячейки
    |    |
    |    |— Вызов метода setWidget(widget: QWidget) экземпляра класса QDockWidget. Устанавливает виджет QTableWidget
    |    |  в качестве цуентрального виджета QDockWidget
    |    |
    |
    |— Метод setPreviousValue(self, item)
    |  |
    |  |— Устанавливаем атрибуту previousValue значение ячейки до редактирования (item.text())
    |  |
    |
    |— Метод setBikeList()
    |  |
    |  |— Блок (try)
    |  |  |
    |  |  |— Генератор списков ([self.pushRow(row) for row in ...]) итерируется внутри двойного
    |  |  |  |  генератора списков, что содержит данные о ТС ввиде списков.
    |  |  |  |
    |  |  |  |— Вызов метода pushRow(row: list) Служит для добавления записей о ТС в виджет QTableWidget
    |  |  |  |
    |  |  |  |— Генератор списков ([getattr(bike, column.name) for column in BikeModel.__table__.columns])
    |  |  |  |  |   служит получения значений атрибутов экземпляров модели BikeModel по имени столбца (атрибута)
    |  |  |  |  |
    |  |  |  |  |— Вызов встроенной функции getattr(bike, column.name). Служит для получения значений атрибутов
    |  |  |  |  |  итерируемого объекта модели BikeModel
    |  |  |  |  |
    |  |  |  |  |— Генератор списков ([bike for bike in self.crud.getBikeList()]) Итерируется внутри списка объектов
    |  |  |  |  |  модели BikeModel, давая возможность проводить операции с итерируемым объектом на уровне выше
    |  |  |  |  |
    |  |  |  |  
    |  |
    |  |— Блок (except exc.SQLAlchemyError)
    |  |  |
    |  |  |— pass Бездействуем в случае возникновение ошибки со стороны ORM SQLAlchemy
    |  |  |
    |
    |— Метод pushRow(self, items: list)
    |  |
    |  |— Переменная row, содержит результат выполнения метода rowCount() экземпляра класса
    |  |  QTableWidget, что возвращает текущее количество строк виджета QTableWidget ввиде
    |  |  целочисленного значения
    |  |
    |  |— Вызов метода insertRow(row: int) экземпляра класса QTableWidget. Служит для
    |  |  добавления в виджет QTableWidget пустой строки.
    |  |
    |  |— Генератор списков ([self.bikeTable.setItem(row, items.index(item), QTableWidgetItem(str(item))) for item in items])
    |  |  | Используется для заполнения столбцов недавно добавленной строки значениями атрибутов нового ТС.
    |  |  |
    |  |  |— Метод setItem(row: int, column: int, item: QTableWidgetItem) экземпляра класса QTableWidget
    |  |  |  Служит для добавления значения в определенную ячейку. В качестве значений принимает индексы
    |  |  |  строки и столбца в которых расположена ячейка, а также экземпляр класса QTableWidgetItem(item)
    |  |  |  принимающий в качестве аргумента значение, которое необходимо вставить в ячейку
    |  |  |
    |  |
    |
    |— Метод updateRow(self, row, column)
    |  |
    |  |— Переменная bikeId, содержит результат выполнения метода item(row: int, column: int) экземпляра класса
    |  |  QTableWidget. Данный метод содержит значение столбца с нулевым индексом столбца текущей строки, быть
    |  |  точнее внутренний идентификатор ТС, который используется для поиска нужного объекта в таблице модели
    |  |  BikeModel. Важно помнить, что метод item(row: int, column: int) возвращает лишь экземпляр класса
    |  |  QTableWidgetItem, для получения значения ячейки, в нашем случае идентификатора, необходимо вызвать
    |  |  метод text() экземпляра класса QTableWidgetItem
    |  |
    |  |— Переменная value, содержит результат выполнения метода item экземпляра класса
    |  |  QTableWidget. Хранит введенное пользователем значение ячейки для дальнейшего
    |  |  обновления атрибута объекта таблицы модели BikeModel, имя которого мы можем
    |  |  получить из кортежа tableAttrs, по индексу столбца (column)
    |  |
    |  |— Ветвление (if not self.crud.updateBikeInfo(bikeId: str, attr: str, value))
    |  |  | Проверяет результат выполнения метода updateBikeInfo(bikeId: str, attr: str, value)
    |  |  | что обновляет значение указанного атрибута объекта модели BikeModel, находя его по
    |  |  | значению атрибута bikeId, что передается в параметры данного метода
    |  |  |
    |  |  |— Экземпляр класса MessageBoxWindow(title: str, text: str, icon: QIcon) отображает предупреждающее окно
    |  |  |  в случае возврата False методом updateBikeInfo(bikeId, attr: str, value)
    |  |
    |  |— Ответвление (else) Запускает логику в случае успешного выполнения метода updateBikeInfo(bikeId: str, attr: str, value)
    |  |  |
    |  |  |— Вызов метода infoLog(text: str) экземпляра класса BikeModelLogDock. Добавляет запись о успешном обновлении
    |  |  |  атрибута объекта модели BikeModel с указанием времени в формате (%H:%M:%S) и внутреннего идентификатора
    |  |  |  обновленного ТС
    |
    |— Метод deleteRow(self)
    |  | 
    |  |— Переменная row, содержит результат выполнения метода rowCount() экземпляра класса
    |  |  QTableWidget, что возвращает текущее количество строк виджета QTableWidget ввиде
    |  |  целочисленного значения
    |  |
    |  |— Атрибут bikeId, содержит результат выполнения метода item(row: int, column: int) экземпляра класса
    |  |  QTableWidget. Хранит внутренний идентификатор удаляемого ТС
    |  |
    |  |— Ветвление (if not self.crud.deleteRow(self, bikeId: str))
    |  |  | Проверяет результат выполнения метода deleteBike(bikeId: str), что служит
    |  |  | для удаления объекта текущего ТС из модели таблицы BikeModel.
    |  |  |
    |  |  |— Экземпляр класса MessageBoxWindow(title: str, text: str, icon: QIcon) отображает предупреждающее окно
    |  |  |  в случае возврата False методом deleteBike(self)
    |  |  |
    |  |
    |  |— Ответвление (else) Запускает логику в случае успешного выполнения метода deleteRow(self, bikeId: str)
    |  |  |
    |  |  |— Вызов метода removeRow(row: int) служит для удаления записи о удаленном ТС из виджета QTableWidgetItem
    |  |  |  индексу строки
    |  |  |
    |  |  |— Вызов метода infoLog(text: str) экземпляра класса BikeModelLogDock. Добавляет запись о успешном удалении
    |  |  |  атрибута объекта модели BikeModel с указанием времени в формате (%H:%M:%S) и внутреннего идентификатора
    |  |  |  удаленного ТС
    |  |  |
    |
    |— Метод rowOperations(self, action: QAction)
    |  |
    |  |— Ветвление match:case проверяющее значение полученного объекта действия
    |  |  |
    |  |  |— Опция 'Удаление ТС'
    |  |  |  |
    |  |  |  |— Вызов метода deleteRow(self) служит для удаления выбранного ТС 
    |  |  |  |
    |  |  |
    |  |  |— Опция 'Удаление ТС'
    |  |  |  |
    |  |  |  |— Экземпляр класса InsertBikeWindow(logger: BikeModelLogDock, table: BikesTableDock)
    |  |  |  |  служит для добавления нового ТС в виджет QTableWidget и таблицу модели BikeModel
    |  |  |  |
    |  |  |
    |  |
    |
    """
    def __init__(self, logger):
        super().__init__() # Инициализируем родительский класс QDockWidget
        self.setWindowTitle("Таблица транспортных средств") # Устанавливаем заголовок DockWidget
        
        self.crud = CRUD(engine=create_engine("sqlite:///ormproto.db")) # Инициализируем атрибут crud хранящий экземпляр класса CRUD
        
        self.logger = logger # Инициализируем атрибут logger хранящий экземпляр класса BikeModelLogDock
        
        self.previousValue = None # Инициализируем атрибут previousValue, для хранения значения столбца до его редактирования
        self.tableAttrs: tuple = (
        "bikeId",
        "bikeType",
        "mode",
        "speed",
        "speedLimit",
        "latitude",
        "longitude") # Инициализируем атрибут tableAttrs хранящий кортеж с названия атрибутов модели bikeModel

        self.bikeTable = QTableWidget() # Инициализируем атрибут bikeTable хранящий экземпляр класса QTableWidget
        self.bikeTable.setColumnCount(7) # Указываем количесво столбцов виджета QTableWidget

        self.bikeTable.setHorizontalHeaderLabels(["Внутренний номер", "Тип ТС", "Режим ТС", "Текущая скорость", "Лимит скорости", "Широта", "Долгота"]) # Устанавливаем горизонтальные заголовки виджета QTableWidget

        self.bikeTable.setItemDelegateForColumn(0, ReadOnlyDelegate()) # Устанавливаем режим ReadOnly для столбца bikeId

        self.setBikeList() # Добавляем в виджет QTableWidget строки из табицы модели BikeModel
        
        self.bikeTable.resizeColumnsToContents() # Форматируем размер столбцов по размеру содержимого ячеек

        self.bikeTable.cellChanged.connect(self.updateRow) # Устанавливаем сигнал cellChanged на атрибут bikeTable
        self.bikeTable.itemPressed.connect(self.setPreviousValue)

        self.setWidget(self.bikeTable) # Устанавливаем widget в качестве главного виджета экземпляра класса QDockWidget

    def setPreviousValue(self, item) -> None:
        self.previousValue = item.text()

    def setBikeList(self):
        try: [self.pushRow(row) for row in [[getattr(bike, column.name) for column in BikeModel.__table__.columns][1:] for bike in self.crud.getBikeList()]] # Вставляем в виджет QTableWidget данные, что были получены из таблицы модели BikeModel
        except exc.SQLAlchemyError: pass # В случае отсутствия строк в таблице модели BikeModel бездействуем 

    def pushRow(self, items: list) -> None:
        row = self.bikeTable.rowCount() # Объявляем переменную row для хранения текущего количества строк внутри виджета QTableWidget 
        self.bikeTable.insertRow(row) # Добавляем в виджет QTableWidget новую, пока что пустую строку
        [self.bikeTable.setItem(row, items.index(item), QTableWidgetItem(str(item))) for item in items] # Наполняем данными столбцы недавно созданной строки
 
    def updateRow(self, row, column) -> None:
        bikeId = self.bikeTable.item(row, 0).text() # Объявляем переменную bikeId для хранения значения столбца bikeId текущей строки
        value = self.bikeTable.item(row, column).text() # Объявляем переменную value для хранения нового значения ячейки
        if not self.crud.updateBikeInfo(bikeId, self.tableAttrs[column], value): # Обновляем значение атбирута, что было получено из редактора ячейки
            MessageBoxWindow(title="Ошибка обновления ТС", text=f"Входное значение не валидно, попробуйте еще раз", icon=QMessageBox.Icon.Warning)
            self.bikeTable.setItem(row, column, QTableWidgetItem(self.previousValue)) # Возвращаем старое значение измененной ячейки

        else: self.logger.infoLog(f"ТС с внутренним идентификатором {bikeId} было обновлено") # Добавляем информационное сообщение об обновлении текущего ТС в виджет QListWidget 
            
    def deleteRow(self) -> None:
        row = self.bikeTable.currentRow() # Объявляем переменную row для хранения индекса выбранной строки 
        bikeId = self.bikeTable.item(row, 0).text() # Объявляем переменную bikeId для хранения значения столбца bikeId текущей строки
        if not self.crud.deleteBike(bikeId): MessageBoxWindow(title="Ошибка удаления ТС", text="SQLAlchemy: не удалось удалить строку", icon=QMessageBox.Icon.Warning) # Удаляем запись о текущем ТС из таблицу модели BikeModel
        else:
            self.bikeTable.removeRow(row) # Удаляем строку по индексу из виджета QTableWidget
            self.logger.infoLog(f"ТС с внутренним идентификатором {bikeId} было удалено") # Добавляем информационное сообщение о удалении ТС в виджет QListWidget
    
    def rowOperations(self, action) -> None:
        match action.text():
            case "Удалить ТС": self.deleteRow() # Вызываем метод deleteRow для удаления выбранного столбца
            case "Добавить ТС": InsertBikeWindow(logger=self.logger, table=self) # Инициализируем экземпляр класса InsertBikeWindow для добавления новой записи о ТС
        

class BikeInfoDock(QDockWidget):
    """
    Описание
        Класс BikeInfoDock — в контексте данного приложения представляет собой информационную
        форму, цель которой — отображение значений атрибутов объекта модели BikeModel, активируется
        при нажатии на столбец любой строки внутри виджета QTableWidget класса BikesTableDock.
        Основанный на виджете QDockWidget, класс BikeInfoDock предоставляет пользовалю возможность
        масштабирования и позиционирования виджета под собственные нужды, что является хорошим решением
        при создании виджетов подобного типа

    Структура класса BikeInfoDock
    |
    |————Конструктор (__init__(self, table))
    |    |
    |    |— Метод super().__init__() Инициализируем родительский класс QDockWidget
    |    |
    |    |— Метод setWindowTitle(title: str) Устанавливаем заголовок текущего виджета
    |    |
    |    |— Атрибут widget, содержит экземпляр класса QWidget. Представляет собой центральный виджет
    |    |  класса BikeInfoDock, и служит для хранения информационной формы
    |    |
    |    |— Атрибут generalLayout, содержит экземпляр класса макета QFormLayout
    |    |
    |    |— Атрибут bikeIdLabel, содержит экземпляр класса QLabel, служит для хранения и отображения
    |    |  внутреннего идентификатора ТС
    |    |
    |    |— Атрибут bikeTypeLabel, содержит экземпляр класса QLabel, используется для отображения и хранения
    |    |  типа выбранного ТС
    |    |
    |    |— Атрибут bikeModeLabel, содержит экземпляр класса QLabel, служит для хранения и отображения
    |    |  режима работы текущего ТС
    |    |
    |    |— Атрибут bikeSpeedLabel, содержит экземпляр класса QLabel, служит для отображения и хранения
    |    |  данных о текущей скорости ТС
    |    |
    |    |— Атрибут bikeSpeedLimitLabel, содержит экземпляр класса QLabel, служит для хранения и отображения
    |    |  текущего режима скоростного ограничения ТС
    |    |
    |    |— Атрибут bikeLatitudeLabel, содержит экземпляр класса QLabel, используется для отображения широты
    |    |  на которой находится выбранное ТС
    |    |
    |    |— Атрибут bikeLongitudeLabel, содержит экземпляр класса QLabel, используется для отображения долготы
    |    |  на которой находится текущий ТС
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLabel из атрибута bikeIdLabel в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLabel из атрибута bikeTypeLabel в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLabel из атрибута bikeSpeedLabel в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLabel из атрибута bikeSpeedLimitLabel в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLabel из атрибута bikeL в макет QFormLayout
    |    |
    |    |— Метод addRow(title: str, widget: QWidget) Добавляем экземпляр класса QLabel из атрибута bikeIdLabel в макет QFormLayout
    |    |
    |    |— Cигнал cellClicked связывающий атрибут bikeTable и метод setCurrentBikeInfo(self, row: int). Служит для отображения атрибутов
    |    |  ТС, при нажатии на один из столбцов его строки
    |    |
    |    |— Метод setLayout(layout: QFormLayout) Устанавливаем макет QFormLayout, в качестве макета родительского виджета
    |    |
    |    |— Метод setWidget экземпляра класса QDockWidget. Данный метод служит для установки центрального
    |    |  виджета QDockWidget
    |
    |— Метод setCurrentBikeInfo(self, row: int)
    |  |
    |  |— Переменная info, содержит в себе генератор списков, что итерируется по диапазону сгенерированному
    |  |  | встроенной функцией range(value: int) диапазону, элементы которого эквивалентны индексам столбцов
    |  |  | виджета QTableWidget
    |  |  |
    |  |  |— Метод item(row: int, column: int) экземпляра класса QTableWidget. В контексте метода setCurrentBikeInfo,
    |  |  |  служит для извлечения объектов QTableWidgetIte в выбранной строке по индексу. Для извлечения значений из
    |  |  |  экземпляров класса QTableWidgetItem используется метод text()
    |  |  |
    |  |
    |  |— Переменная labels, хранит в себе список ключей словаря, эквивалентного строению конструктора (__init__(self, table))
    |  |  и полученного через магический метод '__dict__'. Cлужит для дальнейшего использования внутри метода 
    |  |  setCurrentBikeInfo(self, row: int)
    |  |
    |  |— Генератор списков ([getattr(self, entry).setText(info[labels.index(entry)]) for entry in labels]) итерирующийся
    |  |  по списку ключей словаря конструктора что содержит переменная labels
    |  |  |
    |  |  |— Встроенная функция getattr(self, entry)
    |  |  |  Служит для получения экземпляра класса QLabel по имени его атрибута, далее ему присваивается значение из списка атрибута info через
    |  |  |  метод setText(text: str) экземпляра класса QLabel
    |  |  |
    |  |
    |

    """
    def __init__(self, table):
        super().__init__() # Инициализируем родительский класс QDockWidget
        self.setWindowTitle("Профиль ТО") # Устанавливаем заголовок DockWidget
        
        self.widget = QWidget() # Инициализируем атрибут widget хранящий экземпляр класса QWidget
        self.generalLayout = QFormLayout() # Инициализируем макет QFormLayout

        self.table = table # Инициализируем атрибут table хранящий экземпляр класса BikesTableDock

        self.bikeIdLabel = QLabel("ABC000") # Инициализируем атрибут bikeId хранящий экземпляр класса QLabel
        self.bikeTypeLabel = QLabel("NULL") # Инициализируем атрибут bikeTypeLabel хранящий экземпляр класса QLabel
        self.bikeModeLabel = QLabel("NULL") # Инициализируем атрибут bikeModeLabel хранящий экземпляр класса QLabel
        self.bikeSpeedLabel = QLabel("0") # Инициализируем атрибут bikeSpeedLabel хранящий экземпляр класса QLabel
        self.bikeSpeedLimitLabel = QLabel("0") # Инициализируем атрибут bikeSpeedLimitLabel хранящий экземпляр класса QLabel
        self.bikeLatitudeLabel = QLabel("0.000000") # Инициализируем атрибут bikeLatitudeLabel хранящий экземпляр класса QLabel
        self.bikelongitudeLabel = QLabel("0.000000") # Инициализируем атрибут bikelongitudeLabel хранящий экземпляр класса QLabel
        
        self.generalLayout.addRow("Внутренний идентификатор", self.bikeIdLabel) # Добавляем экземпляр класса QLabel в текущий макет формы 
        self.generalLayout.addRow("Тип ТС", self.bikeTypeLabel) # Добавляем в макет формы атрибут bikeTypeLabel хранящий экземпляр класса QLabel
        self.generalLayout.addRow("Режим ТС", self.bikeModeLabel)# Добавляем в макет формы атрибут bikeModeLabel хранящий экземпляр класса QLabel 
        self.generalLayout.addRow("Скорость (км/ч)", self.bikeSpeedLabel) # Добавляем в макет формы атрибут bikeSpeedLabel хранящий экземпляр класса QLabel
        self.generalLayout.addRow("Ограничение скорости (км/ч)", self.bikeSpeedLimitLabel) # Добавляем в макет формы атрибут bikeSpeedLimitLabel хранящий экземпляр класса QLabel
        self.generalLayout.addRow("Широта", self.bikeLatitudeLabel) # Добавляем в макет формы атрибут bikeLatitudeLabel хранящий экземпляр класса QLabel
        self.generalLayout.addRow("Долгота", self.bikelongitudeLabel) # Добавляем в макет формы атрибут bikelongitudeLabel хранящий экземпляр класса QLabel
        
        self.table.bikeTable.cellClicked.connect(self.setCurrentBikeInfo) # Устанавливаем сигнал cellClicked на атрибут bikeTable

        self.widget.setLayout(self.generalLayout) # Устанавливаем generalLayout в качестве макета родительского виджета с помощью метода setLayout()
        self.setWidget(self.widget) # Устанавливаем widget в качестве главного виджета родительского класса QDockWidget

    def setCurrentBikeInfo(self, row) -> None:
        info = [self.table.bikeTable.item(row, column).text() for column in range(7)] # Объявляем переменную info для хранения списка значений столбцов текущей строки
        labels = list(self.__dict__.keys())[3:] # Объявляем переменную labels что хранит названия атрибутов служащих для отображения информации о текущем ТС  
        [getattr(self, entry).setText(info[labels.index(entry)]) for entry in labels] # Устанавливаем атрибутам значения столбцов текущей записи о ТС
        

class BikeModelLogDock(QDockWidget):
    """
    Описание
        Класс BikeModelLogDock — представляет собой виджет-журнал, в который автоматически заносятся действия
        пользователя выполненные во время активной сессии работы с приложением. Данный виджет используется
        прежде всего для логирование операций, что подпадают под принцип CRUD (Create, Read, Update, Delete)
        т.е добавление, обновление, и удаление записей о ТС. Стоит отметить, что записи данного журнала не
        записываются ни в таблицу базы данных, ни в текстовый файл, данный функционал был опущен в угоду
        простоты понимания, однако в реальных аналогах данного виджета, производится обязательная запись
        событий в отдельную таблицу БД сервиса. Структура класса BikeModelLogDock представлена ниже

    Структура класса BikeModelLogDock
    |
    |————Конструктор (__init__(self))
    |    |
    |    |— Метод super().__init__() Инициализируем родительский класс QDockWidget
    |    |
    |    |— Метод setWindowTitle(title: str) Устанавливаем заголовок текущего виджета
    |    |
    |    |— Атрибут logList содержит экземпляр класса QListWidget, является центральным виджетом
    |    |  класса BikeModelLogDock, служит для хранения записей о действиях пользователя в текущей
    |    |  сессии работы с данным приложением
    |    |
    |    |— Метод setWidget экземпляра класса QDockWidget. Данный метод служит для установки центрального
    |    |  виджета QDockWidget
    |
    |— Метод infoLog(self, text: str)
    |  |
    |  |— Вызов метода addItem(item: str) экземпляра класса QListWidget. В контексте данного класса,
    |  |  служит для добавления записи о действии пользователя в журнал текущей сессии. Запись журнала
    |  |  имеет следующий формат:
    |  |
    |  |        [<точное время действия>] <текст информирующий о типе операции> <идентификатор ТС>
    |  |
    |
    """
    def __init__(self):
        super().__init__() # Инициализируем родительский класс QDockWidget
        self.setWindowTitle("Журнал событий текущей сессии") # Устанавливаем заголовок DockWidget
        
        self.logList = QListWidget() # Инициализируем атрибут logList хранящий экземпляр класса QListWidget

        self.setWidget(self.logList) # Устанавливаем атрибут logList в качестве родительского виджета QDockWidget
    
    def infoLog(self, text: str) -> None:
        self.logList.addItem(f"[{datetime.now().strftime('%H:%M:%S')}] {text}") # Добавляем информационную запись в журнал текущей сессии
    

class ApplicationGUI(QMainWindow):
    """
    Описание
        Класс ApplicationGUI — родительский класс данного приложения. Его основной функционал заключается
        в позиционировании элементов пользовательского интерфейса, а также инициализации и логическом обьединении
        классов описанных ранее. Помимо перечисленного ранее данный класс также инициализирует menuBar, что содержит
        ряд подменю, которые дают альтернативный способ доступа к инструментам ToolBar. Структура класса ApplicationGUI
        представлена ниже

    Структура класса ApplicationGUI
    |
    |————Конструктор (__init__(self))
    |    |
    |    |— Метод super().__init__() Инициализируем родительский класс QMainWindow
    |    |
    |    |— Метод setWindowTitle(title: str) Устанавливает заголовок родительского окна
    |    |
    |    |— Метод setWindowIcon(icon: QIcon) Устанавливает иконку родительского класса
    |    |
    |    |— Атрибут toolbar содержит экземпляр класса ActionToolBar. В парадигме данного приложения представляет собой
    |    |  панель инструментов содержащую инструменты добавления, а также удаления транспортных средств
    |    |
    |    |— Атрибут bikesLog хранит экземпляр класса BikeModelLogDock. Является описанным ранее виджетом-журналом, что
    |    |  сохраняет записи о всех операциях проведенных пользователем в период текущей сессии
    |    |
    |    |— Атрибут bikesTable содержит экземпляр класса BikesTableDock. Является наиболее обьемным классом в данном приложении
    |    |  с точки зрения концентрации логики и исполняемых функций. Содержит виджет QTableWidget, что отображает записи о ТС
    |    |  хранящиеся внутри таблицы модели BikeModel, а также логику взаимодействия с ORM SQLAlchemy через интерфейс ввиде класса
    |    |  CRUD(engine)
    |    |
    |    |— Атрибут bikesInfo содержит экземпляр класса BikeInfoDock. Как было сказано ранее в документации класса, что содержит данный
    |    |  атрибут, BikeInfoDock представляет собой информационную форму, которая отображает значения атрибутов выбранного в QTableWidget
    |    |  ТС посредством активации сигнала cellClicked т.е нажатия на одну из ячеек
    |    |
    |    |— Вызов метода addDockWidget(position: DockWidgetArea, dockWidget: QDockWidget) родительского класса QMainWindow.
    |    |  Служит для позиционирования виджета QDockWidget внутри области родительского окна. В качестве параметров принимает
    |    |  значения констант подкласса Qt — DockWidgetArea, и экземпляр класса QDockWidget
    |    |
    |    |— Вызов метода addDockWidget(position: DockWidgetArea, dockWidget: QDockWidget) родительского класса QMainWindow.
    |    |  Служит для позиционирования виджета BikeInfoDock внутри области родительского окна
    |    |
    |    |— Вызов метода addDockWidget(position: DockWidgetArea, dockWidget: QDockWidget) родительского класса QMainWindow.
    |    |  Служит для позиционирования виджета BikeModelLogDock внутри области родительского окна
    |    |
    |    |— Вызов метода initMenuBar() Данный метод принадлежит к классу ApplicationGUI, и служит для инициализации menuBar
    |    |
    |    |— Вызов метода addToolBar(toolbar: QToolBar) родительского класса QMainWindow, используется для добавления панели
    |    |  инструментов (QToolBar) в родительское окно (QMainWindow)
    |    |
    |    |— Cигнал actionTriggered связывающий атрибут toolbar и метод rowOperations(self, action: QAction). Служит для установки
    |    |  связи между панелью инструментов, и классами что исполнют функции инструметов внутри панели
    |    |
    |
    |————Метод initMenuBar(self)
    |    |
    |    |— Переменная menuBar, содержит экземпляр класса QMenuBar, что представляет собой главное меню родительского окна QMainWindow
    |    |
    |    |— Переменная fileMenu содержит экземпляр класса QMenu, является дочерним меню экземпляра класса QMenuBar
    |    |
    |    |— Переменная editMenu хранит экземпляр класса QMenu, представляет собой дочернее меню экземпляра класса QMenuBar
    |    |
    |    |— Переменная aboutMenu содержит результат выполнения метода addMenu(title: str), является дочерним меню экземпляра класса QMenuBar
    |    |
    |    |
    |    |— Переменная exitAction содержит экземпляр класса QAction(title: str, self), представляет собой действие (activity)
    |    |  что должно быть добавлено в подменю fileMenu
    |    |
    |    |— Переменная addAction содержит экземпляр класса QAction(title: str, self), является действием предназначенным для
    |    |  для добавления в подменю editMenu
    |    |
    |    |— Переменная deleteAction содержит экземпляр класса QAction(title: str, self), предназначено для добавления в подменю
    |    |  editMenu
    |    |
    |    |— Переменная aboutAction хранит экземпляр класса QAction(title: str, self), является действием что должно быть добавлено
    |    |  в подменю aboutMenu
    |    |
    |    |— Cигнал triggered связывающий атрибут exitAction и метод close() родительского виджета QMainWindow. Служит для закрытия данного приложения
    |    |
    |    |— Cигнал triggered устанавливающий связь между атрибутом addAction и методом showInsertDialog. Используется для отображения диалогового окна
    |    |  InsertBikeWindow
    |    |
    |    |— Cигнал triggered связывающий атрибут deleteAction и метод deleteRow(self) экземпляра класса BikesTableDock. Служит для вызова метода deleteRow(self)
    |    |  что удаляет строку выбранную в данный момент
    |    |
    |    |— Cигнал triggered используется для установки связи между атрибутом aboutAction и методом showAboutWindow(self) родительского окна. Служит для вызова метода
    |    |  showAboutWindow(self), который отображает диалоговое окно содержащее справочную информацию о данной программе
    |    |
    |    |— Вызов метода addAction(action: QAction) экземпляра класса QMenuBar. Служит для добавления экземпляра класса QAction в родительское меню fileMenu
    |    |
    |    |— Вызов метода addAction(action: QAction) экземпляра класса QMenuBar. Добавляет экземпляр класса QAction в родительское меню editMenu
    |    |
    |    |— Вызов метода addAction(action: QAction) экземпляра класса QMenuBar. Служит для добавления экземпляра класса QAction в родительское меню editMenu
    |    |
    |    |— Вызов метода addAction(action: QAction) экземпляра класса QMenuBar. Добавляет экземпляр класса QAction в родительское меню aboutMenu
    |    |
    |
    |————Метод showInsertDialog(self)
    |    |
    |    |— Экземпляр класса InsertBikeWindow(logger: BikeModelLogDock, table: BikesTableDock) Отображает диалоговое окно для добавления новой записи о ТС
    |    |
    |
    |————Метод showInsertDialog(self)
    |    |
    |    |— Экземпляр класса AboutWindow, служит для отображения диалогового окна с справочной информацией при активации сигнала triggered, атрибута aboutAction
    |    |
"""
    def __init__(self):
        super().__init__() # Инициализируем родительский класс QMainWindow
        self.setWindowTitle("Панель управления сервиса аренды") # Устанавливаем заголовок текущего окна
        self.setWindowIcon(QIcon("./images/scooter.png")) # Устанавливаем иконку текущего окна c помощью экземпляра класса QIcon
        self.toolbar = ActionToolBar() # Инициализируем атрибут toolbar хранящий экземпляр класса ActionToolBar
        self.bikesLog = BikeModelLogDock() # Инициализируем атрибут bikesLog хранящий экземпляр класса BikeModelLogDock
        self.bikesTable = BikesTableDock(logger=self.bikesLog) # Инициализируем атрибут bikesTable хранящий экземпляр класса BikesTableDock
        self.bikesInfo = BikeInfoDock(table=self.bikesTable) # Инициализируем атрибут bikesInfo хранящий экземпляр класса BikeInfoDock

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.bikesTable) # Добавляем в родительское окно экземпляр класса QDockWidget с позиционированием в левой части окна
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.bikesInfo) # Добавляем в родительское окно экземпляр класса QDockWidget с позиционированием в правой части окна
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.bikesLog) # Добавляем в родительское окно экземпляр класса QDockWidget с позиционированием в правой части окна

        self.initMenuBar() # Инициализируем верхнее меню главного окна
        self.addToolBar(self.toolbar) # Добавляем экземпляр класса ActionToolBar, в качестве панели инструментов
        
        self.toolbar.actionTriggered.connect(self.bikesTable.rowOperations) # Устанавливаем сигнал actionTriggered на атрибут toolbar

    def initMenuBar(self) -> None:
        menuBar = self.menuBar() # Объявляем переменную menuBar хранящую объект menuBar
        
        fileMenu = menuBar.addMenu("Главная") # Объявляем переменную fileMenu хранящую объект главного меню 
        editMenu = menuBar.addMenu("Действия") # Объявляем переменную fileMenu хранящую объект меню действий
        aboutMenu = menuBar.addMenu("Справка") # Объявляем переменную aboutMenu хранящую объект информационного меню
        
        exitAction = QAction("Выйти", self) # Объявляем переменную exitAction хранящую экземпляр класса QAction
        addAction = QAction("Добавить ТС", self) # Объявляем переменную addAction хранящую экземпляр класса QAction
        deleteAction = QAction("Удалить ТС", self) # Объявляем переменную deleteAction хранящую экземпляр класса QAction
        aboutAction = QAction("О программе", self) # Объявляем переменную aboutAction хранящую экземпляр класса QAction
        
        exitAction.triggered.connect(self.close) # Устанавливаем сигнал triggered на атрибут exitAction
        addAction.triggered.connect(self.showInsertDialog) # Устанавливаем сигнал triggered на атрибут addAction
        deleteAction.triggered.connect(self.bikesTable.deleteRow) # Устанавливаем сигнал triggered на атрибут deleteAction
        aboutAction.triggered.connect(self.showAboutWindow) # Устанавливаем сигнал triggered на атрибут aboutAction
        
        fileMenu.addAction(exitAction)  # Добавляем атрибут exitAction, хранящий действие закрытия приложения в родительское меню fileMenuединен
        editMenu.addAction(addAction) # Добавляем атрибут addAction, хранящий действие добавления нового ТС в родительское меню editMenu
        editMenu.addAction(deleteAction) # Добавляем атрибут deleteAction, хранящий действие удаления записи о ТС в родительское меню editMenu
        aboutMenu.addAction(aboutAction) # Добавляем атрибут exitAction, хранящий действие отображения справочной информации в родительское меню aboutMenu
        
    def showInsertDialog(self) -> None:
        InsertBikeWindow(logger=self.bikesLog, table=self.bikesTable) # Инициализируем экземпляр класса InsertBikeWindow

    def showAboutWindow(self) -> None:
        AboutWindow(title="О программе", text="<b>Панель управления сервиса аренды</b> — представляет собой учебное ПО, служит для <br>демонстрации принципа CRUD (Create, Read, Update, Delete) основано на ORM <br>SQLAlchemy, и графическом фреймворке PyQt6") # Инициализируем экземпляр класса AboutWindow


def initDatabaseModel() -> None:
    crud = CRUD(create_engine("sqlite:///ormproto.db")) # Инициализируем переменную crud, что содержит экземпляр класса CRUD для работы с ORM
    crud.initModel() # При необходимости инициализируем модель BikeModel объявленную ранее

def main() -> None:
    initDatabaseModel() # Инициализируем модель BikeModel в случае ее отсутствия
    app = QApplication(argv) # Инициализируем экземпляр класса QApplication, представляющий собой текущее приложение
    gui = ApplicationGUI() # Инициализируем экземпляр класса ApplicationGUI, что является главным окном в рамках нашего приложения
    gui.show() # Отображаем родительское окно
    app.exec() # Запускаем приложение


if __name__ == '__main__': main()
