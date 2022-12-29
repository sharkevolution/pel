Title: Создание тепловой карты в QGIS
Date: 2021-11-24 20:20
Author: Sitala
Tags: qgis
Cover: /images/hexagon.png
Summary:

## Описание краткого порядка действий для создания тепловой карты QGIS

#### Step by Step

* Для необходимого точечного слоя, выбираем **Вектор > Анализ > Создать сетку**

![picture]({static}../images/qgis/create_grid.jpg)

* На форме выбираем поля как указано на рисунке ниже

![picture]({static}../images/qgis/create_grid1.png)

* Результат работы алгоритма, созданая сетка

![picture]({static}../images/qgis/create_grid2.png)

* Переходим в "Инструменты анализа" **Выбрать по расположению**

![picture]({static}../images/qgis/create_grid3.png)

* Результат работы алгоритма, сетка с выделенными кластерами в зонах пересечения объектов

![picture]({static}../images/qgis/create_grid4.png)

* Экспортируем и сохраняем выделенные объекты

![picture]({static}../images/qgis/create_grid_4-5.png)

* Выбираем новый слой и переходим в "Инструменты анализа" **Подсчет точек в полигоне**

![picture]({static}../images/qgis/create_grid5.jpg)

* На форме выбираем поля как указано на рисунке ниже

![picture]({static}../images/qgis/create_grid6.jpg)

* Результат работы алгоритма, созданая тепловая карта с символизацией по диапазонам значений

