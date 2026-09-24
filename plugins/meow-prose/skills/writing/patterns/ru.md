<role>
The Russian counterpart of `en.md`: the same patterns in the same order, with
Russian examples and Russian markers. The shapes sound authoritative by hiding
the author, the reader or the reason. Use this file on any Russian text:
rewrite your own draft into the corrected form, and for a text somebody else
wrote, report each finding as `SKILL.md` says under "review a text". Keep
every fact either way.

A marker finds a candidate, and a hit is a problem only when the sentence
matches the failing form: "Это пересечение - самый сильный аргумент" names its
noun and is fine. Some patterns have no reliable marker; find those on a
read-through. When you add or change a pattern here, change it in `en.md` too,
so the two files stay parallel.
</role>

<example name="bold standing in for structure">
A bold sentence opening a paragraph, a bold fragment standing in for a heading,
and a summary made of bold claims all state a conclusion with its argument
stripped out. Make a heading a heading, finish a fragment as a sentence, and
give a summary numbers and actions a reader can check.

Markers: `**` at the start of a paragraph or a list item.

Failing:

**Дизайн опирается на одно разделение ответственности.** Сервис отвечает на
все вопросы о заказе и применяет к нему все изменения.

Corrected:

Ответственность в дизайне разделена в одном месте: сервис заказов отвечает на
все вопросы о заказе и применяет все изменения, а веб-клиент хранит только то,
что рисует на экране.

Failing:

**Что заставит отказаться.** Падение доли попаданий ниже 60%.

Corrected:

Мы откажемся от кэша, если доля попаданий упадёт ниже 60%, потому что тогда он
тратит больше памяти, чем экономит на запросах к базе.

Failing:

**Такая миграция требует внимательного чтения и почти не затрагивает код.**

Corrected:

Миграция заняла три дня и изменила 122 из 4141 перенесённой строки. Почти всё
время ушло на то, чтобы прочитать старый код достаточно внимательно и найти 23
правила, которые он проверял.
</example>
<example name="counted opener">
Announcing how many items follow makes the reader count the items before
reading them. State the first item, and use a list when there really are three.

Markers: a sentence opening with a number word and a category noun, such as
"Три вещи", "Две причины" or "Есть несколько".

Failing:

Работу обеспечивают три вещи. Кэш хранит отрисованные страницы, поэтому сервер
пропускает шаблонизацию...

Corrected:

Это работает, потому что кэш хранит отрисованные страницы и сервер пропускает
шаблонизацию. Помогает и то, что...
</example>
<example name="pointer fragment">
A bare reference at the end of a paragraph makes the reader guess why to
follow it.

Markers: a paragraph ending in "Раздел 8.", "См. X." or a bare link.

Failing:

Это работает на текущем слое хранения. Раздел 8.

Corrected:

Это работает на нынешнем слое хранения; в разделе 8 перечислено, что нельзя
обещать, пока не выйдет новый.
</example>
<example name="text about the text">
A sentence repeating its neighbour, one announcing what the next paragraph will
say, and a paragraph describing its own plan each cost the reader a sentence
and give nothing back. Say the thing.

Markers: "как упоминалось", "как отмечалось", "выше", "ниже", "в следующем
разделе", "в этом разделе", "данный раздел".

Failing:

В следующем разделе описан кэш. Как упоминалось выше, кэш хранит отрисованные
страницы.

Corrected:

Кэш хранит отрисованные страницы, поэтому повторный запрос пропускает
шаблонизацию.

Failing:

Третий пробел самый дорогой, поэтому в этом абзаце изложен план его
устранения. Ни один тест не сравнивает новые правила со старыми.

Corrected:

Дороже всего обходится то, что ни один тест не сравнивает новые правила со
старыми. Этот пробел закрывает прогон на данных за прошлый месяц: ...
</example>
<example name="draft archaeology">
"В предыдущей версии было" and "это удаление отменено" tell the reader the
history, where they came for the current rule. Version control keeps the
history.

Markers: "в предыдущей версии", "ранее", "больше не", "отменено", "на раннем
этапе".

Failing:

Ничего не удаляется из-за избыточности. На раннем этапе были убраны алиасы
вроде `rm-all`, потому что ту же работу делала другая команда. Эти удаления
отменены.

Corrected:

Избыточные алиасы вроде `rm-all` остаются: их удаление ничего не экономит и
ломает скрипты, которые их вызывают.
</example>
<example name="the document as author">
"Этот документ утверждает", "в этих заметках принято" and "это изменение
определяет" hide who decided.

Markers: "Этот документ", "В данном документе", "Настоящий документ", "В этих
заметках", "это изменение определяет".

Failing:

Поэтому в этих заметках используется термин "импортёр", а "загрузчик" оставлен
за старым инструментом.

Corrected:

Здесь я называю его импортёром, а "загрузчиком" оставляю старый инструмент.
</example>
<example name="a person where the reader is you">
"Человек вносит изменение" and "кто-то может закончить" is the voice of a
rulebook with no author. Address the reader, or name the role.

Markers: "человек", "кто-то", "необходимо" with no actor.

Failing:

Человек вносит серию изменений, читает весь дифф и затем принимает решение.

Corrected:

Вы вносите серию изменений, читаете весь дифф и решаете, сохранять ли их.
</example>
<example name="an abstract one as the subject">
"Одно правило определяет" and "одно из следствий" make an abstraction the
actor.

Markers: a sentence opening "Одно ", "Один из", "Одна из".

Failing:

Одно правило определяет, что входит в запрос.

Corrected:

Запрос несёт всё, что нужно серверу для проверки, а клиент хранит всё, что
влияет только на отображение.
</example>
<example name="absence as the subject">
"Ничто его не обновляет", "никто не измерял" and "ни одна проверка не
запускалась" describe a world where nobody acts. Name who doesn't, and why.

Markers: "Ничто", "Ничего не", "Никто", "Ни один", "Ни одна".

Failing:

Клиент кэширует ответы, и ничто не сообщает ему, когда ответ устарел.

Corrected:

Клиент кэширует ответы, но никогда их не инвалидирует, потому что единственное
событие, которое он получает, называет таблицу, а не строку.
</example>
<example name="importance promised instead of given">
A phrase such as "стоит прочитать внимательно", "если честно, итог такой" or
"X важнее Y" promises value and delays it. Delete the frame and say the
important thing.

Markers: "стоит отметить", "стоит обратить внимание", "важно", "честно
говоря", "ключевой", "имеет значение", "следует подчеркнуть".

Failing:

Две детали этого результата стоит прочитать внимательно. Повторная попытка уже
вернула ошибку, поэтому...

Corrected:

Повторная попытка уже вернула ошибку, поэтому второй вызов ничего не меняет и
строка в базе остаётся прежней.

Failing:

Свойство масштабирования важнее самих чисел. Правка стоит пропорционально
своему размеру.

Corrected:

Правка стоит пропорционально своему размеру, поэтому числа выше не растут
вместе с проектом, и это говорит больше, чем их абсолютные значения.
</example>
<example name="drama in place of an argument">
"Пересечение неудобное", "это фатально" and "перечитайте этот абзац" put
emotion where the reason belongs.

Markers: "фатально", "неудобно", "катастрофа", "перечитайте", "бросается в
глаза", "тревожно".

Failing:

Перечитайте этот абзац рядом с разделом 3, и пересечение станет неудобным.

Corrected:

У существующего инструмента уже есть все свойства, которых требует раздел 3:
он детерминирован, изолирован и ограничен по ресурсам. Это пересечение - самый
сильный аргумент за то, чтобы взять его, а не писать свой.
</example>
<example name="a long sentence and a short punchline">
The short sentence is usually the reason, cut off from the long one before it.

Markers: none reliable. On a read-through, look for a sentence under about
eight words that follows a long one.

Failing:

Дашборд показывает результат последнего завершившегося прогона. Иногда такого
нет.

Corrected:

Дашборд показывает результат последнего завершившегося прогона, а в часы пик
такого часто нет, потому что каждый новый пуш отменяет текущий прогон.
</example>
<example name="definition chain">
A row of X-is-Y sentences reads as doctrine. Say what happens and why. Russian
marks this shape in writing, so unlike `en.md` this pattern has markers.

Markers: "- это", "является", "представляет собой".

Failing:

Проверка - это проход, и она ничего не блокирует.

Corrected:

Проверка запускается как проход по расписанию, поэтому не может заблокировать
сохранение: к моменту отчёта правка уже применена.
</example>
<example name="a contrast with the consequence missing">
A contrast such as "X, а Y не Z", "X, а не Y" or "вместо Y" hides the
consequence the reader needs. One is fine; a page of them reads as a string of
aphorisms. Keep the claim, drop the "not Y" half and add the reason.

Markers: "а не", "вместо", "не ..., а". Step 5 of the checks in `SKILL.md`
sets how many a text can keep.

Failing:

Валидация есть, а интеграция не сделана.

Corrected:

Правила валидации уже написаны, но ни задача импорта, ни форма в админке их
пока не вызывают, поэтому данные, введённые любым из этих путей, проходят мимо
всех правил.

Failing:

Решение - во владельце, а не в инструментах.

Corrected:

Это не исправит ни один инструмент, только владелец, потому что цена очереди
без владельца ложится на каждую команду, которая из неё читает, и ни одна
команда не чувствует её целиком.
</example>
<example name="that pointing at a whole sentence">
"Это позволяет" and "это задаёт предел" make the reader guess what "это" is.
Give it a noun, or join the sentences.

Markers: a sentence opening "Это " or "Что " followed by a verb, such as "Это
позволяет", "Это даёт", "Это значит", "Что приводит".

Failing:

Заглушка содержит имя и тип, но не содержимое. Это позволяет одному процессу
держать весь проект.

Corrected:

Заглушка содержит имя и тип без содержимого, поэтому один процесс может держать
весь проект.
</example>
<example name="pet abstraction">
Суть, механизм, подход, аспект, момент and контур, used again and again, are
category words standing in for the thing (rule D2).

Markers: суть, механизм, подход, аспект, момент, контур, "история про".

Failing:

Эта пара и есть суть миграции, и каждый мигрированный сервис её повторяет.

Corrected:

Каждый мигрированный сервис устроен как эта пара: фронтенд без состояния и
воркер, который владеет очередью.
</example>
