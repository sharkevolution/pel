Title: Страница ошибки 404 по умолчанию в Django
Date: 2023-03-21 00:01
Author: Sitala
Tags: django, error, 404
Cover: /images/error-404-not-found.png
Summary:


### Как добавить страницу по умолчанию Error 404 Django

Ошибка 404 одна из наиболее распространенных ошибок что случается. Важно, чтобы пользователь "не завис" и понял, что делать дальше без кнопки CTA (призыва к действию). В примере ниже у пользователя будет плохой пользовательский опыт и скорее всего он закроет страницу.

![picture]({static}../images/django/nginx_404.jpg)

Чтобы избежать плохого взаимодействия с пользователем, мы можем отобразить пользовательскую страницу 404 с некоторой информацией которая поможет пользователю, а не просто закрыть сайт. 

В Django легко написать пользовательскую страницу логики для ошибки 404

Перейдите в главный файл **urls.py** проекта и добавьте следующий фрагмент:

	:::python
    # yourproject/url.py
    handler404 = "yourproject.views.handler404"

Теперь нам необходимо добавить функцию для отображения страницы 404, в файл **views.py** вашего приложения.
 
	:::python
	def handler404(request, *args, **argv):
		response = render(request, '404.html')
		response.status_code = 404
		return response

В приведенной выше функции мы отображаем пользовательский шаблон страницы **404.html** и передаем `404 status_code`.

Создайте файл **404.html** в папке **templates** вашего приложения:

	:::html
	<!DOCTYPE html>
	<html>
	<title>Wrong address</title>

	<body>
		<h1>Ooops!</h1>
		<h2>I cannot find the file you requested!</h2>
	</body>
	</html>

Вот и все. Теперь у вас есть пользовательская страница 404 по умолчанию для всех запросов, которые ранее выдавали error 404.
