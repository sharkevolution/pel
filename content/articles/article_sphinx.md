Title: Документация как код 
Date: 2023-07-28 00:01
Author: Sitala
Tags: sphinx, docs, python 
Cover: /images/docs_as_code.png
Summary:

##### Разработка технической документации с использованием инструментов и процессов, что и написание кода: 

[1]:https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/?utm_source=pocket_saves
[2]:https://www.joelonsoftware.com/about-me/

# Документация не полная или часто устаревшая 

Довольно часто, качественное описание документации занимает много времени, а поддержка в актуальном состоянии требует постоянных трудозатрат. При небольшом объеме проекта, просто использовать всем знакомые текстовые процессоры и редакторы. Но в один прекрасный день, я осознал, что немогу быть эффективным при описании системы в промышленных масштабах. 

>Скорость, удобочитаемость, поддержка, автоматизация и доступность, - это те вещи которые желаешь видеть, но не знаешь как реализовать.

Можно ли это автоматизировать и создать отличный статический веб-сайт, описывающий документацию? 

Да. И вот где приходит на помощь Sphinx!

# Что такое Sphinx?

Sphinx — это генератор документации на Python, преобразующий файлы в формате **reStructuredText** в HTML website и другие форматы. Он использует ряд расширений для reStructuredText.

