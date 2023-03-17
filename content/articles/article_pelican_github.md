Title: Pelican публикация сайта на Github
Date: 2023-03-17 00:01
Author: Sitala
Tags: github, pelican, site, publish
Cover: /images/pelican_github1.png
Summary:

[TOC]

#### Перевод части статьи [How I Build This Site - Part 7][1] , автор «Peter Kazarinoff»

[1]:https://pythonforundergradengineers.com/how-i-built-this-site-7.html

### Измените файл *publishconf.py* для использования **github pages url**

Нам необходимо отредактировать publishconf.py и добавить наш github pages url в `SITEURL` и установить `RELATIVE_URLS` в True. Строки для изменения:

    :::Python
    #publishconf.py
    SITEURL = 'https://username.github.io/staticsite'
    RELATIVE_URLS = True

Убедитесь, что вы установили `username` вашего github user name. `RELATIVE_URLS = True`. Это необходимо для работы ссылок на сайте и запуска css и javascript файлов на github pages. Когда я в начале установил `RELATIVE_URLS = False`, сайт выглядел ужасающе, без форматирования css и без каких-либо рабочих ссылок. Установка `RELATIVE_URLS = True`, исправила эту проблему.

### Создайте опубликованную версию сайта
До этого момента мы использовали команду `make html` для сборки демо версии нашего сайта. Сейчас мы готовы опубликовать наш сайт. Мы публикуем наш сайт запуском команд:

    :::bash
    (staticsite) $ pelican content -s publishconf.py

Это создает опубликованную версию сайта с относительными путями в директории **output**.

### Add, commit, push в ветку main на github
Перед тем как мы сможем разместить версию нашего сайта на github pages, нам необходимо сохранить текущую версию на ветку main.

    :::bash
    (staticsite) $ git add .
    (staticsite) $ git commit -m "first published version"
    (staticsite) $ git push origin master

### Создание **gh-pages** ветки в нашем репозитории статического сайта на github
До этого момента, мы сохранили нашу работу в ветку **master** в репозитории staticsite на github. Чтобы разместить сайт на github pages, на необходимо создать новую ветку в репозитории **staticsite** с названием **gh-pages**. 
В ветке **main** все еще находится наш код, настройки, разметки файлов, блокноты, изображения и так далее для создания сайта. Однако, на ветке **gh-pages** репозитория **staticsite** repo любой html, css или файлы javascript будут обслуживаться как обычный вебсайт. Чтобы создать новую ветку, перейдите на главную страницу репозитория **staticsite** github и нажмите в раскрывающемся меню [Branch: Master] в верхнем левом углу. Введите имя новой ветки: **gh-pages**.

### Используйте **ghp-import** чтобы отправить содержимое в директорию **output** в ветку **gh-pages**
Как показано в документации [Pelican][2], вы можете использовать Python пакет с названием `ghp-import` чтобы помочь опубликовать содержимое каталога output в ветке `gh-pages` нашего репозитория на gitgub. Если `ghp-import` еще не инсталлирован используйте `pip`. Убедитесь, что вы находитесь в виртуальном окружении среды python, когда вы запускаете `pip`.

[2]:https://docs.getpelican.com/en/stable/tips.html

    :::bash
    (staticsite) $ pip install ghp-import

Теперь мы будем использовать ghp-import пакет, который поможет нам опубликовать сайт.  Команда `ghp-import output` назначит содержимое каталога **output** на ветку **gh-pages** нашего локального репозитория. Мы отправляем `push` содержимое локальной ветки `gh-pages` в удаленную ветку `gh-page` на github.

    :::bash
    (staticsite) $ ghp-import output
    (staticsite) $ git push origin gh-pages

У меня были проблемы с этими командами. В зависимости от компьютера который я использовал. Я бы получил следуюшую ошибку:

    :::bash
    ! [rejected]        gh-pages -> gh-pages (fetch first)
    error: failed to push some refs to 'https://github.com/professorkazarinoff/staticsite.git'
    hint: Updates were rejected because the remote contains work that you do
    hint: not have locally. This is usually caused by another repository pushing
    hint: to the same ref. You may want to first integrate the remote changes
    hint: (e.g., 'git pull ...') before pushing again.
    hint: See the 'Note about fast-forwards' in 'git push --help' for details.

Я пытался выполнить `git stash` но это не работало. Я также пытался `git pull origin gh-pages` но это закончилось тем, что все было помещено из директории **output** в мой корневой каталог **staticsite** и привело к большому беспорядку.

Способ которым я обошел это было использование `-f` (force) флаг. Я не думаю что это наиболее элегантный или предпочтительный путь передать содержимое контента **output** каталога в ветку **gh-pages**. Я просто действительно не понимаю как `git` работает достаточно хорошо, чтобы знать, как обойти проблему без *forced* commit. Если вы получаете ошибку попробуйте:

    :::bash
    (staticsite) $ pelican content -s publishconf.py

    (staticsite) $ git add .
    (staticsite) $ git commit -m "published"
    (staticsite) $ git push origin master

    (staticsite) $ ghp-import output
    (staticsite) $ git push -f origin gh-pages

Что работало до сих пор для меня.

### Посмотрите сайт на github pages

Потрясающе! Теперь сайт размещен и доступен к просмотру для всех. Довольно круто верно? Укажите в браузере URL-адрес страниц github и посмотрите:

`https://username.github.io/staticsite`