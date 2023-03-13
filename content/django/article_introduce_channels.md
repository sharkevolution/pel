Title: Введение в Django Channels
Date: 2023-03-07 00:01
Author: Sitala
Tags: django, python, channels
Cover: /images/b1922774.png
Summary:

[TOC]

#### Это перевод оригинальной статьи [Introduction to Django Channels][1] Автор [Nik Tomazic][2]: 

[1]:https://testdriven.io/blog/django-channels/
[2]:https://testdriven.io/authors/tomazic/

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


**ЗАМЕТКИ**:

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

### ДОБАВЛЕНИЕ CHANNEL LAYER
Channel layer это своего рода система связи, которая позволяет множествам частей вашего приложения обмениваться сообщениями, без пересылки всех сообщений или событий через базу данных.

Нам необходимо channel layer дать потребителям (которых мы реализуем на следующем шаге) способным говорить друг с другом.

Хотя мы могли бы использовать **InMemoryChannelLayer** слой, поскольку мы находимся в режиме разработки, мы будем использовать готовый к работе слой **RedisChannelLayer**. Поскольку для этого слоя требуется Redis, введите следующую команду чтобы запустить его с Docker:

	:::bash
	(env)$ docker run -p 6379:6379 -d redis:5

Эта команда скачает образ и запустит контейнер Redis Docker на порту `6379`.

>Если вы не хотите использовать Docker, просто скачайте Redis прямо с официального вебсайта.

Чтобы подключится к Redis из Django, нам необходимо инсталлировать дополнительный пакет с названием **channel_redis**:
	
	:::bash
	(env)$ pip install channels_redis==3.3.1

После этого, настроим слой *core/settings.py* следующим образом:

	:::python
	# core/settings.py

	CHANNEL_LAYERS = {
		'default': {
			'BACKEND': 'channels_redis.core.RedisChannelLayer',
			'CONFIG': {
				"hosts": [('127.0.0.1', 6379)],
			},
		},
	}

Здесь, мы позволим channels_redis знать где сервер Redis находится. 
Чтобы протестировать все ли работает как ожидалось, откройте Django оболочку:

	:::bash
	(env)$ python manage.py shell

Затем запустите:

	:::python
	>>> import channels.layers
	>>> channel_layer = channels.layers.get_channel_layer()
	>>>
	>>> from asgiref.sync import async_to_sync
	>>> async_to_sync(channel_layer.send)('test_channel', {'type': 'hello'})
	>>> async_to_sync(channel_layer.receive)('test_channel')
	{'type': 'hello'}

Здесь мы подключились к channel layer используя настройки определенные в *core/settings.py*. Мы использовали `channel_layer.send` для отправки сообщения группе `test_channel` и `channel_layer.receive` для чтения всех сообщений отправленных в туже группу.

>Отметьте, что мы обернули все вызовы функции в `async_to_sync`, потому что слой каналов асинхронный.

Введите `quit()` для выхода из оболочки.

### ДОБАВЛЕНИЕ КАНАЛОВ ПОТРЕБИТЕЛЕЙ
Потребитель — это основная единица кода Channels. Они крошечные приложения ASGI, управляемые событиями. Они похожи на Django представления. Однако в отличии от Django представлений, потребители являются долгосрочными по умолчанию. Django проект может иметь множество потребителей которые объединены с использованием маршрутизации Channels (которые мы рассмотрим в следующем разделе).

Каждый потребитель имеет собственную область, который представляет набор сведений об одном входящем сообщении. Они содержат фрагменты данных о типе протокола, путь, заголовки, аргументы маршрутизации, пользовательский агент и другое.

Создайте новый файл с названием *consumers.py* внутри “chat”:

	:::python
	# chat/consumers.py

	import json

	from asgiref.sync import async_to_sync
	from channels.generic.websocket import WebsocketConsumer

	from .models import Room


	class ChatConsumer(WebsocketConsumer):

		def __init__(self, *args, **kwargs):
			super().__init__(args, kwargs)
			self.room_name = None
			self.room_group_name = None
			self.room = None

		def connect(self):
			self.room_name = self.scope['url_route']['kwargs']['room_name']
			self.room_group_name = f'chat_{self.room_name}'
			self.room = Room.objects.get(name=self.room_name)

			# connection has to be accepted
			self.accept()

			# join the room group
			async_to_sync(self.channel_layer.group_add)(
				self.room_group_name,
				self.channel_name,
			)

		def disconnect(self, close_code):
			async_to_sync(self.channel_layer.group_discard)(
				self.room_group_name,
				self.channel_name,
			)

		def receive(self, text_data=None, bytes_data=None):
			text_data_json = json.loads(text_data)
			message = text_data_json['message']

			# send chat message event to the room
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'chat_message',
					'message': message,
				}
			)

		def chat_message(self, event):
			self.send(text_data=json.dumps(event))

Здесь, мы создали `ChatConsumer`, который наследуется от **WebsocketConsumer**.
`WebsocketConsumer` предоставляет три метода, `connect()`, `disconnect()`, and `receive()`:

1. Внутри `connect()` we `called accept()` чтобы принять соединение. После этого, мы добавляем пользователя в группу channel layer.
2. Внутри `disconnect()` мы удаляем пользователя из группы channel layer.
3. Внутри `receive()` мы разбираем данные в формате JSON и извлекаем message. Затем мы пересылаем message используя group_send в chat_message.

>При использовании `group_send` принадлежащий channel layer, ваш потребитель должен иметь метод для каждого типа `type` JSON сообщения который вы используете. В нашей ситуации, `type` равен `chat_message`. Таким образом мы добавили метод с названием `chat_message`.
Если вы используете точки в ваших типах сообщений, Channels автоматически конвертирует их в подчеркивания при поиске метода -- например, `chat.message` станет `chat_message`.

Поскольку `WebsocketConsumer` это асинхронный потребитель, нам пришлось вызвать `async_to_sync` кода работаем с слоем channel layer. Мы решили использовать sync consumer приложения чата поскольку оно тесно связанно с Django (которое есть sync по умолчанию. Другими словами, мы не получим прироста производительности при использовании async потребителя. 

>Вам следует использовать sync consumers по умолчанию. Более того, используйте асинхронных потребителей в случаях, где вы абсолютно уверенны, что делаете что-то что принесет выигрыш от асинхронной обработки (например, длительные задачи, которые могли бы выполнится параллельно) и вы используете только async-native (асинхронные) библиотеки.

### ДОБАВЛЕНИЕ МАРШРУТИЗАЦИИ КАНАЛОВ
Каналы представляют различные классы маршрутизации **routing** которые позволяют объединять и складывать потребителей. Они похожи на Django's URLs.

Добавьте файл *routing.py* в "chat":

	:::python
	# chat/routing.py

	from django.urls import re_path

	from . import consumers

	websocket_urlpatterns = [
		re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
	]

Зарегистрируйте файл *routing.py* в *core/asgi.py*:

	:::python
	# core/asgi.py

	import os

	from channels.routing import ProtocolTypeRouter, URLRouter
	from django.core.asgi import get_asgi_application

	import chat.routing

	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

	application = ProtocolTypeRouter({
	  'http': get_asgi_application(),
	  'websocket': URLRouter(
		  chat.routing.websocket_urlpatterns
		),
	})


### WEBSOCKETS (FRONTEND)
Чтобы общаться с Channels из frontend, мы будем использовать **WebSocket API**.

WebSockets чрезвычайно легок для использования. Во первых, нам необходимо установить соединение указав `url` и затем вы можете прослушивать следующие события:

1. `onopen` - вызывается, когда WebSocket соединение устанавливается.
2. `onclose` - вызывается, когда WebSocket соединение разрывается.
3. `onmessage` - вызывается, когда WebSocket получает сообщение.
4. `onerror` - вызывается, когда WebSocket обнаруживает ошибку.

Чтобы интегрировать WebSockets в наше приложение, добавьте следующее в конец *room.js*:

	:::python
	// chat/static/room.js

	let chatSocket = null;

	function connect() {
		chatSocket = new WebSocket("ws://" + window.location.host + "/ws/chat/" + roomName + "/");

		chatSocket.onopen = function(e) {
			console.log("Successfully connected to the WebSocket.");
		}

		chatSocket.onclose = function(e) {
			console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s...");
			setTimeout(function() {
				console.log("Reconnecting...");
				connect();
			}, 2000);
		};

		chatSocket.onmessage = function(e) {
			const data = JSON.parse(e.data);
			console.log(data);

			switch (data.type) {
				case "chat_message":
					chatLog.value += data.message + "\n";
					break;
				default:
					console.error("Unknown message type!");
					break;
			}

			// scroll 'chatLog' to the bottom
			chatLog.scrollTop = chatLog.scrollHeight;
		};

		chatSocket.onerror = function(err) {
			console.log("WebSocket encountered an error: " + err.message);
			console.log("Closing the socket.");
			chatSocket.close();
		}
	}
	connect();
	
После установления соединения WebSocket, в событии `onmessage`, мы определили тип сообщения на основе `data.type`. Обратите внимание ка мы обернули WebSocket внутри метода `connect()` чтобы иметь возможность восстановить соединение в случае разрыва. 

Наконец, измените TODO внутри `chatMessageSend.onclickForm` на следующее:

	:::python
	// chat/static/room.js

	chatSocket.send(JSON.stringify({
		"message": chatMessageInput.value,
	}));

Полный обработчик теперь должен выглядеть так:

	:::python
	// chat/static/room.js

	chatMessageSend.onclick = function() {
		if (chatMessageInput.value.length === 0) return;
		chatSocket.send(JSON.stringify({
			"message": chatMessageInput.value,
		}));
		chatMessageInput.value = "";
	};

Первая версия чата выполнена.

Чтобы протестировать, запустите сервер разработки. Затем, откройте два приватных/инкогнито окна браузера и в каждом, перейдите по ссылке http://localhost:8000/chat/default/.  Вы должны иметь возможность отправлять сообщения:

![picture]({static}../images/django/channels/picture35.png)

Это то все что касается базовой функциональности. Далее, мы рассмотрим аутентификацию.

## АУТЕТНТИФИКАЦИЯ
### БЭКЕНД

Channels поставляются с встроенным классом для Django сессии и управления аутентификацией, которая называется `AuthMiddlewareStack`.
Чтобы использовать его, единственное что необходимо сделать обернуть URLRouter внутри **core/asgi.py** следующим образом:

	:::python
	# core/asgi.py

	import os

	from channels.auth import AuthMiddlewareStack  # new import
	from channels.routing import ProtocolTypeRouter, URLRouter
	from django.core.asgi import get_asgi_application

	import chat.routing

	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

	application = ProtocolTypeRouter({
	'http': get_asgi_application(),
	'websocket': AuthMiddlewareStack(  # new
			URLRouter(
				chat.routing.websocket_urlpatterns
			)
		),  # new
	})

Теперь, когда бы ни присоединялся клиент, пользовательский объект будет добавлен в область. Доступ к нему можно получить:

	:::python
	user = self.scope['user']

>Если вы хотите запускать каналы с одним из фреймворков JavaScript (такие как Angular, React, or Vue), вам придется использовать разные системы аутентификации (например, токен аутентификации). Если вы хотите изучить как использовать токен аутентификации с Channels, ознакомьтесь со следующими курсами:

>1.	Developing a Real-Time Taxi App with Django Channels and Angular
>2.	Developing a Real-Time Taxi App with Django Channels and React

Давайте изменим `ChatConsumer` чтобы заблокировать не аутентифицированных пользователей от разговора и отобразим имена пользователей с сообщениями.
 
Измените **chat/consumers.py** на следующее:

	:::python
	# chat/consumers.py

	import json

	from asgiref.sync import async_to_sync
	from channels.generic.websocket import WebsocketConsumer

	from .models import Room, Message  # new import


	class ChatConsumer(WebsocketConsumer):

		def __init__(self, *args, **kwargs):
			super().__init__(args, kwargs)
			self.room_name = None
			self.room_group_name = None
			self.room = None
			self.user = None  # new

		def connect(self):
			self.room_name = self.scope['url_route']['kwargs']['room_name']
			self.room_group_name = f'chat_{self.room_name}'
			self.room = Room.objects.get(name=self.room_name)
			self.user = self.scope['user']  # new

			# connection has to be accepted
			self.accept()

			# join the room group
			async_to_sync(self.channel_layer.group_add)(
				self.room_group_name,
				self.channel_name,
			)

		def disconnect(self, close_code):
			async_to_sync(self.channel_layer.group_discard)(
				self.room_group_name,
				self.channel_name,
			)

		def receive(self, text_data=None, bytes_data=None):
			text_data_json = json.loads(text_data)
			message = text_data_json['message']

			if not self.user.is_authenticated:  # new
				return                          # new

			# send chat message event to the room
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'chat_message',
					'user': self.user.username,  # new
					'message': message,
				}
			)
			Message.objects.create(user=self.user, room=self.room, content=message)  # new

		def chat_message(self, event):
			self.send(text_data=json.dumps(event))

### FRONTEND
Далее, давайте изменим **room.js** чтобы отображалось имя пользователя. Внутри `chatSocket.onMessage`, добавьте следующее:

	:::python
	// chat/static/room.js

	chatSocket.onmessage = function(e) {
		const data = JSON.parse(e.data);
		console.log(data);

		switch (data.type) {
			case "chat_message":
				chatLog.value += data.user + ": " + data.message + "\n";  // new
				break;
			default:
				console.error("Unknown message type!");
				break;
		}

		// scroll 'chatLog' to the bottom
		chatLog.scrollTop = chatLog.scrollHeight;
	};

### ТЕСТИРОВАНИЕ
Создайте суперпользователя, которого вы будете использовать для тестирования:

	:::bash
	(env)$ python manage.py createsuperuser

Запустите сервер:

	:::bash
	(env)$ python manage.py runserver

Откройте браузер и в войдите в систему используя админ логин Django по адресу http://localhost:8000/admin. 
Затем перейдите http://localhost:8000/chat/default. Протестируйте это:

![picture]({static}../images/django/channels/picture42.png)

Выйдите из админ-панели Django. Перейдите к http://localhost:8000/chat/default. Что случается, когда вы пытаетесь отправить сообщение?

## СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ

Далее мы добавим следующие три типа сообщения:

1. `user_list` – отправляется вновь присоединившемуся пользователю (data.users = список пользователей онлайн).
2. `user_join` – отправляется, когда пользователь присоединяется к чату.
3. `user_leave` – отправляется когда пользователь покидает чат.

### БЭКЕНД
В конце метода `connect` в `ChatConsumer` добавьте:

	:::python
	# chat/consumers.py

	def connect(self):
		# ...

		# send the user list to the newly joined user
		self.send(json.dumps({
			'type': 'user_list',
			'users': [user.username for user in self.room.online.all()],
		}))

		if self.user.is_authenticated:
			# send the join event to the room
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'user_join',
					'user': self.user.username,
				}
			)
			self.room.online.add(self.user)

В конце метода `disconnect` в `ChatConsumer` добавьте:

	:::python
	# chat/consumers.py

	def disconnect(self, close_code):
		# ...

		if self.user.is_authenticated:
			# send the leave event to the room
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'user_leave',
					'user': self.user.username,
				}
			)
			self.room.online.remove(self.user)

Потому что мы добавили новые типы сообщений, нам также необходимо добавить методы для слоя channel_layer. В конце **chat/consumers.py** добавьте:

	:::python
	# chat/consumers.py

	def user_join(self, event):
		self.send(text_data=json.dumps(event))

	def user_leave(self, event):
		self.send(text_data=json.dumps(event))

Ваш **consumers.py** после этого шага должен выглядеть так: consumers.py.

### ФРОНТЕНД
Для обработки сообщений из фронтенда добавьте следующие случаи в оператор switch в `chatSocket.onmessage` обработчик:

	:::python
	// chat/static/room.js

	switch (data.type) {
		// ...
		case "user_list":
			for (let i = 0; i < data.users.length; i++) {
				onlineUsersSelectorAdd(data.users[i]);
			}
			break;
		case "user_join":
			chatLog.value += data.user + " joined the room.\n";
			onlineUsersSelectorAdd(data.user);
			break;
		case "user_leave":
			chatLog.value += data.user + " left the room.\n";
			onlineUsersSelectorRemove(data.user);
			break;
		// ...

### ТЕСТИРОВАНИЕ
Запустите сервер снова, залогинтесь и посетите http://localhost:8000/chat/default.

![picture]({static}../images/django/channels/picture47.png)

Теперь вы должны видеть сообщения о присоединении и оставлении сообщений. Список пользователей также должен быть заполнен.

## ЧАСТНЫЕ СООБЩЕНИЯ

Пакет Channels не позволяет на прямую фильтровать, поэтому нет встроенного метода для отправки сообщений от одного клиента другому клиенту. С помощью каналов вы можете отправить сообщения:

1. Клиентам потребителя (`self.send`)
2. Группе channel layer (`self.channel_layer.group_send`)

Таким образом, для того чтобы реализовать частные сообщения, мы:

1. Создадим новую группу с названием `inbox_%USERNAME%` каждый раз как клиент присоединяется.
2. Добавим клиента в свою группу входящих сообщений (`inbox_%USERNAME%`).
3. Удалим клиента из группы входящих сообщений (`inbox_%USERNAME%`) когда они отключаются.

После реализации, каждый клиент будет иметь свой ящик входящих сообщений. Затем другие клиенты могут отправлять частные сообщения в `inbox_%TARGET_USERNAME%`.

### БЭКЕНД
Измените **chat/consumers.py**.

	:::python
	# chat/consumers.py

	class ChatConsumer(WebsocketConsumer):

		def __init__(self, *args, **kwargs):
			# ...
			self.user_inbox = None  # new

		def connect(self):
			# ...
			self.user_inbox = f'inbox_{self.user.username}'  # new

			# accept the incoming connection
			self.accept()

			# ...

			if self.user.is_authenticated:
				# -------------------- new --------------------
				# create a user inbox for private messages
				async_to_sync(self.channel_layer.group_add)(
					self.user_inbox,
					self.channel_name,
				)
				# ---------------- end of new ----------------
				# ...

		def disconnect(self, close_code):
			# ...

			if self.user.is_authenticated:
				# -------------------- new --------------------
				# delete the user inbox for private messages
				async_to_sync(self.channel_layer.group_discard)(
					self.user_inbox,
					self.channel_name,
				)
				# ---------------- end of new ----------------
				# ...

Итак, мы:

1. Добавили `user_inbox` в `ChatConsumer` и инициализировали его на `connect()`.
2. Добавили пользователя в группу `user_inbox` когда он подключается.
3. Удалили пользователя из группы `user_inbox` когда он отключается.

Далее, измените метод `receive()` для обработки частных сообщений:

	:::python
	# chat/consumers.py

	def receive(self, text_data=None, bytes_data=None):
		text_data_json = json.loads(text_data)
		message = text_data_json['message']

		if not self.user.is_authenticated:
			return

		# -------------------- new --------------------
		if message.startswith('/pm '):
			split = message.split(' ', 2)
			target = split[1]
			target_msg = split[2]

			# send private message to the target
			async_to_sync(self.channel_layer.group_send)(
				f'inbox_{target}',
				{
					'type': 'private_message',
					'user': self.user.username,
					'message': target_msg,
				}
			)
			# send private message delivered to the user
			self.send(json.dumps({
				'type': 'private_message_delivered',
				'target': target,
				'message': target_msg,
			}))
			return
		# ---------------- end of new ----------------

		# send chat message event to the room
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name,
			{
				'type': 'chat_message',
				'user': self.user.username,
				'message': message,
			}
		)
		Message.objects.create(user=self.user, room=self.room, content=message)

Добавьте следующие методы в конец файла **chat/consumers.py**:

	:::python
	# chat/consumers.py

	def private_message(self, event):
		self.send(text_data=json.dumps(event))

	def private_message_delivered(self, event):
		self.send(text_data=json.dumps(event))

Ваш окончательный файл **chat/consumers.py** должен быть равен этому файлу: consumers.py

### ФРОНТЕНД
Для обработки частных сообщений в фронтенде, добавьте `private_message` и `private_message_delivered` случаи внутри оператора `switch(data.type)`:

	:::python
	// chat/static/room.js

	switch (data.type) {
		// ...
		case "private_message":
			chatLog.value += "PM from " + data.user + ": " + data.message + "\n";
			break;
		case "private_message_delivered":
			chatLog.value += "PM to " + data.target + ": " + data.message + "\n";
			break;
		// ...
	}

Чтобы сделать чат немного удобнее, мы можем изменить ввод сообщения в 
pm `%USERNAME%` когда пользователь нажимает на одного из онлайн пользователей в `onlineUsersSelector`. Добавьте следующий обработчик внизу:

	:::python
	// chat/static/room.js

	onlineUsersSelector.onchange = function() {
		chatMessageInput.value = "/pm " + onlineUsersSelector.value + " ";
		onlineUsersSelector.value = null;
		chatMessageInput.focus();
	};

### ТЕСТИРОВАНИЕ
Вот и все! Приложение чат теперь завершено. Давайте протестируем это в последний раз.

Создайте суперпользователя для тестирования, и затем запустите сервер.

Откройте два разных частных/incognito браузера, вход в оба по адресу http://localhost:8000/admin.

Затем перейдите http://localhost:8000/chat/default в обоих браузерах. Нажмите на одного из подключенных пользователей чтобы отправить ему частное сообщение:

![picture]({static}../images/django/channels/picture53.png)

## ЗАКЛЮЧЕНИЕ

В этом учебном пособии, мы посмотрели, как использовать Channels с Django. Вы узнали о разнице между выполнением синхронного и асинхронного кода вместе со следующими понятиями Channels.

1. Потребители
2. Слои Channel layers
3. Маршрутизация

Наконец, мы связали все вместе с WebSockets и создали приложение чат.
Наш чат далек от совершенства. Если вы хотите практиковать то, чему научились, вы можете улучшить это следующим образом:

1. Добавление чатов только для администраторов.
2. Отправка последних десяти сообщений пользователю, когда он присоединился в чат комнату.
3. Позволить пользователям редактировать и удалять сообщения
4. Добавить функциональность «пользователь печатает»
5. Добавить реакции на сообщения.

> Идеи ранжируются от самых легких до самых сложных для реализации.

Вы можете взять код из репозитория django-channels-example на GitHub.

https://github.com/testdrivenio/django-channels-example

https://testdriven.io/authors/tomazic/

https://coderbooks.ru/books/python/

![picture]({static}../images/django/channels/tomazic.png)






