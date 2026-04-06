# CS 1.6 — GoldSrc Config Engineer

[![CI](https://github.com/under2ker/GoldSrc-Config-Engineer/actions/workflows/ci.yml/badge.svg)](https://github.com/under2ker/GoldSrc-Config-Engineer/actions/workflows/ci.yml)

**Текущая версия: 3.2.1** · Профессиональный генератор конфигурационных файлов для **Counter-Strike 1.6** (GoldSrc)

Активная кодовая база — **Tauri 2 + React 18 + TypeScript** (Rust backend). Предыдущая стабильная линейка **v2.4.x (Python + CustomTkinter)** перенесена в **[`archive/v2-python-customtkinter/`](archive/v2-python-customtkinter/README.md)** и помечена как архив.

Ниже описаны **возможности продукта** (реализованы в v2.4; перенос в v3 идёт по [QUICK_START.md](QUICK_START.md) и [checklist.md](checklist.md)).

---

## Содержание

- [Разработка v3 (Tauri)](#разработка-v3-tauri)
- [Архив v2.4 (Python)](#архив-v24-python)
- [Возможности](#возможности)
- [Запуск](#запуск)
- [Установка](#установка)
- [CLI](#cli-режим)
- [Интерфейс: разделы и горячие клавиши](#интерфейс-разделы-и-горячие-клавиши)
- [Данные пользователя](#данные-пользователя)
- [Экспорт и установка в игру](#экспорт-и-установка-в-игру)
- [Загрузка конфига в запущенную CS 1.6](#загрузка-конфига-в-запущенную-cs-16)
- [Структура проекта](#структура-проекта)
- [Модульные .cfg](#модульные-cfg)
- [Сборка standalone .exe](#сборка-standalone-exe)
- [Тесты и CI](#тесты-и-ci)
- [Документация для разработчиков](#документация-для-разработчиков)
- [Дизайн-система](#дизайн-система)
- [Лицензия](#лицензия)

---

## Возможности

### Генерация конфигов

| Функция | Описание |
|--------|----------|
| **Быстрая настройка** | Режим, чувствительность, FPS, громкость — конфиг в несколько кликов |
| **Шаблоны** | Готовые пресеты стиля игры из `templates.json` |
| **Модульный экспорт** | Набор файлов: `autoexec.cfg` + `config/*.cfg` (алиасы, сеть, видео, звук, мышь, прицел, HUD, buy, коммуникация, бинды) |
| **Один файл** | Экспорт всего в один `autoexec.cfg` / `userconfig.cfg` |
| **Диагностика** | Проверка конфига, предупреждения, авто-исправления, оценка |
| **Сравнение** | Ваш конфиг vs про-пресет: radar chart + таблица отличий (прогрессивная подгрузка строк) |

### Режимы игры

| Режим | Назначение |
|-------|------------|
| Classic | Соревновательный 5v5 |
| KZ | Kreedz / climb |
| HNS | Hide and Seek |
| Surf | Surf-карты |
| DeathMatch | Перестрелка |
| War3 | Мод Warcraft 3 |
| Deathrun | Deathrun |
| Zombie | Zombie Plague и аналоги |
| GunGame | Gun Game / Arms Race |

### Пресеты про-игроков

Пресеты из `presets.json` (например): **f0rest**, **GeT_RiGhT**, **neo**, **markeloff**, **SpawN**, **HeatoN**, **Edward**, **cArn**, **Potti**, **elemeNt** — с командами, ролями и типичными настройками.

### Сеть и визуал

- **Сетевые пресеты** — LAN, Broadband, Medium, Poor, Terrible (rate, cmdrate, updaterate, ex_interp и др.)
- **Визуальные пресеты** — Competitive, Max FPS, Beautiful
- **Кроссхейр** — пресеты + **визуальный редактор** (canvas), экспорт, сравнение

### Железо и запуск

- Профили GPU (NVIDIA / AMD / Intel) и уровни производительности
- Подсказки и **launch options** для `hl.exe`

### Алиасы и скрипты

- База в `aliases.json`: movement, weapon, communication, utility, KZ/Surf, practice, цепочки **kz_chain**, HJ/CJ/LJ и др.
- Генерация **aliases.cfg** с маркерами `[SAFE]`, `[WAIT]`, `[PRACTICE]`, `[SERVERSIDE]`
- **Buy-скрипты** — визуальный редактор закупки + `buyscripts.json`

### Безопасность и импорт

- Импорт `.cfg` с диска или **URL**
- Блокировка опасных паттернов (`exec` вне контекста, `rcon`, подозрительные команды — см. `importer.py`)
- Валидация диапазонов CVAR

### Профили и история

- Сохранение профилей в `%APPDATA%\GoldSrcConfigEngineer\profiles\` (в т.ч. **gzip** `.json.gz`)
- История снимков конфига, лимит по количеству и по **размеру папки** (50 MB)
- Автосохранение и восстановление после сбоя

### Инструменты GUI (кратко)

| Раздел | Назначение |
|--------|------------|
| Главная | Обзор, быстрые действия |
| Быстрая настройка, шаблоны, избранные CVAR | Старт конфига |
| Режимы, пресеты, сеть, визуал, прицел, железо | Тонкая настройка |
| Расширенные | Покатегорийный список CVAR |
| Экспорт / импорт | Файлы и URL |
| Сравнение, клавиатура биндов, buy-редактор | Анализ и закупка |
| Чувствительность, диагностика, демо | Мышь, проверка, demo-настройки |
| Профили, история | Сохранённые состояния |
| Загрузка в игру | Путь к CS, копирование файлов, `exec`, очистка клиента |
| Параметры запуска | Конструктор командной строки `hl.exe` |
| Просмотр | Интерактивный превью с подсветкой синтаксиса |
| Настройки приложения | Тема, язык, автосохранение и др. |

### Дополнительно

- **Undo / Redo** для изменений конфига  
- **Глобальный поиск** (Ctrl+K): CVAR и переход по страницам  
- **F1** — встроенная справка  
- **F12** — отладочная панель (память, виджеты, after-задачи)  
- **Drag & Drop** импорта `.cfg` на странице «Импорт»  
- Оптимизации UI: skeleton на тяжёлых вкладках, порционная отрисовка списков, prefetch данных при наведении на пункт меню  

---

## Разработка v3 (Tauri)

Требования: **Node.js**, **Rust**. В корне репозитория:

```bash
npm install
npm run tauri dev
```

Сборка установщика: `npm run tauri build`. Игровые JSON для нового стека лежат в **`data/`** (копия из архива на этапе миграции).

---

## Архив v2.4 (Python)

Полный исходник GUI/CLI на Python: **`archive/v2-python-customtkinter/`** — см. [README в архиве](archive/v2-python-customtkinter/README.md). Запуск и тесты выполняются **из этой папки**, не из корня.

---

## Запуск

### Текущий GUI v3 (Tauri)

```bash
npm install
npm run tauri dev
```

### Устаревший GUI v2.4 (архив)

```bash
cd archive/v2-python-customtkinter
pip install -r requirements.txt
python main.py
```

По умолчанию открывается **графический интерфейс**. Для работы CLI см. раздел [CLI](#cli-режим) (относится к архивной сборке v2).

---

## Установка

### v3 (основная ветка разработки)

- **Node.js** (LTS), **Rust** (stable), **npm**
- ОС: Windows (основная цель), также macOS / Linux для Tauri

Зависимости фронтенда и Tauri — в **`package.json`** (`npm install`).

### Архив v2.4 (Python)

- **Python 3.10+** (рекомендуется 3.11–3.12), зависимости — **`archive/v2-python-customtkinter/requirements.txt`**
- **Windows** (основная цель), также возможны Linux/macOS при наличии Tk и шрифтов

| Пакет | Назначение |
|-------|------------|
| `customtkinter` | GUI |
| `colorama`, `rich` | Цветной вывод в CLI |
| `requests` | Импорт конфига по URL |
| `beautifulsoup4` | Разбор HTML при необходимости |
| `pyinstaller` | Сборка `.exe` (опционально) |
| `pytest`, `pytest-cov` | Тесты (разработка) |

Опционально для отладки: `psutil` (метрики в overlay в архиве).

---

## CLI-режим

Запуск без GUI — удобно для скриптов и автоматизации (**архив v2**, каталог `archive/v2-python-customtkinter/`).

```text
python main.py --cli                     # Интерактивное меню (rich)
python main.py --quick                   # Быстрый конфиг → файл
python main.py --mode kz                 # Режим KZ
python main.py --preset fnatic_f0rest    # Пресет про-игрока
python main.py --mode classic --sensitivity 2.2 --fps 144
python main.py --output my_autoexec.cfg
python main.py --lang en                 # Язык CLI (ru/en)
```

Флаги `--quick`, `--mode`, `--preset` подразумевают вывод в консоль и запись файла (см. `main.py`).

---

## Интерфейс: разделы и горячие клавиши

### Навигация

Боковая панель: **Главная**, блоки «Конфигурация», «Файлы», «Инструменты» — см. подписи кнопок в приложении.

### Часто используемые сочетания

| Сочетание | Действие |
|-----------|----------|
| **Ctrl+K** | Палитра поиска (CVAR / страницы) |
| **Ctrl+Z** / **Ctrl+Y** | Отмена / повтор |
| **F1** | Справка |
| **F12** | Отладочная информация |

Точный набор горячих клавиш см. в архиве: `archive/v2-python-customtkinter/cfg_generator/gui.py` (`_bind_hotkeys`) и во встроенной справке v2.

---

## Данные пользователя

| Путь (Windows) | Содержимое |
|----------------|------------|
| `%APPDATA%\GoldSrcConfigEngineer\profiles\` | Профили конфигов (`*.json` / `*.json.gz`), `_meta.json` |
| `%APPDATA%\GoldSrcConfigEngineer\history\` | Снимки истории |
| `%APPDATA%\GoldSrcConfigEngineer\~autosave.json` | Автосохранение для восстановления |

Настройки приложения и пользовательские данные не смешиваются с каталогом установки репозитория.

---

## Экспорт и установка в игру

1. Сгенерируйте конфиг в приложении и выполните **Экспорт** (один файл или полный модульный набор).
2. Скопируйте выходную папку (например `output\cstrike_…`) в каталог **`cstrike`** вашей установки CS 1.6.
3. Убедитесь, что `autoexec.cfg` лежит в корне `cstrike\` (или используйте `userconfig.cfg` по вашей схеме).
4. Модульные файлы — в `cstrike\config\` согласно структуре экспорта.

Подробности имён файлов — в разделе [Модульные .cfg](#модульные-cfg) и в `CHANGELOG.md`.

---

## Загрузка конфига в запущенную CS 1.6

На странице **«Загрузка в игру»** (deploy): обнаружение пути к игре, проверка процесса, копирование файлов в `cstrike`, при необходимости отправка команд в окно игры (Windows), отдельно — **очистка клиента** от лишних файлов (осторожно: пользовательские данные).

Требуется корректный путь к установке CS 1.6 и права на запись в `cstrike`.

---

## Структура проекта

```text
cspres/
├── Cargo.toml              # Workspace: goldsr_cfg_core + src-tauri
├── goldsr_cfg_core/        # Rust: `src/data/` (встраивание `data/*.json`), generator, exporter, …
├── package.json            # Vite + React 18, Tauri CLI
├── src/                    # Фронтенд TypeScript (stores, страницы — по мере миграции)
├── src-tauri/              # Tauri 2 + Rust (commands/, …)
├── data/                   # Игровые JSON для v3 (CVAR, режимы, пресеты, …)
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── archive/
│   └── v2-python-customtkinter/   # Архив: Python GUI/CLI v2.4, pytest, benchmarks
│       ├── cfg_generator/
│       ├── main.py
│       ├── build.py
│       ├── requirements.txt
│       ├── tests/
│       └── benchmarks/
└── output/                 # Примеры сгенерированных .cfg (по желанию)
```

---

## Модульные .cfg

При экспорте **полного набора** типичная структура:

| № | Файл | Назначение |
|---|------|------------|
| 1 | `autoexec.cfg` | Точка входа: `exec` модулей по порядку |
| 2 | `config/aliases.cfg` | Алиасы |
| 3 | `config/network.cfg` | Сеть |
| 4 | `config/video.cfg` | Видео / OpenGL |
| 5 | `config/audio.cfg` | Звук |
| 6 | `config/mouse.cfg` | Мышь |
| 7 | `config/crosshair.cfg` | Прицел |
| 8 | `config/hud.cfg` | HUD |
| 9 | `config/buyscripts.cfg` | Закупка |
| 10 | `config/communication.cfg` | Чат / голос |
| 11 | `config/bindings.cfg` | Бинды |

Точный список и порядок могут меняться — ориентируйтесь на сгенерированный `autoexec.cfg` и комментарии внутри файлов.

---

## Сборка установщика (v3)

```bash
npm install
npm run tauri build
```

Артефакты: `src-tauri/target/release/bundle/` (MSI / NSIS на Windows).

## Сборка standalone v2 (архив, PyInstaller)

```bash
cd archive/v2-python-customtkinter
pip install -r requirements.txt
python build.py
```

Результат обычно в **`archive/v2-python-customtkinter/dist/`**.

---

## Тесты и CI

### Архив Python (pytest)

```bash
cd archive/v2-python-customtkinter
pip install -r requirements.txt
python -m pytest tests/ -v
```

### v3

По мере внедрения: `cargo test` в `src-tauri/`, фронтенд-тесты (Vitest и т.д.) — см. [checklist.md](checklist.md).

---

## Документация для разработчиков

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — v3 (npm/Tauri); правки данных CVAR/режимов для архива v2 — пути в `archive/…`  
- **[CHANGELOG.md](CHANGELOG.md)** — история версий  
- Репозиторий может содержать внешние спецификации (например «GoldSrc Config Engineer») — ориентир по полноте CVAR и правилам генерации  

---

## Дизайн-система

Актуальное описание токенов, типографики, сетки, состояний и a11y: **[docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md)** — интерфейс **v3.2.1** (Tailwind 4, shadcn-стиль, Radix, OKLCH, тема по системе при первом запуске). Список изменений: [CHANGELOG.md](CHANGELOG.md).

Историческая тема v2 (CustomTkinter): в архиве **`archive/v2-python-customtkinter/cfg_generator/theme.py`** — палитра **midnight** и альтернативы. Миграция: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md). Ориентир по цветам (midnight v2):

| Элемент | Цвет |
|---------|------|
| Фон окна | `#0D1117` |
| Sidebar | `#161B22` |
| Карточки | `#1C2333` |
| Акцент | `#1F6FEB` |
| Успех | `#2EA043` |
| Предупреждение | `#D29922` |
| Ошибка | `#F85149` |
| Текст | `#E6EDF3` / `#8B949E` |

---

## Лицензия

Проект предназначен для **личного и образовательного** использования. Текст правовых условий — в файле **[LICENSE](LICENSE)**; при необходимости уточняйте распространение у автора.

---

**GoldSrc Config Engineer** — генератор глубоких CFG для CS 1.6 · *Ultimate Edition*
