Title: Документация как код 
Date: 2023-07-28 00:01
Author: Sitala
Tags: sphinx, docs, python 
Cover: /images/docs_as_code.png
Summary:

[TOC]

# Разработка технической документации с использованием инструментов и процессов, что и написание кода:

Довольно часто, качественное описание документации занимает много времени, а поддержка в актуальном состоянии требует постоянных трудозатрат. При небольшом объеме проекта, просто использовать всем знакомые текстовые процессоры и редакторы. Но в один прекрасный день, я осознал, что немогу быть эффективным при описании системы в промышленных масштабах. 

>Скорость, удобочитаемость, поддержка, автоматизация и доступность, - это те вещи которые желаешь видеть, но не знаешь как реализовать.

Можно ли это автоматизировать и создать отличный статический веб-сайт, описывающий документацию? 

Да. И вот где приходит на помощь Sphinx!

### Что такое Sphinx?

Sphinx — это генератор документации на Python, преобразующий файлы в формате **reStructuredText** в HTML website и другие форматы. Он использует ряд расширений для reStructuredText.

### Инсталяция Sphinx?

Выполните следующий код в терминале в виртуальном окружении python

	:::python
    pip install sphinx sphinx_rtd_theme

### Создание структуры папок

	:::bash
    sphinx_basic
    |-docs
    |-infor
      |-__init__.py
      |-add.py
      |-divide.py
      |-multiply.py
      |-substract.py
    |-venv

Папка `docs` необходима для создания проекта с использованием Sphinx, название папки не имеет значения. Папка `infor` будет служить для хранения кода который мы вставим позже в сгененрированные файлы документации в папке `docs`.

### Шаг1: Sphinx-quickstart

В терминале перейдите в папку `docs`, выполните следующую команду в терминале с запущеннім виртуальным окружением python

    :::python
    sphinx-quickstart

`sphinx-quickstart` — это интерактивный инструмент, который задает несколько вопросов о вашем проекте, а затем создает полный каталог документации вместе с файлом make.bat, который позже будет использоваться для создания HTML.

### Шаг2: Отредактируйте conf.py file

Добавьте следующие строки в начало файла, после текстового описания

	:::python
    import os
    import sys
    sys.path.insert(0, os.path.abspath('..'))

os.path.abspath('..') сообщаем sphinx, что код находится за пределами текущей папки docs.
Добавьте расширения, указанные ниже:

    :::python
    extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.viewcode',
        'sphinx.ext.napoleon'
    ]

Далее, перейдите к темам и замените `alabaster` на `sphinx_rtd_theme`. Полный обновленный файл `conf.py` приведен ниже:

    :::python
    # Configuration file for the Sphinx documentation builder.
    #
    # For the full list of built-in configuration values, see the documentation:
    # https://www.sphinx-doc.org/en/master/usage/configuration.html

    # -- Project information -----------------------------------------------------
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

    import os
    import sys
    sys.path.insert(0, os.path.abspath('..'))


    project = 'infor'
    copyright = '2023, Sitala'
    author = 'Sitala'
    release = '00.00.01'

    # -- General configuration ---------------------------------------------------
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

    extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.viewcode',
        'sphinx.ext.napoleon'
    ]

    templates_path = ['_templates']
    exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

    language = 'ru'

    # -- Options for HTML output -------------------------------------------------
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

    html_theme = 'sphinx_rtd_theme'
    html_static_path = ['_static']


### Шаг3: Генерация .rst files

До сих пор в вашей папке документов был `index.rst`, который будет целевой страницей вашей документации. Но мы не сгенерировали infor.rst, в котором есть наш код на Python.

Перейдите в родительскую папку `sphinx_basics` и выполните команду:

    :::bash
    sphinx-apidoc -o docs infor/


По этой команде sphinx берет наш код из папки `infor` и выводит сгенерированные файлы .rst в папку `docs`. После чего вы увидите файлы `infor.rst` и `modules.rst`, сгенерированные в ваших документах.

### Шаг4: Включение module.rst и создание html

Теперь включите сгенерированный файл `modules.rst` в свой `index.rst`. Добавьте строчку `modules`

    :::bash
    .. tets documentation master file, created by
    sphinx-quickstart on Fri Jul 28 19:38:14 2023.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

    Welcome to tets's documentation!
    ================================

    .. toctree::
    :maxdepth: 2
    :caption: Contents:

    modules

    Indices and tables
    ==================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`


Теперь все готово для создания красивой документации, зайдите в папку с документами и выполните команду

    :::bash
    make html

Вот и все!!!. Вы можете увидеть файлы HTML, сгенерированные внутри вашей папки _build в документах. Также, в дополнение к этому, вы можете искать любые методы, подпакеты и т. д. на странице поиска. 

Вся тяжелая работа по созданию HTML-документации была сделана Sphinx.

Теперь предположим, что вы внесли некоторые изменения в свой код и теперь хотите перестроить этот HTML. Перейдите в папку с документами и напишите

    :::bash
    make clean html
    make html

Эти команды перестроят ваши HTML-коды с учетом ваших изменений.

Ура! Мы успешно автоматизировали сборку части документации.

Ссылка на [документацию Sphinx][1]

[1]:https://www.sphinx-doc.org/en/master/index.html