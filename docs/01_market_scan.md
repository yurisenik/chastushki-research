# Market scan: сервис генерации русских частушек

Дата обзора: 2026-04-14

## Короткий вывод

По прямым источникам я **не нашёл заметного отдельного продукта, сфокусированного именно на генерации русских частушек**. Рынок рядом уже занят тремя классами решений:

1. **общие AI lyrics / AI song платформы** (Suno, Udio, GSong, Neume и др.),
2. **узкие шаблоны “генератор русских текстов песен”**, но без фолк-специализации,
3. **academic/open-source решения** по генерации текстов песен, пародий, рэпа, lyrics-to-song и controllable rewriting.

Отсюда следует важный вывод: **ниша “частушки как отдельный формат” выглядит слабо занятой**, особенно если продукт делает ставку не просто на генерацию рифмованных четверостиший, а на:
- русскую культурную специфику,
- фольклорный стиль,
- метр, рифму и “ударность” частушки,
- локальные темы (свадьба, корпоратив, деревня, праздники, мемы, политика, поздравления),
- режимы “под баян / под сцену / под тост / баттл”.

Ниже, где я пишу “похоже” или “вероятно”, это **моя рыночная интерпретация**, а не прямое утверждение источника.

---

## 1) Прямые аналоги и смежные продукты

### A. Общие AI lyrics / AI song сервисы

#### 1. Suno
- Ссылка: https://suno.com/hub/ai-song-lyrics-generator
- Что есть: генерация lyrics из prompt, затем превращение текста в полную песню.
- Прямой вывод из источника: Suno позиционирует себя как AI song lyrics generator и связывает генерацию текста с полным music workflow.
- Почему важно: это не конкурент “частушкам” по специализации, но сильный **субститут**. Пользователь может просто попросить “Russian folk humorous short song” внутри большой платформы.

#### 2. Udio
- Ссылка: https://help.udio.com/en/articles/10716221-create-a-song-with-your-own-lyrics
- Что есть: можно дать описание песни, Udio сгенерирует lyrics; можно вставить свои lyrics и доработать в editor.
- Почему важно: подтверждает, что крупные генераторы уже закрывают базовый сценарий “сделай текст + музыку”, но не дают отдельного продукта под частушки.

#### 3. GSong AI Lyrics Generator
- Ссылка: https://www.gsong.ai/Lyrics-Generator
- Что есть: общий генератор текстов песен по идее/жанру.
- Почему важно: пример commodity-инструмента. Низкий порог входа в generic lyrics generation.

#### 4. Neume Folk Lyrics Generator
- Ссылка: https://neume.io/lyrics-generator/folk
- Что есть: отдельная страница именно под folk lyrics.
- Почему важно: это уже ближе к теме. Но продукт всё равно **не русско-специфичен** и не выделяет частушку как отдельный жанр.

#### 5. WNR.AI, шаблон “Russian Hit Song Lyrics Generator”
- Ссылка: https://wnr.ai/templates/russian-hit-song-lyrics-generator
- Что есть: шаблон для генерации текстов песен на русском по жанру, теме, настроению и стилю.
- Почему важно: показывает, что “русский язык” как сегмент есть, но **русский фольклор / частушка** не выделены.

### B. Сервисы персонализации и переписывания песен

#### 6. AI Music Service
- Ссылка: https://aimusicservice.com/
- Что есть: сервис смены текста известной песни с сохранением узнаваемой подачи/голоса для свадеб, бизнеса, подарков.
- Почему важно: это не генератор частушек, но подтверждает сильный спрос на **короткий персонализированный музыкальный юмористический контент для событий**. Для частушек это очень релевантный коммерческий сигнал.

### C. Исторически важные lyric generators / смежные публичные демо

#### 7. These Lyrics Do Not Exist
- Ссылка: https://www.producthunt.com/products/these-lyrics-do-not-exist
- Что есть: публично запущенный сервис генерации оригинальных lyrics по теме, жанру и настроению; на Product Hunt указан запуск в 2019.
- Почему важно: один из ранних известных consumer-facing генераторов lyrics. Но жанрово это поп/rock/rap и т.п., не фолк-локаль.

---

## 2) Open-source и developer tools

#### 8. dlebech/lyrics-generator
- Ссылка: https://github.com/dlebech/lyrics-generator
- Что есть: open-source проект генерации lyrics на Keras/TensorFlow, работает также через TensorFlow.js, поддерживает train на собственном song dataset.
- Почему важно: хороший референс для MVP-подхода “свой датасет + генерация текста”, но без фолк-специфики и без русской культурной модели.

#### 9. gaodechen/gpt-lyrics (TuneFlow plugin)
- Ссылка: https://github.com/gaodechen/gpt-lyrics
- Что есть: open-source plugin для TuneFlow, умеет писать lyrics с нуля и дописывать/переписывать строки и секции.
- Почему важно: показывает продуктовый паттерн “генерация + редактура”, полезный для UX частушечного сервиса.

#### 10. Hugging Face model: bcash2233/lyrics-generator-gpt2
- Ссылка: https://huggingface.co/bcash2233/lyrics-generator-gpt2
- Что есть: fine-tuned GPT-2 для генерации song lyrics по prompt.
- Почему важно: рынок моделей commoditized, “просто ещё один генератор lyrics” трудно защитить.

#### 11. Hugging Face model: ECE1786-AG/lyrics-generator
- Ссылка: https://huggingface.co/ECE1786-AG/lyrics-generator
- Что есть: ещё один openly published lyrics model.
- Почему важно: подтверждает избыточность generic-моделей.

#### 12. nevoit/Song-Lyrics-Generator
- Ссылка: https://huggingface.co/nevoit/Song-Lyrics-Generator
- Что есть: RNN-проект, где отдельно рассматривается генерация lyrics с учётом melody features.
- Почему важно: полезен как технический ориентир, если сервис захочет потом перейти от текста к “частушка + напев”.

---

## 3) Academic и research решения

### A. Общая генерация lyrics

#### 13. UniLG: A Unified Structure-aware Framework for Lyrics Generation (ACL 2023)
- Ссылка: https://aclanthology.org/2023.acl-long.56/
- Что есть: структура-осведомлённый framework для lyrics generation под разные условия.
- Почему важно: академически подтверждает, что для lyrics важны **структура и музыкальные атрибуты**, а не только тема текста.
- Вывод для частушек: шанс сделать продукт лучше generic LLM, если жёстко кодировать форму частушки.

#### 14. Unsupervised Melody-to-Lyrics Generation (ACL 2023)
- Ссылка: https://aclanthology.org/2023.acl-long.513/
- Что есть: генерация lyrics под заданную мелодию без aligned melody-lyric train data.
- Почему важно: даёт маршрут к более сильному продукту “частушка под готовый наигрыш / минус / гармошку”.

#### 15. SongComposer (ACL 2025)
- Ссылка: https://aclanthology.org/2025.acl-long.352/
- Что есть: LLM для совместной генерации lyrics и melody.
- Почему важно: верхняя граница того, куда движется рынок, то есть от текста к полноценной song composition.

### B. Rewriting / imitation / parody, особенно релевантно частушкам

#### 16. To Sing like a Mockingbird (EACL 2017)
- Ссылка: https://aclanthology.org/E17-2048/
- Что есть: система автоматического музыкального parody generation, учитывающая метрику, рифму и лексику, с опорой на новости как исходный материал.
- Почему важно: очень близко к прикладному сценарию частушек, где нужен **сатирический отклик на инфоповод**.

#### 17. SongRewriter (Findings ACL 2023)
- Ссылка: https://aclanthology.org/2023.findings-acl.814/
- Что есть: controllable rewriting lyrics под существующую мелодию, с контролем контента и rhyme scheme.
- Почему важно: для частушек может быть даже ценнее, чем generation-from-scratch, потому что пользователи любят “переделать известную форму под свой повод”.

#### 18. Sudowoodo: A Chinese Lyric Imitation System with Source Lyrics (EMNLP Demo 2023)
- Ссылка: https://aclanthology.org/2023.emnlp-demo.8/
- Что есть: imitation system на основе исходного текста песни.
- Почему важно: сильный референс для режима “сделай частушки в стиле X” или “по мотивам этого текста”.

### C. Rap generation как близкая техническая категория

#### 19. GhostWriter: Using an LSTM for Automatic Rap Lyric Generation (EMNLP 2015)
- Ссылка: https://aclanthology.org/D15-1221/
- Что есть: ранняя работа по автоматической генерации rap lyrics.
- Почему важно: rap и частушка различаются культурно, но обе задачи жёстко завязаны на рифму, ритм, punchline и короткую форму.

#### 20. Rapformer: Conditional Rap Lyrics Generation with Denoising Autoencoders (INLG 2020)
- Ссылка: https://aclanthology.org/2020.inlg-1.42/
- Что есть: conditional generation с усилением rhyme density.
- Почему важно: методически полезно для частушек, где плотность рифмы и “ударность” критичны.

#### 21. DeepRapper: Neural Rap Generation with Rhyme and Rhythm Modeling (ACL 2021)
- Ссылка: https://aclanthology.org/2021.acl-long.6/
- Что есть: моделирование и rhyme, и rhythm, плюс данные с выравниванием lyrics-beat.
- Почему важно: подтверждает, что quality ceiling растёт, когда система моделирует не только слова, но и ритм исполнения.

---

## 4) Что видно по конкурентному полю

### Слой 1. Крупные универсальные платформы
Игроки: Suno, Udio и им подобные.

**Их сила:**
- огромный дистрибутив,
- быстрый TTI (“ввёл prompt, получил песню”),
- уже есть text-to-song pipeline.

**Их слабость относительно частушек:**
- нет узкой специализации,
- нет культурной экспертизы по русскому фольклору,
- нет режима “короткая смешная частушка под случай/человека/событие”,
- нет community/UGC вокруг жанра частушки как отдельной практики.

### Слой 2. Узкие lyrics generators и template pages
Игроки: Neume, GSong, WNR template и десятки похожих страниц.

**Их сила:**
- SEO long-tail,
- низкий барьер использования,
- простая ценность “сгенерируй текст”.

**Их слабость:**
- очень слабая дифференциация,
- жанры широкие и поверхностные,
- мало defensibility,
- обычно нет реальной глубины контроля формы.

### Слой 3. Research/open-source
Игроки: ACL papers, GitHub/Hugging Face проекты.

**Их сила:**
- продвинутые техники structure/rhyme/rhythm/rewriting,
- есть научная база для controllable generation.

**Их слабость:**
- почти не упакованы в consumer-продукт,
- нет локального UX под русскую культуру,
- нет готового consumer brand вокруг частушек.

---

## 5) Есть ли явная незанятая ниша?

### Да, похоже есть

На основании прямых источников **явно просматривается свободная продуктовая позиция**:

## “AI-генератор русских частушек” как специализированный vertical tool

Почему это похоже на свободную нишу:
1. **Не найден отдельный заметный лидер именно в частушках.**
2. **Generic tools закрывают только базовую генерацию**, но не форму жанра.
3. **Есть коммерчески понятные use cases**: свадьбы, юбилеи, корпоративы, поздравления, сельские/городские праздники, контент для TikTok/Reels/Telegram.
4. **Частушка короткая**, значит быстрее получать удачный результат, чем в длинной песне.
5. **Частушка меметична и социальна**: её удобно шарить пачками, баттлами, карточками, видео-роликами.

### Где именно можно отличиться

#### Вариант A. “Персональные частушки под повод”
Лучший кандидат на MVP.
- вход: кому, по какому поводу, тон, уровень дерзости, локальные детали;
- выход: 5-20 частушек, сразу пригодных для чтения со сцены.

#### Вариант B. “Новостные / сатирические частушки”
Очень дифференцированная ниша.
- опора на паттерн parody/news-driven generation из `To Sing like a Mockingbird`.
- риск: модерация и политическая чувствительность.

#### Вариант C. “Частушки под мелодию / баян / темп”
Более технологически сложный, но сильный moat.
- опора на SongRewriter, UniLG, Unsupervised Melody-to-Lyrics, SongComposer.
- может стать настоящим product moat, если делать не только текст, но и пригодность к исполнению.

#### Вариант D. “Фольклорный co-pilot для авторов/ведущих/ансамблей”
B2B/B2Pro угол.
- свадебные ведущие,
- event-агентства,
- фольклорные ансамбли,
- SMM и короткие вертикальные видео.

---

## 6) Главный риск идеи

Главный риск в том, что **“сгенерировать рифмованный текст” уже стало commodity**. Поэтому продукту нельзя продаваться как просто “ещё один AI пишет стишки”.

Рабочая дифференциация должна быть в одном или нескольких пунктах:
- жёсткая форма частушки,
- русская культурная точность,
- сильная персонализация,
- готовность к сценическому исполнению,
- юмор/дерзость/цензура как контролируемые режимы,
- пачки, баттлы, карточки, экспорт в видео/караоке.

---

## 7) Практический вывод для запуска

### Что выглядит самым разумным MVP

**MVP:** генератор персональных русских частушек для событий и контента.

Функции первого релиза:
1. тема / повод,
2. адресат,
3. стиль: народная, дерзкая, свадебная, корпоративная, деревенская, политсатирическая, детская,
4. уровень остроты,
5. генерация сразу пакета из 10-20 вариантов,
6. кнопки “смешнее”, “злее”, “короче”, “больше фольклора”, “под баян”,
7. экспорт в карточки/карусель/вертикальное видео/телеграм-пост.

### Что может стать moat во второй итерации
- своя размеченная коллекция частушек,
- rule-based слой поверх LLM для метра/рифмы/формы,
- retrieval по фольклорным корпусам и сборникам,
- режим переписывания под существующую мелодию,
- голосовой/музыкальный слой “спой частушку”.

---

## 8) Итоговая оценка

### Вердикт
Идея **не выглядит занятой “в лоб”**. Конкуренция есть, но в основном:
- либо слишком широкая (Suno/Udio),
- либо слишком generic-SEO (folk lyrics generators),
- либо академическая/open-source без продуктовой упаковки.

### Значит
Если делать продукт как **специализированный генератор частушек с русской культурной точностью и сценариями использования**, это похоже на **реальную незанятую микронишу**.

Наиболее перспективное позиционирование:

> “Не AI для любых песен, а AI для быстрых, смешных, персонализированных русских частушек, которые сразу можно петь, читать на празднике или постить в соцсети.”

---

## Список ключевых источников

### Продукты и сервисы
1. Suno, AI Song Lyrics Generator: https://suno.com/hub/ai-song-lyrics-generator
2. Udio Help, Create a Song with Your Own Lyrics: https://help.udio.com/en/articles/10716221-create-a-song-with-your-own-lyrics
3. GSong AI Lyrics Generator: https://www.gsong.ai/Lyrics-Generator
4. Neume Folk Lyrics Generator: https://neume.io/lyrics-generator/folk
5. WNR.AI, Russian Hit Song Lyrics Generator: https://wnr.ai/templates/russian-hit-song-lyrics-generator
6. AI Music Service: https://aimusicservice.com/
7. These Lyrics Do Not Exist on Product Hunt: https://www.producthunt.com/products/these-lyrics-do-not-exist

### Open-source / models
8. dlebech/lyrics-generator: https://github.com/dlebech/lyrics-generator
9. gaodechen/gpt-lyrics: https://github.com/gaodechen/gpt-lyrics
10. bcash2233/lyrics-generator-gpt2: https://huggingface.co/bcash2233/lyrics-generator-gpt2
11. ECE1786-AG/lyrics-generator: https://huggingface.co/ECE1786-AG/lyrics-generator
12. nevoit/Song-Lyrics-Generator: https://huggingface.co/nevoit/Song-Lyrics-Generator

### Academic
13. UniLG (ACL 2023): https://aclanthology.org/2023.acl-long.56/
14. Unsupervised Melody-to-Lyrics Generation (ACL 2023): https://aclanthology.org/2023.acl-long.513/
15. SongComposer (ACL 2025): https://aclanthology.org/2025.acl-long.352/
16. To Sing like a Mockingbird (EACL 2017): https://aclanthology.org/E17-2048/
17. SongRewriter (Findings ACL 2023): https://aclanthology.org/2023.findings-acl.814/
18. Sudowoodo (EMNLP Demo 2023): https://aclanthology.org/2023.emnlp-demo.8/
19. GhostWriter (EMNLP 2015): https://aclanthology.org/D15-1221/
20. Rapformer (INLG 2020): https://aclanthology.org/2020.inlg-1.42/
21. DeepRapper (ACL 2021): https://aclanthology.org/2021.acl-long.6/
