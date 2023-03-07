Title: Excel самое необходимое
Date: 2023-03-08 00:01
Author: Sitala
Tags: excel, automation, analytics
Cover: /images/rocket404.png
Summary:

## Базовые инструменты для работы в Excel 
> В настоящее время ооочень мнооого инфы по Excel, поэтому кому нужно еще одно руководство смело закрывайте, здесь будет краткое описание и только самое необходимое для комфортной работы.

### Преобразование текста в число
В случае когда вам необходимо преобразовать число или дату в текстовом формате, нам необходимо выполнить несколько шагов:

1. В любую ячейку записываем  **`1`**
2. Копируем ячейку **`Ctrl+C`**
3. Выделяем диапазон для преобразования
4. В контекстном меню, специальная вставка
5. На форме выбираем умножить или разделить.

![picture]({static}../images/excel/ex01.png)

![picture]({static}../images/excel/ex02.png)

Результат:

![picture]({static}../images/excel/ex03.png)
***

### Заполнение диапазона значениями с «шагом»
Для заполнения ячеек необходимо:

1. Вставить например в ячейку A1 = 1, в ячейку A2 = 3
2. Выделить 2 ячейки, 
3. В правом нижнем углу последней ячейки (когда появится указатель +), зажать левую клавишу мыши
4. Тащить вниз. 

Пример:

![picture]({static}../images/excel/ex04.png)
 
Результат:

![picture]({static}../images/excel/ex05.png)
***

### Отключаем ссылки R1C1
Как убрать вид формул ```=RC[-1]/RC[-3]```

1. Открыть вкладку файл
2. Выбрать параметры
3. На форме снять флажок

![picture]({static}../images/excel/ex06.png)

***
### Сопоставление данных
Кратко о поиске по ключу

##### Составной ключ
Очень часто возникает потребность сопоставлять данные по нескольким полям, которые будут являться уникальным ключем для поиска.
Используйте для объединение полей, знак амперсанд ```"&"```

![picture]({static}../images/excel/ex07.png)


##### Убираем пробелы в начале и конце текста
Часто при поиске, внешний вид ключей совпадает, но по факту в конце одной из строк может быть например "пробел", в результате поиск не даст желаемого результата. Удалите перед поиском пробелы, для этого используем формулу =СЖПРОБЕЛЫ()


##### ВПР
Формула ВПР имеет ограничения, для поиска данных в вашей таблице, ключ должен находится всегда в первом столбце, иначе ничего найдено не будет. Поэтому желательно использовать формулу ```(ИНДЕКС + ПОИСКПОЗ)```.


##### ИНДЕКС+ПОИСКПОЗ
Это комбинация универсальная, и позволяет искать значения без привязки к первому столбцу таблицы поиска, как в случае с ВПР.

![picture]({static}../images/excel/ex08.png)
***

### Условное форматирование
Пример простого автоматического форматирования текста. Единственное ограничение, на большом массиве данных, будет тормозить.. 

![picture]({static}../images/excel/ex09.png)
***

### Формула ЕСЛИ


### Сводная таблица

####Отключение автоматического изменения ширины столбцов в сводной

#### Макеты сводной таблицы

#### Значения МИН, МАКС, среднее, количество

#### Разгруппировать даты в сводной


### Множественная сортировка


### Фильтрация

####Добавить выделенный фрагмент в фильтр


### Текст по столбцам


### Выбор пустых ячеек


### Формат по образцу


### Копировать как рисунок


### Печать

#### Вид страничный режим

#### Напечатать выделенный фрагмент



### Переводчик функций в Excel






