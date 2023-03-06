Title: Введение в Django Channels
Date: 2023-03-07 00:01
Author: Sitala
Tags: django, python, channels
Cover: /images/b1922774.png
Summary:

В этом примере мы будем создавать реал-тайм приложение чата с использованием Django Channels, фокусируясь на том, как интегрировать Django с Django Channels.

> Зачем еще один чат? Ну хорошо, чат это самый легкий способ показать силу Channels. Тем не менее, это руководство выходит за рамки основ, осуществляя множество типов запросов, сообщения/постоянство чата, и личные сообщения (один на один). После прохождения руководства, вы будете способны собрать приложение реального времени. 

## ЧТО ТАКОЕ DJANGO CHANNELS?
Django Channels (или просто Channels) расширяет встроенные возможности Django позволяя Django проектам управлять не только HTTP протоколами но и протоколами что требуют длительных соединений, таких как WebSockets, MQTT (IoT), chatbots, radios, и другими приложениями реального времени. Помимо этого, он обеспечивает поддержку основных функций Django, таких как аутентификация и сеансы.

Базовая настройка каналов выглядит примерно так:
![picture]({static}../images/django/channels/django_channels_structure.png)

>Чтобы больше изучить Channels, ознакомьтесь с вводным руководством из официальной документации.

## СИНХРОННОСТЬ VS АСИНХРОННОСТЬ
Какая разница между Channels и Django, нам будет необходимо часто переключаться между sync (синхронным) и async (асинхронным) выполнением кода. Например, доступ к базе данных Django необходимо осуществлять с помощью синхронного кода в то время, как к слою каналов Channels необходим доступ с использованием асинхронного кода.

Самый легкий путь переключится между ними, использовать в строенный в Django asgiref (asgiref.sync) функции:
1.	sync_to_async – принимает синхронную функцию и возвращает асинхронную функцию в которую обернута синхронная.
2.	async_to_sync – принимает асинхронную функцию и возвращает синхронную.

> Не волнуйтесь пока на счет этого, мы покажем практический пример позже в этом руководстве.

## НАСТРОЙКА ПРОЕКТА
Опять же, мы будем создавать чат. В приложении будет много комнат, где аутентифицированной пользователь может использовать чат. Каждая комната будет иметь список реально подключенных пользователей. Мы также реализуем личную переписку, один на один.

### НАСТРОЙКА ПРОЕКТА DJANGO
Начнем с создания новой директории и установки нового проекта Django:

    :::bash
	$ mkdir django-channels-example && cd django-channels-example
	$ python3.9 -m venv env
	$ source env/bin/activate

	(env)$ pip install django==4.0
	(env)$ django-admin startproject core .

После чего, создаем новое приложение Django с названием ```chat```:

	:::bash
	(env)$ python manage.py startapp chat

Регистрируем приложение в *core/settings.py* под ```INSTALLED_APPS```:

    :::python
	# core/settings.py

	INSTALLED_APPS = [
		'django.contrib.admin',
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.messages',
		'django.contrib.staticfiles',
		'chat.apps.ChatConfig',  # new
	]

### СОЗДАНИЕ DATABASE MODELS
Далее, давайте создадим две модели Django, ```Room``` и ```Message```, в *chat/models.py*:

	:::python
	# chat/models.py

	from django.contrib.auth.models import User
	from django.db import models


	class Room(models.Model):
		name = models.CharField(max_length=128)
		online = models.ManyToManyField(to=User, blank=True)

		def get_online_count(self):
			return self.online.count()

		def join(self, user):
			self.online.add(user)
			self.save()

		def leave(self, user):
			self.online.remove(user)
			self.save()

		def __str__(self):
			return f'{self.name} ({self.get_online_count()})'


	class Message(models.Model):
		user = models.ForeignKey(to=User, on_delete=models.CASCADE)
		room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
		content = models.CharField(max_length=512)
		timestamp = models.DateTimeField(auto_now_add=True)

		def __str__(self):
			return f'{self.user.username}: {self.content} [{self.timestamp}]'


##### ЗАМЕТКИ:
1. ```Room``` представляет комнату чата. Она содержит поле online для отслеживания когда пользователи подключаются и отключаются от чата.
2. ```Message``` представляет сообщение отправленное в чат. Мы будем использовать эту модель для хранения всех сообщений, отправленных в чат. 

Запустите ```makemigrations``` и ```migrate``` команды для синхронизации базы данных:
	
	:::bash
	(env)$ python manage.py makemigrations
	(env)$ python manage.py migrate

Регистрируем модели в *chat/admin.py* для того, чтобы они были доступны в административной панели Django:

	:::python
	# chat/admin.py

	from django.contrib import admin

	from chat.models import Room, Message

	admin.site.register(Room)
	admin.site.register(Message)

### ПРЕДСТАВЛЕНИЯ И URLs АДРЕСА
У веб приложения будет два следующих URLs:

1. /chat/ - селектор чат комнаты
2. /chat/<ROOM_NAME>/ - комната чата

Добавьте следующие представления в *chat/views.py*:

	:::python
	# chat/views.py
	from django.shortcuts import render

	from chat.models import Room


	def index_view(request):
		return render(request, 'index.html', {
			'rooms': Room.objects.all(),
		})


	def room_view(request, room_name):
		chat_room, created = Room.objects.get_or_create(name=room_name)
		return render(request, 'room.html', {
			'room': chat_room,
		})

Создайте файл *urls.py* в директории ```chat```:

	:::python
	# chat/urls.py

	from django.urls import path

	from . import views

	urlpatterns = [
		path('', views.index_view, name='chat-index'),
		path('<str:room_name>/', views.room_view, name='chat-room'),
	]

Обновите *urls.py* на уровне проекта с приложением чата:

	:::python
	# core/urls.py

	from django.contrib import admin
	from django.urls import path, include

	urlpatterns = [
		path('chat/', include('chat.urls')),  # new
		path('admin/', admin.site.urls),
	]

### ШАБЛОНЫ И СТАТИЧЕСКИЕ ФАЙЛЫ
Создайте файл *index.html* внутри папки с названием” templates” в папке “chat”:

	:::html
	<!-- chat/templates/index.html -->

	{% load static %}

	<!DOCTYPE html>
	<html lang="en">
		<head>
			<title>django-channels-chat</title>
			<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
			<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.min.js"></script>
			<style>
				#roomSelect {
					height: 300px;
				}
			</style>
		</head>
		<body>
			<div class="container mt-3 p-5">
				<h2>django-channels-chat</h2>
				<div class="row">
					<div class="col-12 col-md-8">
						<div class="mb-2">
							<label for="roomInput">Enter a room name to connect to it:</label>
							<input type="text" class="form-control" id="roomInput" placeholder="Room name">
							<small id="roomInputHelp" class="form-text text-muted">If the room doesn't exist yet, it will be created for you.</small>
						</div>
						<button type="button" id="roomConnect" class="btn btn-success">Connect</button>
					</div>
					<div class="col-12 col-md-4">
						<label for="roomSelect">Active rooms</label>
						<select multiple class="form-control" id="roomSelect">
							{% for room in rooms %}
								<option>{{ room }}</option>
							{% endfor %}
						</select>
					</div>
				</div>
			</div>
			<script src="{% static 'index.js' %}"></script>
		</body>
	</html>


Далее, добавьте *room.html* в туже самую папку:

	:::html
	<!-- chat/templates/room.html -->

	{% load static %}

	<!DOCTYPE html>
	<html lang="en">
		<head>
			<title>django-channels-chat</title>
			<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
			<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.min.js"></script>
			<style>
				#chatLog {
					height: 300px;
					background-color: #FFFFFF;
					resize: none;
				}

				#onlineUsersSelector {
					height: 300px;
				}
			</style>
		</head>
		<body>
			<div class="container mt-3 p-5">
				<h2>django-channels-chat</h2>
				<div class="row">
					<div class="col-12 col-md-8">
						<div class="mb-2">
							<label for="chatLog">Room: #{{ room.name }}</label>
							<textarea class="form-control" id="chatLog" readonly></textarea>
						</div>
						<div class="input-group">
							<input type="text" class="form-control" id="chatMessageInput" placeholder="Enter your chat message">
							<div class="input-group-append">
								<button class="btn btn-success" id="chatMessageSend" type="button">Send</button>
							</div>
						</div>
					</div>
					<div class="col-12 col-md-4">
						<label for="onlineUsers">Online users</label>
						<select multiple class="form-control" id="onlineUsersSelector">
						</select>
					</div>
				</div>
				{{ room.name|json_script:"roomName" }}
			</div>
			<script src="{% static 'room.js' %}"></script>
		</body>
	</html>

Сделаем наш код более читабельным, мы включим JavaScript код в отдельные файлы – *index.js* и *room.js*, соответственно. Так как мы не можем получить доступ к контексту Django в JavaScript, мы можем использовать json_script шаблон тега для хранения ```room.name``` и потом получить его в JavaScript файле.

В папке "chat" создайте папку с названием "static". Затем, в папке "static", создайте файлы *index.js* и *room.js*.

Содержимое *index.js*:

	:::javascript
	// chat/static/index.js

	console.log("Sanity check from index.js.");

	// focus 'roomInput' when user opens the page
	document.querySelector("#roomInput").focus();

	// submit if the user presses the enter key
	document.querySelector("#roomInput").onkeyup = function(e) {
		if (e.keyCode === 13) {  // enter key
			document.querySelector("#roomConnect").click();
		}
	};

	// redirect to '/room/<roomInput>/'
	document.querySelector("#roomConnect").onclick = function() {
		let roomName = document.querySelector("#roomInput").value;
		window.location.pathname = "chat/" + roomName + "/";
	}

	// redirect to '/room/<roomSelect>/'
	document.querySelector("#roomSelect").onchange = function() {
		let roomName = document.querySelector("#roomSelect").value.split(" (")[0];
		window.location.pathname = "chat/" + roomName + "/";
	}
	
Содержимое *room.js*:

	:::javascript
	// chat/static/room.js

	console.log("Sanity check from room.js.");

	const roomName = JSON.parse(document.getElementById('roomName').textContent);

	let chatLog = document.querySelector("#chatLog");
	let chatMessageInput = document.querySelector("#chatMessageInput");
	let chatMessageSend = document.querySelector("#chatMessageSend");
	let onlineUsersSelector = document.querySelector("#onlineUsersSelector");

	// adds a new option to 'onlineUsersSelector'
	function onlineUsersSelectorAdd(value) {
		if (document.querySelector("option[value='" + value + "']")) return;
		let newOption = document.createElement("option");
		newOption.value = value;
		newOption.innerHTML = value;
		onlineUsersSelector.appendChild(newOption);
	}

	// removes an option from 'onlineUsersSelector'
	function onlineUsersSelectorRemove(value) {
		let oldOption = document.querySelector("option[value='" + value + "']");
		if (oldOption !== null) oldOption.remove();
	}

	// focus 'chatMessageInput' when user opens the page
	chatMessageInput.focus();

	// submit if the user presses the enter key
	chatMessageInput.onkeyup = function(e) {
		if (e.keyCode === 13) {  // enter key
			chatMessageSend.click();
		}
	};

	// clear the 'chatMessageInput' and forward the message
	chatMessageSend.onclick = function() {
		if (chatMessageInput.value.length === 0) return;
		// TODO: forward the message to the WebSocket
		chatMessageInput.value = "";
	};
	
Ваш окончательная структура каталога приложения "chat" должна теперь выглядеть так:
```
	chat
	├── __init__.py
	├── admin.py
	├── apps.py
	├── migrations
	│   ├── 0001_initial.py
	│   ├── __init__.py
	├── models.py
	├── static
	│   ├── index.js
	│   └── room.js
	├── templates
	│   ├── index.html
	│   └── room.html
	├── tests.py
	├── urls.py
	└── views.py
```

### ТЕСТИРОВАНИЕ
Базовая настройка проекта завершена, давайте проверим все в браузере.
Запустите сервер разработки Django:

	:::bash
	(env)$ python manage.py runserver

Перейдите по адресу http://localhost:8000/chat/. Вы увидите селектор комнаты:

![picture]({static}../images/django/channels/picture16.png)

Чтобы убедится, что статические файлы корректно сконфигурированы, откройте 'Developer Console'. Вы должны увидеть проверку работоспособности.

```
	Sanity check from index.js.
```

Затем, введите текст названия комнаты 'Room name' и нажмите ввод. Вы будете перенаправлены в комнату:

![picture]({static}../images/django/channels/picture18.png)

> Это просто статические шаблоны. Мы реализуем функциональность для чата и онлайн пользователей позже.

## ДОБАВЛЯЕМ КАНАЛЫ CHANNELS
Далее давайте подключим Django Channels.
Начните с инсталляции пакета:

	:::bash
	(env)$ pip install channels==3.0.4

Затем добавьте ```channels``` в ваш ```INSTALLED_APPS``` в *core/settings.py*:

	:::python
	# core/settings.py

	INSTALLED_APPS = [
		'django.contrib.admin',
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.messages',
		'django.contrib.staticfiles',
		'chat.apps.ChatConfig',
		'channels',  # new
	]

С этого момента мы будем использовать WebSockets вместо HTTP для связи от клиента к серверу, нам необходимо обернуть нашу конфигурацию ASGI с помощью **ProtocolTypeRouter** in *core/asgi.py*:

	:::python
	# core/asgi.py

	import os

	from channels.routing import ProtocolTypeRouter
	from django.core.asgi import get_asgi_application

	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

	application = ProtocolTypeRouter({
	  'http': get_asgi_application(),
	})

Этот маршрутизатор будет направлять трафик в разные части веб приложения в зависимости от используемого протокола.

> Django версии <= 2.2 не имеет встроенной поддержки ASGI. Для того чтобы получить запуск ```channels``` с устаревшими версиями Django пожалуйста перейдите по ссылке на руководство по официальной установке.

Далее нам необходимо позволить Django знать местоположение нашего ASGI приложения. Добавьте следующее в ваш файл *core/settings.py*, чуть ниже настроек ```WSGI_APPLICATION```:

	:::python
	# core/settings.py

	WSGI_APPLICATION = 'core.wsgi.application'
	ASGI_APPLICATION = 'core.asgi.application'  # new

Когда вы сейчас запустите сервер разработки, вы увидите, что Channels были задействованы:

```
	Starting ASGI/Channels version 3.0.4 development server at http://127.0.0.1:8000/
```

