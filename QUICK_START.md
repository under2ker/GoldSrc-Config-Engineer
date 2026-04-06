# 🚀 Быстрый старт-гайд: миграция на Tauri + React

> **Один набор документов (корень репозитория):** этот файл · [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) · [ADDITIONAL_IDEAS.md](ADDITIONAL_IDEAS.md) · [checklist.md](checklist.md)  
> **Актуальный продукт:** Python + CustomTkinter **v2.4.x**. Ниже — дорожная карта **будущего** v3.0 (Tauri + React), а не описание текущего релиза.

### Скелет v3 в репозитории

В корне добавлены **`src/`** (Vite + React 18 + TypeScript) и **`src-tauri/`** (Tauri 2). Требуются **Node.js** и **Rust**. Запуск окна разработки:

```bash
npm install
npm run tauri dev
```

Сборка установщика: `npm run tauri build`. **Архив GUI v2.4:** `archive/v2-python-customtkinter/` → `pip install -r requirements.txt` → `python main.py`.

## 📋 Что было прочитано и проанализировано

✅ **README.md** — v2.4.0, CustomTkinter GUI, полная документация  
✅ **CHANGELOG.md** — история развития (v0.1.0 → v2.4.0), множество оптимизаций  
✅ **checklist.md** — детальный чеклист миграции на v3.0+ (Tauri), метрики  

---

## 🎯 Основной вывод

**CustomTkinter больше не соответствует современным стандартам профессиональных десктопных приложений.** Необходимо переходить на:

### ⭐ **Tauri 2 + React 18 + TypeScript**

| Параметр | CustomTkinter | Tauri+React | Победитель |
|----------|---|---|---|
| Размер .exe | 45 MB | 8–15 MB | ✅ Tauri |
| Скорость запуска | ~2.5s | < 1.0s | ✅ Tauri |
| Потребление RAM | 120 MB idle | 40–70 MB idle | ✅ Tauri |
| Визуальный дизайн | Плоский, устаревший | Современный Shadcn/ui | ✅ Tauri |
| Производительность | 30 FPS, фризит | 60 FPS smoothly | ✅ Tauri |
| Кроссплатформенность | Windows | Win/Mac/Linux одним кодом | ✅ Tauri |
| Экосистема | Маленькая | npm (миллионы пакетов) | ✅ Tauri |

---

## 📚 Документы дорожной карты v3.0 (в корне репозитория)

### 1. **checklist.md**
- Чеклист для v3.0+
- Разбит на 4 фазы (Критично → Важно → Желательно → Бонусы) + инфраструктура
- Временные оценки и метрики успеха
- Таблица технологий и зависимостей

### 2. **MIGRATION_GUIDE.md** (подробное руководство)
- Сравнение всех фреймворков (Tauri, PyQt6, Electron, Dear ImGui)
- Полная архитектура приложения (папки, модули)
- Выбор и настройка библиотек:
  - **UI**: Shadcn/ui + Tailwind CSS
  - **State**: Zustand
  - **Forms**: React Hook Form + Zod
  - **Animations**: Framer Motion
  - **Charts**: Recharts
  - **Tables**: TanStack Table
  - **API**: Tauri invoke wrapper
- Примеры кода для каждой библиотеки
- План миграции по неделям

### 3. **ADDITIONAL_IDEAS.md** (бонусные идеи)
- UI/UX улучшения: glassmorphism, particle effects, breadcrumbs
- Технические оптимизации: semantic diff, caching, multi-monitor support
- Новый контент: +10 про-пресетов, +5 режимов, интерактивные туториалы
- Community features: Config marketplace, PDF экспорт
- Интеграция с CS 1.6 (запуск из приложения)

---

## 🏗️ Архитектура v3.0

```
Rust Backend (Tauri)          React Frontend (TypeScript)
├─ commands/                  ├─ components/
├─ services/                  ├─ pages/
├─ models/                    ├─ stores/ (Zustand)
├─ data/                      ├─ hooks/
└─ utils/                     ├─ lib/
                              └─ styles/ (Tailwind)
                
        ↔️ IPC (Tauri invoke)
```

---

## 📅 План разработки (10 недель)

### **Неделя 1–3: Архитектура и core** (🔴 КРИТИЧНО)

```bash
# Неделя 1: Setup
cargo tauri init
npm install -D tailwindcss postcss autoprefixer typescript
npx shadcn-ui@latest init

# Неделя 2: Rust core
# Выделить logic: generator.rs, validator.rs, exporter.rs, importer.rs
# SQLite schema для profiles, history, settings

# Неделя 3: Backend API
# Tauri commands: config.rs, profile.rs, game.rs, export.rs, import.rs
# TypeScript wrapper для invoke()
```

**Результат**: Полностью функциональный backend, работающий без UI

---

### **Неделя 4–7: Frontend страницы** (🟠 ВАЖНО)

```typescript
// Неделя 4–5: Layout + основные страницы
- Sidebar, Header, Titlebar (кастомный)
- Dashboard, Quick Setup, Game Modes, Presets

// Неделя 6: Основные инструменты
- Crosshair Editor (Canvas + Framer Motion)
- Comparison (Radar + TanStack Table)
- Export / Import

// Неделя 7: Остальное
- Preview, Diagnostics, Profiles, History, Settings
```

**Результат**: Приложение полностью функционально и красиво

---

### **Неделя 8–9: Полировка** (🟡 ЖЕЛАТЕЛЬНО)

```typescript
// Неделя 8: Animations & optimization
- Framer Motion для page transitions, button states
- Lazy loading, memoization, code splitting
- Unit tests (Vitest + React Testing Library)

// Неделя 9: E2E testing & docs
- Playwright E2E tests
- Оптимизация размера (.exe < 15 MB)
- Документация и README
```

**Результат**: Production-ready приложение v3.0

---

### **Неделя 10: Релиз**

```bash
# Windows MSI
cargo tauri build

# macOS DMG
cargo tauri build --target universal-apple-darwin

# Linux AppImage
cargo tauri build --target x86_64-unknown-linux-gnu

# Публиковать на GitHub Releases
```

---

## 🛠️ Необходимые зависимости

### Rust (src-tauri/Cargo.toml)
```toml
[dependencies]
tauri = { version = "2.0", features = ["shell-open", "fs-all", "dialog-all"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
rusqlite = { version = "0.29", features = ["bundled"] }
regex = "1"
tracing = "0.1"
```

### npm (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.4.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "framer-motion": "^10.16.0",
    "recharts": "^2.10.0",
    "@tanstack/react-table": "^8.13.0",
    "cmdk": "^0.2.0",
    "@tauri-apps/api": "^2.0.0",
    "@tauri-apps/plugin-dialog": "^2.0.0",
    "@tauri-apps/plugin-fs": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

---

## ✅ Чеклист начальных шагов

### Сегодня (подготовка):
- [ ] Читай **MIGRATION_GUIDE.md** полностью (2–3 часа)
- [ ] Смотри примеры кода Tauri + React (GitHub, YouTube)
- [ ] Выбери текстовый редактор: VS Code + Rust Analyzer + TypeScript extension

### На этой неделе (setup):
- [ ] Создай новый Tauri проект: `cargo tauri init`
- [ ] Клонируй текущий проект как backup
- [ ] Инициализируй TypeScript + Tailwind CSS + shadcn/ui
- [ ] Создай базовую структуру папок (см. MIGRATION_GUIDE)
- [ ] Настрой GitHub Actions CI/CD

### На следующей неделе (core logic):
- [ ] Портируй `generator.py` → `src-tauri/src/services/generator.rs`
- [ ] Портируй `validator.py` → `src-tauri/src/services/validator.rs`
- [ ] Портируй `exporter.py` → `src-tauri/src/services/exporter.rs`
- [ ] Настрой SQLite базу (profiles, history, settings)
- [ ] Напиши Tauri commands (config.rs, profile.rs)

### На третьей неделе (first UI):
- [ ] Напиши базовый Layout (Sidebar + Header + MainContent)
- [ ] Создай компоненты UI (Button, Input, Card, Slider, Select)
- [ ] Реализуй Zustand stores (configStore, profileStore, appStore)
- [ ] Напиши Dashboard страницу
- [ ] Тестируй Tauri invoke от React компонентов

---

## 🎓 Полезные ресурсы

### Официальная документация
- **Tauri docs**: https://tauri.app/start/ (актуальная версия — см. сайт, для v2 используйте разделы Tauri 2)
- **React docs**: https://react.dev/
- **TypeScript handbook**: https://www.typescriptlang.org/docs/

### UI/Design
- **Shadcn/ui**: https://ui.shadcn.com/ (копируй компоненты!)
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Radix UI**: https://www.radix-ui.com/ (примитивы для a11y)

### Libraries
- **Zustand**: https://github.com/pmndrs/zustand
- **React Hook Form**: https://react-hook-form.com/
- **Framer Motion**: https://www.framer.com/motion/
- **Recharts**: https://recharts.org/
- **TanStack Table**: https://tanstack.com/table/

### Learning
- YouTube: "Tauri Tutorial for Beginners"
- YouTube: "React 18 Complete Course"
- YouTube: "Shadcn/ui Component Library"

---

## 💡 Рекомендации

### 1. Новая версионировка
```
v2.4.0 (CustomTkinter)
v3.0.0-beta.1 (Tauri + React, ограниченный функционал)
v3.0.0-beta.2 (все фичи, тестирование)
v3.0.0 (релиз)
v3.1.0+ … v3.2.x (улучшения UI, дизайн-система, навигация, релизы 3.2.x)
```

### 2. Сохраняй совместимость конфигов
Убедись, что **экспортируемые .cfg файлы будут идентичны** v2.4.0. Пользователи должны иметь возможность использовать конфиги между версиями.

### 3. Помни о performance
- Не делай все за один render цикл (используй `React.memo`, `useMemo`)
- Кэшируй результаты генерации конфига (если параметры не изменились)
- Используй virtual scrolling для больших списков
- Optimize images (14×14 иконки, 64×64 фото про-игроков)

### 4. Тестирование
- Unit tests для Rust logic (generator, validator, exporter)
- Component tests для React UI
- E2E tests для основных flows (generate → export → load)
- Тестируй на Windows/macOS/Linux

### 5. Документация
- Обновляй README по мере разработки
- Веди CHANGELOG (какие фичи добавил, какие исправил)
- Пиши комментарии в сложном коде (особенно в Rust)
- Создай CONTRIBUTING.md для контрибьюторов

---

## 🎯 Финальная таблица: что делать дальше

| Действие | Время | Приоритет |
|----------|-------|-----------|
| Прочитать MIGRATION_GUIDE.md | 3 часа | 🔴 |
| Создать Tauri проект + setup | 4 часа | 🔴 |
| Портировать Rust logic | 20 часов | 🔴 |
| Создать backend API (Tauri commands) | 16 часов | 🔴 |
| Создать базовый Layout + компоненты | 24 часа | 🟠 |
| Реализовать основные страницы (8 шт) | 48 часов | 🟠 |
| Добавить animations и polish | 16 часов | 🟡 |
| Тестирование и оптимизация | 16 часов | 🟡 |
| **Итого на v3.0** | **~150 часов** | |

**Примерное время**: 150 часов = 4–5 недель (если работать 8 часов в день, 5 дней в неделю) или 8–10 недель (если 4 часа в день).

---

## 🎉 Результат (v3.0 Release)

```
GoldSrc Config Engineer v3.0
├─ Tauri 2 + React 18 + TypeScript
├─ Moderne design (Shadcn/ui + Tailwind)
├─ Windows/macOS/Linux support
├─ 8–15 MB .exe (vs 45 MB было)
├─ < 1.0s startup (vs 2.5s было)
├─ < 70 MB RAM idle (vs 120 MB было)
├─ 60 FPS smooth animations
├─ Все фичи v2.4.0 + новое
└─ Полная документация + видео-туториалы
```

---

**Готов начинать? Прочитай MIGRATION_GUIDE.md и создавай! 🚀**

Questions? Check ADDITIONAL_IDEAS.md для вдохновения.
