# Архив: GoldSrc Config Engineer v2.4.x (Python + CustomTkinter)

Эта папка — **замороженная копия** последней линейки на Python. Активная разработка перенесена в корень репозитория (**Tauri 2 + React 18 + TypeScript**, v3).

## Запуск из архива

Из каталога `archive/v2-python-customtkinter/`:

```bash
pip install -r requirements.txt
python main.py              # GUI
python main.py --cli        # CLI
python -m pytest tests/     # тесты
```

Сборка `.exe`: `python build.py` (нужен PyInstaller).

## Содержимое

| Путь | Назначение |
|------|------------|
| `cfg_generator/` | GUI, ядро генерации, JSON-данные в `cfg_generator/data/` |
| `main.py`, `build.py` | Точка входа и PyInstaller |
| `requirements.txt` | Зависимости Python |
| `tests/`, `benchmarks/` | pytest и бенчмарки |

Копия игровых JSON для нового стека продублирована в **`data/`** в корне репозитория (общий источник для v3; при изменении логики сверяйте с архивом).

## Версия

Соответствует **v2.4.x** на момент переноса в архив. Полная пользовательская документация — в корневом `README.md` (разделы про возможности и поведение продукта сохраняются как спецификация для v3).
