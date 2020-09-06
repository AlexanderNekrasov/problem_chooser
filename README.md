# Problem chooser

Сделано для класса 22b школы 179.

До дедлайна по информатике осталось пару дней? Не хочется думать над сложными задачами? Наше приложение поможет вам выбрать самые простые задачи!

## Как установить

Приложение доступно только для систем Windows, Linux и Mac OS.

Скачайте [отсюда](https://github.com/AlexanderNekrasov/problem_chooser/releases/tags/v2.0) архив `problem-chooser-v2.0-OS.zip` для своей операционной системы.

После разархивации появится файл `problem-chooser` (с расширением для вашей операционной системы).
Запустите этот файл. Готово!

#### Возможные проблемы при установке
1. На Mac OS программа может автоматически переместиться на карантин, в этом случае у вас не получится её запустить.
Чтобы это исправить, зайдите в терминале в директорию где находится приложение. Дальше введите следующее:\
`sudo xattr -rd com.apple.quarantine [program-name].app`\
У вас должны попросить пароль, введите его. После этого программа должна убраться с карантина и у вас получится её запустить.

2. Если программа не запускается на Linux, попробуйте обновить систему.

3. С большой вероятностью ОС сначала попросит подтверждение на запуск, так как ей не удасться проверить разработчика (неизвестный источник).

4. Не рекомендуется располагать приложение в папке, путь к которой состоит не только из ASCII символов (особенно касается пользователей Windows). Если в пути к приложению есть, например, русские буквы, то некоторый функционал может не работать.

При других проблемах обращайтесь к разработчикам.

## Как пользоваться
В специальном поле можно ввести своё имя, и вам будет предложен список нерешённых задач в порядке возрастания сложности.

В списке вы можете увидеть оценку простоты задачи, ID контеста и название задачи (как в тестирующей системе - A, B, C и т.д.)

Чем больше оценка простоты, тем, скорее всего, вам будет легче решить задачу. Максимальная простота равняется 100, минимальная - не ограничена, у задачи без посылок - 0. Она зависит от посылок других людей, так что у самых новых задач оценка будет не совсем корректна (она просто будет около нуля).

Данные о посылках для подсчёта простоты задач берутся из общей таблицы ejudge, так что если server.179.ru недоступен, то обновить данные не получиться. Но они сохраняются, так что при перезапуске программы все данные останутся.

Вручную обновить данные можно при нажатии на кнопку "Reload", Сtrl+R или в меню.

При двойном клике на имя человека его имя вводится в поле.
Также вы можете сделать двойной клик по любой из ячеек предложенных задач:
 * При клике на ячейку "ID контеста" откроется ссылка на контест в тестирующей системе.
 * При клике на ячейку с названием задачи откроется условие задачи.
 * При клике на ячейку с простотой задачи откроется таблица результатов этого контеста.

Вы можете настроить работу программы для себя (нужные вкладки находятся в верхнем меню).
Настроить можно:
* Размер текста (Настройки > Шрифт). Увеличить/уменьшить текст и заголовки.
* Автоввод имени (Настройки > Автоввод имени). При входе в приложение в поле ввода будет автоматически вставляться нужное имя.
* Автообновление (Таблица > Автообновление). Программа будет сама обновлять таблицу раз в X секунд.

## Как поддержать проект
Если вы обнаружили неисправность или хотите новую функциональность, *обязательно* напишите разработчикам:
 * telegram: [@crazyilian](https://t.me/crazyilian "Открыть чат @crazyilian")
 * telegram: [@AlexNekrasov01](https://t.me/AlexNekrasov01 "Открыть чат @AlexNekrasov01")
 * vk: [@crazyilian](https://vk.com/im?sel=240253698 "Открыть чат @crazyilian")

Также поддержать проект вы можете отправив любую сумму:
 * на телефон +79295917075 (мегафон)
 * на [yandex.money](https://money.yandex.ru/quickpay/shop-widget?writer=seller&targets=%D0%A0%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA%D0%B0%D0%BC%20%D0%BD%D0%B0%20%D0%B5%D0%B4%D1%83&targets-hint=&default-sum=17.9&button-text=14&payment-type-choice=on&comment=on&hint=%D0%9D%D0%B0%D0%BF%D0%B8%D1%88%D0%B8%D1%82%D0%B5%20%D0%B2%D1%81%D1%91%20%D1%87%D1%82%D0%BE%20%D0%B4%D1%83%D0%BC%D0%B0%D0%B5%D1%82%D0%B5%20%D0%BE%20Problem%20Chooser&successURL=https%3A%2F%2Fgithub.com%2FAlexanderNekrasov%2Fproblem_chooser&quickpay=shop&account=4100110318593748 "Открыть форму")
 * на перемене любым способом (к Илиану)

за другими реквизитами обращайтесь к разработчикам.
