# Contributing to GoldSrc Config Engineer

Спасибо за интерес к проекту! Активная разработка ведётся на **v3 (Tauri 2 + React 18 + TypeScript)**. Линейка **v2.4 (Python)** лежит в **`archive/v2-python-customtkinter/`** и не развивается, кроме критичных исправлений по согласованию.

---

## Быстрый старт (v3)

```bash
git clone https://github.com/YOUR_USER/cspres.git
cd cspres
npm install
npm run tauri dev
```

Сборка релиза: `npm run tauri build`.

---

## Архив Python (v2.4)

Только для справки и сравнения логики при переносе в Rust:

```bash
cd archive/v2-python-customtkinter
pip install -r requirements.txt
python main.py          # GUI
python main.py --cli    # CLI
python -m pytest tests/
```

---

## Структура v3 (целевая)

```
src/                    # React + TypeScript
src-tauri/              # Rust, Tauri commands (src/commands/)
data/                   # Игровые JSON (CVAR, режимы, пресеты, …)
```

Структура архива v2 — см. **`archive/v2-python-customtkinter/README.md`**.

---

## Как добавить новый CVAR

1. Отредактируйте **`data/cvars.json`** (это рабочая копия для v3; дублирует смысл архива `archive/v2-python-customtkinter/cfg_generator/data/cvars.json`).
2. Найдите подходящую категорию (`mouse`, `video`, `audio`, `network`, `gameplay`).
3. Добавьте запись:

```json
"my_new_cvar": {
  "default": "1.0",
  "min": "0",
  "max": "10",
  "type": "float",
  "description_en": "Description in English",
  "description_ru": "Описание на русском"
}
```

4. После появления Rust-валидатора в v3 — добавьте тесты там; для архива Python: `python -m pytest archive/v2-python-customtkinter/tests/test_data_integrity.py` из каталога архива.

---

## Как добавить новый режим игры

1. Откройте **`data/modes.json`**
2. Добавьте новый ключ:

```json
"my_mode": {
  "name_en": "My Mode",
  "name_ru": "Мой режим",
  "description_en": "Description",
  "description_ru": "Описание"
}
```

3. Обновите генератор в Rust (после порта логики из `archive/.../cfg_generator/core/generator.py`).

---

## Как добавить пресет про-игрока

1. Откройте **`data/presets.json`**
2. Добавьте новый объект с полями как у существующих пресетов
3. Убедитесь, что команды и CVAR валидны

---

## Стиль кода

### TypeScript / React

- ESLint / Prettier — по мере подключения в репозитории
- Функциональные компоненты, хуки
- Имена файлов: `PascalCase` для компонентов, `camelCase` для утилит

### Rust

- `cargo fmt`, `cargo clippy`
- Команды Tauri в `src-tauri/src/commands/`

---

## Коммиты

- Формат: `type: краткое описание` (например `feat: add ping command`)
- Один логический коммит — одна задача

---

## Вопросы

Откройте issue или обсуждение в репозитории.
