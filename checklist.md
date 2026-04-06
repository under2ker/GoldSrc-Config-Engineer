# Чеклист развития GoldSrc Config Engineer → v3.0+

> **Связанные документы:** [QUICK_START.md](QUICK_START.md) (краткий план и чеклист первых шагов) · [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) (стек, структура, код) · [ADDITIONAL_IDEAS.md](ADDITIONAL_IDEAS.md) (идеи после v3.0) · [чеклист визуала.md](чеклист%20визуала.md) (ТЗ UI/UX + чеклист визуальной зрелости) · **[visual set](visual%20set)** (исходное ТЗ v1.0, референс «геймерский» dark; трекер UI/UX — **отдельная таблица ниже**)  
> **Версия приложения:** **3.2.1** (`package.json`, `src-tauri/Cargo.toml`, `tauri.conf.json`; в «О приложении» подтягивается из `package.json`).  
> **Текущая кодовая база:** корень репозитория — **Tauri 2 + React 18** (v3). Исходник Python **v2.4.x** перенесён в **`archive/v2-python-customtkinter/`** (архив). Этот файл описывает **целевую** миграцию и следующие шаги.

## Трекер бэклога (одна таблица, порядок работ)

| # | Задача | Приоритет | Статус | Комментарий |
|---|--------|-----------|--------|-------------|
| 1 | Табличный трекер в `checklist.md` | P0 | готово | этот раздел |
| 2 | `config/buyscripts.cfg` в модульном экспорте (`data/buyscripts.json`) | P0 | готово | `goldsr_cfg_core::buyscripts`, `exec` после `binds.cfg` |
| 3 | IPC: `export_config_snapshot`, `history_*`, `profile_update` | P0 | готово | `src-tauri/src/commands/` |
| 4 | Сортировка профилей: избранное сверху | P1 | готово | `ORDER BY is_favorite DESC` |
| 5 | API и типы TS (`HistoryEntry`, вызовы в `api.ts`) | P0 | готово | `src/types/api.ts`, `src/lib/api.ts` |
| 6 | Экспорт: снимок в истории после модульной сборки | P0 | готово | `ExportPage` + `history_append` |
| 7 | Профили: избранное и переименование | P1 | готово | `ProfilesPage` |
| 8 | Профили: список истории, черновик, удаление записи | P1 | готово | `ProfilesPage` |
| 9 | История при записи модульного набора из профиля в папку | P1 | готово | `onModularDeploy` |
| 10 | Сборка и проверка | P0 | готово | `cargo check`, `npm run build` |
| 11 | История после одиночной генерации `.cfg` (вкладка «Один файл») | P0 | готово | `ExportPage` + `export_config_snapshot` |
| 12 | `history_clear` + диалог «Очистить всё» | P1 | готово | `ProfilesPage` |
| 13 | `fetch_text_from_url` (http/https, лимит 512 КБ, UTF-8) | P0 | готово | `reqwest` blocking, `fetch_commands.rs` |
| 14 | Импорт: карточка «По ссылке» | P1 | готово | `ImportPage` (только Tauri) |
| 15 | `app_settings` + лимит истории + обрезка в `history_append` и при смене лимита | P0 | готово | `db.rs`, `settings_commands.rs` |
| 16 | Настройки: «Макс. записей истории» (10–500) | P1 | готово | `SettingsPage` |
| 17 | GitHub Actions: `cargo test`, `cargo check`, `npm run build` | P1 | готово | `.github/workflows/ci.yml` |
| 18 | Тест core: `buyscripts` не пустой | P2 | готово | `buyscripts.rs` `#[cfg(test)]` |
| 19 | CHANGELOG [Unreleased] — партия 11–20 | P2 | готово | этот релиз |
| 20 | Трекер: строки 11–20 зафиксированы | P2 | готово | таблица ниже |
| 21 | `history_count` + главная: карточка «История снимков» | P1 | готово | `DashboardPage`, диагностика |
| 22 | Главная: запись снимка в историю после «Сгенерировать .cfg» | P0 | готово | как на «Экспорт» |
| 23 | Диагностика: строка про базу истории | P2 | готово | `historyCount` |
| 24 | Профили: копия профиля (новое имя) | P1 | готово | `profileSave` + диалог |
| 25 | Профили: поиск по имени | P2 | готово | фильтр списка |
| 26 | Импорт по URL: проверка URL (Zod) до сети | P1 | готово | `importUrlSchema` |
| 27 | Палитра: ключевые слова для профилей / истории | P3 | готово | `AppCommandPalette` |
| 28 | `npm test` = cargo test + check + frontend build | P1 | готово | `package.json` |
| 29 | CI: один шаг `npm test` | P1 | готово | `.github/workflows/ci.yml` |
| 30 | CHANGELOG + трекер строки 21–30 | P2 | готово | документация |
| 31 | Горячая клавиша **Ctrl+Shift+P / ⌘⇧P** → «Профили» | P2 | готово | `MainLayout`, F1-таблица |
| 32 | Главная: обновление счётчиков при возврате на вкладку | P2 | готово | `visibilitychange` + `historyCount`, профили |
| 33 | Профили: фильтр списка **истории** (id, дата, размер) | P2 | готово | `ProfilesPage` |
| 34 | Профили: копирование **ID** в буфер | P3 | готово | кнопка «ID» |
| 35 | Настройки: «Открыть в проводнике» для найденной папки игры | P2 | готово | `openPath`, plugin-opener |
| 36 | Константа `HISTORY_MAX_ENTRIES_KEY` в `settingsKeys.ts` | P3 | готово | единый ключ |
| 37 | Экспорт: описание модульного набора (aliases, buyscripts, buy_binds) | P2 | готово | `ExportPage` |
| 38 | Палитра: ключевые слова для профилей (shift, ctrl shift p) | P3 | готово | `AppCommandPalette` |
| 39 | CHANGELOG [Unreleased] — партия 31–40 | P2 | готово | документация |
| 40 | Трекер: строки 31–40 | P2 | готово | таблица |
| 41 | IPC `get_app_paths_info` (каталог данных, путь к SQLite) | P1 | готово | `app_commands.rs` |
| 42 | API + Zod `AppPathsInfo` | P1 | готово | `api.ts`, `types/api.ts` |
| 43 | Диагностика: проверка путей данных | P2 | готово | `DiagnosticsPage` |
| 44 | Настройки: карточка «Данные приложения» (открыть / копировать) | P2 | готово | `SettingsPage`, `openPath` |
| 45 | Профили: копирование ID записи истории | P3 | готово | `ProfilesPage` |
| 46 | Импорт: кнопка «Очистить поле» у URL | P3 | готово | `ImportPage` |
| 47 | Тест core: модульный набор содержит `buyscripts.cfg` | P2 | готово | `exporter.rs` `#[cfg(test)]` |
| 48 | Палитра: ключевые слова для диагностики (sqlite, путь) | P3 | готово | `AppCommandPalette` |
| 49 | CHANGELOG [Unreleased] — партия 41–50 | P2 | готово | документация |
| 50 | Трекер: строки 41–50 | P2 | готово | таблица |
| 51 | Горячая клавиша **Ctrl+Shift+D / ⌘⇧D** → «Диагностика» | P2 | готово | `MainLayout`, F1 |
| 52 | `saveJsonToDisk` в `cfgFiles.ts` | P2 | готово | диалог JSON |
| 53 | Профили: сохранить **JSON** профиля на диск | P2 | готово | `ProfilesPage` |
| 54 | Профили: сохранить **JSON** снимка истории на диск | P2 | готово | `ProfilesPage` |
| 55 | Настройки «О приложении»: строка **`ping()`** (бэкенд) | P2 | готово | `SettingsPage` |
| 56 | Тест core: `autoexec.cfg` ссылается на `buyscripts.cfg` | P2 | готово | `exporter.rs` |
| 57 | Палитра: расширение ключевых слов для диагностики | P3 | готово | `AppCommandPalette` |
| 58 | Документация клавиш: запись про ⌘⇧D | P3 | готово | `keyboardShortcutsMeta` |
| 59 | CHANGELOG [Unreleased] — партия 51–60 | P2 | готово | документация |
| 60 | Трекер: строки 51–60 | P2 | готово | таблица |
| 61 | **Ctrl+Shift+S / ⌘⇧S** → «Настройки»; в полях **Ctrl+S** по-прежнему не перехватывается | P2 | готово | `MainLayout` |
| 62 | **Ctrl+Shift+H / ⌘⇧H** → «Главная» | P2 | готово | `MainLayout` |
| 63 | Документация клавиш: ⌘⇧S, ⌘⇧H | P3 | готово | `keyboardShortcutsMeta` |
| 64 | Палитра: ключевые слова для **Главная** и **Настройки** | P3 | готово | `AppCommandPalette` |
| 65 | Контекстное меню страницы: пункт **«Настройки…»** | P3 | готово | `MainLayout` |
| 66 | Тест core: **`core_version_is_semver_like`** | P2 | готово | `goldsr_cfg_core` `lib.rs` |
| 67 | «О приложении»: кнопка **«Копировать»** у строки ответа **`ping()`** | P2 | готово | `SettingsPage` |
| 68 | Диагностика: **«Копировать сводку»** (табличный текст проверок) | P2 | готово | `DiagnosticsPage` |
| 69 | CHANGELOG [Unreleased] — партия 61–70 | P2 | готово | документация |
| 70 | Трекер: строки 61–70 | P2 | готово | таблица |
| 71 | **Ctrl+Shift+Q / ⌘⇧Q** → «Быстрая настройка» | P2 | готово | `MainLayout` |
| 72 | **Ctrl+Shift+M / ⌘⇧M** → «Режимы» | P2 | готово | `MainLayout` |
| 73 | **Ctrl+Shift+G / ⌘⇧G** → «Сравнение конфигов» | P2 | готово | `MainLayout` |
| 74 | Документация клавиш (F1): ⌘⇧Q, ⌘⇧M, ⌘⇧G | P3 | готово | `keyboardShortcutsMeta` |
| 75 | Палитра: ключевые слова для мастера, режимов, сравнения | P3 | готово | `AppCommandPalette` |
| 76 | Контекстное меню: **Быстрая настройка**, **Режимы**, **Сравнение** | P3 | готово | `MainLayout` |
| 77 | Тест core: **`modes_catalog_non_empty`** (`modes.json`) | P2 | готово | `modes.rs` |
| 78 | Страница «Сравнение»: подсказка про **⌘⇧G** и F1 | P3 | готово | `ComparisonPage` |
| 79 | CHANGELOG [Unreleased] — партия 71–80 | P2 | готово | документация |
| 80 | Трекер: строки 71–80 | P2 | готово | таблица |
| 81 | **Ctrl+Shift+B / ⌘⇧B** → «Про-пресеты» | P2 | готово | `MainLayout` |
| 82 | **Ctrl+Shift+X / ⌘⇧X** → «Прицел» | P2 | готово | `MainLayout` |
| 83 | **Ctrl+Shift+T / ⌘⇧T** → «Чувствительность мыши» | P2 | готово | `MainLayout` |
| 84 | Документация клавиш (F1): ⌘⇧B, ⌘⇧X, ⌘⇧T | P3 | готово | `keyboardShortcutsMeta` |
| 85 | Палитра: ключевые слова для пресетов, прицела, чувствительности | P3 | готово | `AppCommandPalette` |
| 86 | Контекстное меню: **Про-пресеты**, **Прицел**, **Чувствительность** | P3 | готово | `MainLayout` |
| 87 | Тест core: **`presets_catalog_non_empty`** (`presets.json`) | P2 | готово | `presets.rs` |
| 88 | Страница «Про-пресеты»: подсказка про **⌘⇧B** и F1 | P3 | готово | `PresetsPage` |
| 89 | CHANGELOG [Unreleased] — партия 81–90 | P2 | готово | документация |
| 90 | Трекер: строки 81–90 | P2 | готово | таблица |
| 91 | Главная: **«Заполненность конфига»** (10 разделов, прогресс); трекер **V-25** → готово | P2 | готово | `configCompleteness.ts`, `DashboardConfigCompletenessCard`, `checklist.md` |
| 92 | Релиз **v3.2.0**: версия в `package.json` / Tauri / Cargo; **CHANGELOG** (корень + `public/` + `dist/`); README, DESIGN_SYSTEM, чеклисты | P2 | готово | дата релиза в журнале: 2026-04-06 |
| 93 | **Миграция данных**: модуль `goldsr_cfg_core/src/data/` — modes, presets, cvars, aliases, buyscripts; JSON в `data/` | P1 | готово | см. раздел «Миграция данных» в этом файле |
| 94 | Выделить при необходимости **`tailwind.config.ts`** (сейчас токены в `@theme inline` + `globals.css`) | P3 | готово | `tailwind.config.ts`, `@config` в `globals.css`, `components.json` |
| 95 | **Zustand persist** в IndexedDB (`idb-keyval`) для черновика/настроек UI в браузере — без дублирования SQLite | P2 | готово | `configStore` + persist `gce-config-v1`, в Tauri без persist |
| 96 | **Dashboard**: карточка со **статистикой профилей / истории** из SQLite (Tauri), счётчики как на главной | P2 | готово | блок «Статистика» в `DashboardInsightCards` + карточки профилей/истории ниже |
| 97 | Вынести **`AlertDialog`** (shadcn) для разрушительных действий вместо общего `Dialog` где уместно | P3 | готово | `alert-dialog.tsx`, импорт, профили (удаление/история) |
| 98 | **Формы**: связать критичные `Input`/`Textarea` с **react-hook-form + Zod** там, где много полей | P3 | готово | `form.tsx`, `formSchemas.ts`, **Настройки** (лимит истории), **Импорт** (URL, имя профиля); мастер — только Select, без текстовых полей |
| 99 | **Combobox** или поиск в **`Select`** для длинных списков (режимы/пресеты) — по желанию | P4 | готово | `popover` + `command` (cmdk), `ModeSearchSelect` / `PresetSearchSelect`, главная / экспорт / мастер |
| 100 | **TanStack Table** для таблиц без текущей виртуализации (если появятся тяжёлые гриды) | P4 | готово | **Сравнение**: вкладка «Таблица», сортировка, фильтр категории, поиск, пагинация, CSV |
| 101 | **Framer Motion** — страничные переходы / микроанимации; согласовать с `prefers-reduced-motion` | P4 | готово | `PageRouteMotion`, `animations.css`, `useReducedMotion` + настройка в приложении |
| 102 | **i18n** — вынести строки UI (хотя бы RU/EN слой) | P4 | готово | `src/locales/ru.json`, `en.json`, `useI18n` + хром: Sidebar, Header, MainLayout, Breadcrumbs, TitleBar, `routeMeta` |
| 103 | Документировать в README **дерево `goldsr_cfg_core/src/data/`** для контрибьюторов | P3 | готово | таблица в README «Структура проекта» |
| 104 | Скрипт или **`build.rs` проверка**: `data/*.json` валидный JSON при сборке core (опционально) | P4 | готово | `goldsr_cfg_core/build.rs` — парсинг всех `../data/*.json`, `cargo:rerun-if-changed` на каждый файл |
| 105 | Расширить **типизацию** `aliases.json` в Rust (`serde` структуры вместо части `Value`) — по мере необходимости | P4 | готово | `aliases.rs`: `AliasDef` (untagged + `TaggedAlias`), `AliasSection`; корень пока через `Value` → `from_value` по секциям |
| 106 | E2E / smoke: **генерация → экспорт → модульный набор** в CI (Playwright или скрипт) | P4 | готово (core) | CI: `npm test` → `cargo test`; smoke **`smoke_single_cfg_and_modular_pipeline`** в `goldsr_cfg_core`; UI/E2E — п. 116 |
| 107 | Периодически синхронизировать **чеклист визуала** с закрытыми V-** пунктами** | P3 | готово | 2026-04-06: V-09/V-14/V-23/Vis-18 + Vis-25 (i18n), приоритеты визуала |
| 108 | Релиз **v3.2.1**: версии в манифестах, CHANGELOG, тег **`v3.2.1`**, GitHub Release | P2 | готово | 2026-04-02 |

### Партия 109–118 (порядок: ~10 шагов за итерацию)

| # | Шаг | Приоритет | Статус | Комментарий |
|---|-----|-----------|--------|-------------|
| 109 | **Smoke core**: один `#[test]` — `generate_single_cfg` + `generate_modular_files`, непустой вывод | P4 | готово | `exporter.rs` → `smoke_single_cfg_and_modular_pipeline` |
| 110 | Зафиксировать покрытие п. **106** через **`npm test`** / `cargo test` | P4 | готово | см. строка 106 |
| 111 | Комментарий в **CI** (`ci.yml`), что smoke входит в `cargo test` | P4 | готово | `.github/workflows/ci.yml` |
| 112 | **i18n**: блок «Генерация по режиму» и тосты на **главной** (`DashboardPage`) | P4 | готово | `dashboard.*` в `ru.json`/`en.json`, `DashboardPage` |
| 113 | **i18n**: **Dashboard** — профили, история, ссылки «Открыть…» | P4 | готово | Hero, Insight, Readiness, Completeness, QuickActions, Recent, GameTip; `formatRelativeTime` по локали |
| 114 | **i18n**: **QuickSetup** — шаги, кнопки, подсказки | P4 | не начато | |
| 115 | **i18n**: **Export** — вкладки, модульный набор, диалоги | P4 | не начато | |
| 116 | Опционально: **Playwright** (или аналог) — smoke открытия приложения / маршрута | P4 | не начато | после стабилизации i18n страниц |
| 117 | **V-07**: индикатор «несохранённые правки» (store + UI) | P3 | не начато | см. приоритет визуала ниже |
| 118 | Свести дубли заголовков на страницах с подзаголовком **Header** | P4 | не начато | контент vs `layout.page` |

_Партия 119+ — после закрытия 112–118 или по пополнению таблицы._

## Трекер UI/UX по документу «[visual set](visual%20set)»

Источник: **ТЗ UI/UX-редизайн v1.0** (июнь 2025), изначально под CustomTkinter; в проекте v3 — **Tauri + React + shadcn**. Статусы — сверка с текущим кодом (2026-04).

| # | Пункт (раздел ТЗ) | Статус | Комментарий / где смотреть |
|---|-------------------|--------|----------------------------|
| V-01 | §2.1 Цветовая палитра (HEX: bg_primary, accent_blue, …) | частично | Токены **OKLCH** в `src/styles/globals.css` (`.dark`), смысл как у ТЗ, не копия HEX-таблицы |
| V-02 | §2.2 Типографика (Segoe UI, JetBrains Mono для чисел) | частично | В `globals.css` первым идёт **Inter**; mono: JetBrains + fallback; размеры H1–body близки к сетке |
| V-03 | §2.3–2.4 Сетка 4px, отступы, «уровни» теней | частично | `--space-*`, `layoutTokens`; тени упрощённые (sidebar `shadow`, карточки `shadow-sm`) |
| V-04 | §3.1 Sidebar: иконки, секции, разделители | готово | `Sidebar.tsx`: Lucide **18px**, группы **«Разделы»** / **«Инструменты»**, `Separator` |
| V-05 | §3.1.2 Блок логотипа (иконка 32×32, две строки названия) | частично | Свой бренд (**GoldSrc Config Engineer**, иконка `Wrench` в квадрате), не CS 1.6 / CFG Generator из макета |
| V-06 | §3.1.3 Nav item: hover, активное состояние | готово | Hover `transition-colors`; активный — **левая полоса** `border-l-sidebar-primary` + фон |
| V-07 | §3.1.5 Статус-бар внизу sidebar («Config loaded», точка, версия) | частично | **Недавний .cfg** — имя последнего сохранения + индикатор (список `recentConfigs`); не отслеживает «несохранённые правки» |
| V-08 | §3.1.6 Узкий / развёрнутый sidebar (опционально v2) | готово | `appStore.sidebarCollapsed`, ширина `w-60` / `3.75rem`, кнопка сворачивания |
| V-09 | §3.2.1 Заголовок страницы H1 + подзаголовок + линия | частично | **`Header`**: **H1 + подзаголовок** по маршруту (`getLayoutPage` / `src/locales/*.json`); разделитель — **border-b** шапки; вводные на страницах остаются |
| V-10 | §3.2.2 Карточки: radius ~12px, border, hover | частично | `Card`: усилен hover border **primary/40** + lift (как раньше) |
| V-11 | §3.2.3 Область прокрутки и стили scrollbar | частично | **`#main-content`** + **`ScrollArea`**: полоса **6px** (`w-1.5`), thumb с hover (`scroll-area.tsx`) |
| V-12 | §3.3.1 Слайдер: одна строка label + трек + значение | частично | + **`PreviewPage`** (размер шрифта); трек **6px** глобально (`slider.tsx` `h-1.5`) |
| V-13 | §3.3 Кнопка Generate: зелёный акцент, состояния loading/done | частично | Вариант **`success`** (`button.tsx`); основные **Сгенерировать** / **Сформировать** на главной, мастере, экспорте, режимах, пресетах |
| V-14 | §5 Анимации и §10 Ph.2 hover на карточках/кнопках | частично | Смена маршрута: **`PageRouteMotion`** (Framer Motion) + **`animations.css`**; при «Уменьшить анимации» / `prefers-reduced-motion` — длительность 0; hover карточек/кнопок — **разной** глубины |
| V-15 | §6 Quick Setup по структуре ТЗ | частично | `QuickSetupPage`: шаги, Progress, карточки — **есть**, вёрстка не копия ASCII |
| V-16 | §7 Иконки outline 18px (Lucide/Phosphor) | готово | **Lucide** `strokeWidth` ~1.75, сайдбар **18px** |
| V-17 | §8 / Ph.3 Toast success/error | готово | **sonner** по приложению |
| V-18 | §10 Ph.3 Compare с подсветкой diff | готово | `ComparisonPage` + `diffLinesLazy` / виртуализация |
| V-19 | §10 Ph.4 Кастомный title bar | готово | `TitleBar.tsx`, `tauri.conf.json` → `decorations: false` |
| V-20 | §10 Ph.4 Контекстное меню + горячие клавиши | готово | ПКМ по контенту `MainLayout`, палитра **⌘K**, **F1** |
| V-21 | §10 Ph.1 Минимальный размер окна | готово | `tauri.conf.json`: **minWidth 1280**, **minHeight 600** (согласовано с `MainLayout` `min-w-[1280px]`) |
| V-22 | §10 Ph.3 Splash screen | частично | **`SplashScreen`**: лого + версия, **градиент фона**, fade, только **Tauri** |
| V-23 | §10 Ph.3 Подписи секций sidebar EN «CONFIGURATION» / «FILES» | частично | Подписи групп в **`src/locales`**: **RU/EN** (`sidebar.sections`, `sidebar.tools`); та же идея секций |
| V-24 | §10 Ph.3 Карточки пресетов с аватарами | частично | **`CatalogAvatar`**: круг с **инициалами** по названию; на **режимах** и **пресетах**; не фото игроков |
| V-25 | §10 Ph.3 Progress bar «заполненности конфига» | готово | **Главная**: «Готовность окружения» (0–100, окружение) + «Заполненность конфига» (10 разделов по CVAR/биндам, цвет полосы по порогам; см. v2 `gui.py`) — `configCompleteness.ts`, `DashboardConfigCompletenessCard` |

### Визуальная партия 1 (старт по `visual set`, 2026-04)

| # | Шаг | Статус | Комментарий |
|---|-----|--------|-------------|
| Vis-01 | Окно Tauri: **minWidth / minHeight** | готово | `src-tauri/tauri.conf.json` |
| Vis-02 | **Недавний .cfg** в подвале sidebar + точка | готово | `Sidebar.tsx` → `SidebarRecentStatus`, данные `loadRecentConfigs` |
| Vis-03 | Событие при **добавлении** в недавние (обновление статуса сразу) | готово | `addRecentConfig` → `dispatchRecentUpdated()` |
| Vis-04 | Карточки: чуть сильнее **hover border** | готово | `components/ui/card.tsx` → `border-primary/40` |
| Vis-05 | Главная прокрутка: **тонкий scrollbar** | готово | `globals.css` → `#main-content` |
| Vis-06 | **Чувствительность**: строка **m_yaw** label \| слайдер \| значение | готово | `SensitivityPage.tsx` |
| Vis-07 | **Прицел**: три слайдера в сетке как в ТЗ | готово | `CrosshairPage.tsx` |

### Визуальная партия 2 (2026-04)

| # | Шаг | Статус | Комментарий |
|---|-----|--------|-------------|
| Vis-08 | Кнопка **`variant="success"`** (зелёный CTA) | готово | `components/ui/button.tsx` |
| Vis-09 | Генерация .cfg: **success** на главной, мастере, экспорте, режимах, пресетах | готово | `DashboardPage`, `QuickSetupPage`, `ExportPage`, `GameModesPage`, `PresetsPage` |
| Vis-10 | **Просмотр**: слайдер размера шрифта — сетка label \| трек \| px | готово | `PreviewPage.tsx` |
| Vis-11 | **ScrollArea** (Radix): ширина 6px, hover thumb | готово | `scroll-area.tsx` |
| Vis-12 | **Slider**: высота трека **6px** (как в ТЗ) | готово | `slider.tsx` → `h-1.5` |

### Визуальная партия 3 (2026-04)

| # | Шаг | Статус | Комментарий |
|---|-----|--------|-------------|
| Vis-13 | **Splash** при старте (Tauri) | готово | `SplashScreen.tsx`, `MainLayout`; `prefers-reduced-motion` — без задержки |
| Vis-14 | **CatalogAvatar** — инициалы в круге | готово | `CatalogAvatar.tsx` |
| Vis-15 | **CatalogItemCard** — слот `avatar` | готово | `CatalogItemCard.tsx` |
| Vis-16 | **Режимы** и **про-пресеты**: аватар на карточке | готово | `GameModesPage`, `PresetsPage` |
| Vis-17 | Экспорт: **«Собрать модульный набор»** — `success` + `loading` | готово | `ExportPage.tsx` |

### Визуальная партия 4 (2026-04)

| # | Шаг | Статус | Комментарий |
|---|-----|--------|-------------|
| Vis-18 | Шапка: **подзаголовок** под H1 по разделам | готово | `Header` prop `subtitle`; тексты из **`layout.page`** в `ru.json` / `en.json` |
| Vis-19 | Шапка: высота под две строки (`min-h`, `line-clamp`) | готово | `Header.tsx` |
| Vis-20 | **Splash**: лёгкий **градиент** фона | готово | `SplashScreen.tsx` |

### Визуальная партия 5 (2026-04)

| # | Шаг | Статус | Комментарий |
|---|-----|--------|-------------|
| Vis-21 | **V-25**: индикатор «готовности» с **Progress** | готово | `DashboardReadinessCard.tsx`, главная |
| Vis-22 | Формула **0–100** (каталог, недавние файлы, БД/импорт, финальный шаг) | готово | `computeReadinessScore` |

### Визуальная партия 6 (2026-04)

| # | Шаг | Статус | Комментарий |
|---|-----|--------|-------------|
| Vis-23 | Дизайн-система: **`layoutTokens`** (`pageShell*`, `pageLeadClass`, сайдбар, `CardDescription`) | готово | `src/lib/layoutTokens.ts`, `docs/DESIGN_SYSTEM.md` |
| Vis-24 | **V-25**: карточка **«Заполненность конфига»** (10 секций, прогресс, список разделов) | готово | `configCompleteness.ts`, главная; палитра ⌘K: ключевые слова «готовность», «заполненность» |

### Визуальная партия 7 (2026-04)

| # | Шаг | Статус | Комментарий |
|---|-----|--------|-------------|
| Vis-25 | Оболочка: **i18n RU/EN** (сайдбар, шапка, крошки, title bar, контекстное меню) | готово | `useI18n`, `src/locales/*.json`; язык в **Настройках** |

**Приоритет следующих визуальных шагов:** индикатор **несохранённых правок** (V-07); дубли текста на страницах vs подзаголовок шапки; расширение **i18n** на страницы контента; токены **HEX 1:1** (V-01) при необходимости.

## 🎯 Новая архитектура: Tauri 2 + React 18 + Rust

**Миграция с CustomTkinter на современный стек.**

---

## 🔴 КРИТИЧНО — Фаза 1: Подготовка и архитектура (2–3 недели)

### Архитектурное планирование

- [x] **Выделение core логики в Rust crate** — `goldsr_cfg_core/` (workspace member), публичный API: каталоги режимов/пресетов из `data/*.json` через `include_bytes!`:
  - `src/lib.rs` — `GameModeSummary`, `ProPresetSummary`, `core_version`
  - `src/modes.rs`, `src/presets.rs` — загрузка и списки
  - [x] `generator.rs` — `create_mode_config`, `create_preset_config`, `generate_single_cfg` (порт с Python)
  - [x] `cvars_catalog.rs`, `cfg_config.rs`, `validator.rs` — каталог CVAR, `validate_settings_keys` (strict опционально)
  - [x] `exporter.rs`, `importer.rs` + `regex` в core; профили — не `profiles.rs` в core, а SQLite в `src-tauri` (`db.rs`) + `rusqlite`

- [x] **Tauri backend слой** — `src-tauri/src/commands/`:
  - [x] `config_commands.rs` — `ping`, `get_game_modes`, `get_pro_presets`, `generate_config`, `check_cfg_import_safety`, **`export_modular_config`**, **`parse_import_cfg`**
  - [x] Экспорт одного `.cfg` — UI: `@tauri-apps/plugin-dialog` + `@tauri-apps/plugin-fs` (сохранение UTF-8), capabilities `dialog` + `fs` + scope `**`
  - [x] Модульный экспорт и парсинг импорта: `export_modular_config` → список файлов; `parse_import_cfg` → JSON (`CfgConfig`); опасные команды — `check_cfg_import_safety`
  - [x] `profile_commands.rs` — `profile_save`, `profile_list`, `profile_load`, `profile_delete`
  - [x] `game_commands.rs` — `detect_game_installation`, `deploy_modular_files`; `execute_console_command_stub` — заглушка (`Err`)
  - Каждый command возвращает `Result<T, String>` или кастомный `ApiError`

- [x] **TypeScript type-safety** — `src/types/api.ts`:
  - `GenerateConfigRequest`, `GenerateConfigResponse`, `Profile`, `ModularFile`, обёртки Zod где нужно
  - Zod-схемы для `get_game_modes` / `get_pro_presets`
  - Типы `GameModeSummary`, `ProPresetSummary`

- [~] **State management** — Zustand:
  - [x] `stores/catalogStore.ts` — режимы и пресеты с IPC
  - [x] `stores/configStore.ts` — выбор режима/пресета + **черновик импорта** (`stagedProfileJson`); `stores/appStore.ts`; `stores/profileStore.ts` — список профилей + **`refreshProfiles`**
  - [~] Persist в IndexedDB — `idb-keyval` (`src/lib/idbStorage.ts`); подключение к Zustand — по желанию; **профили в Tauri** уже из SQLite

### Миграция данных

- [x] **JSON → модуль Rust `src/data/`** — каталоги по-прежнему в **`data/*.json`** (корень репозитория), встраиваются через `include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/../data/…"))` и парсятся в типизированные структуры / `serde_json::Value` где нужна гибкость:
  - [x] `cvars.json` → `goldsr_cfg_core/src/data/cvars.rs` (`CvarsCatalog`)
  - [x] `modes.json` → `goldsr_cfg_core/src/data/modes.rs`
  - [x] `presets.json` → `goldsr_cfg_core/src/data/presets.rs`
  - [x] `aliases.json` → `goldsr_cfg_core/src/data/aliases.rs`
  - [x] `buyscripts.json` → `goldsr_cfg_core/src/data/buyscripts.rs` (единый путь к JSON, как у остальных)
  - [x] `lib.rs` реэкспортирует публичный API без изменений для `src-tauri` и фронта
  - [x] SQLite schema для профилей, истории, настроек — **реализовано** в `src-tauri/src/db.rs` (`rusqlite`, не sqlx)

- [x] **Database schema** — SQLite при старте приложения (`CREATE TABLE IF NOT EXISTS`):
  - `profiles` — `id`, `name`, `config_json`, `created_at`, `updated_at`, `is_favorite`
  - `history` — `profile_id`, `config_json`, `created_at`, `size_bytes`
  - `app_settings` — `key`, `value`

---

## 🟠 ВАЖНО — Фаза 2: Frontend с Shadcn/ui (3–4 недели)

> **Статус (2026-04-02, v3.2.1):** **Dashboard** — готовность окружения, **заполненность конфига** (10 разделов), дизайн-токены и единая оболочка страниц (`layoutTokens`), тема по **`prefers-color-scheme`** при первом запуске, документация **[docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md)**. Навигация: горячие клавиши **⌘⇧** для основных разделов, контекстное меню и палитра (⌘K). Профили, история, импорт по URL, диагностика и пути данных — как в [CHANGELOG](CHANGELOG.md) для v3.2.x. Опционально дальше: Framer Motion, расширенный i18n, **TanStack Table** где уместно.

### UI Framework и дизайн-система

- [~] **Проект структура** (фактически: `src/pages/` + `src/components/layout/`, не вложенные в `components/`):
  ```
  src/
  ├── components/
  │   ├── ui/                    # shadcn/ui компоненты
  │   │   ├── button.tsx
  │   │   ├── input.tsx
  │   │   ├── select.tsx
  │   │   ├── slider.tsx
  │   │   ├── card.tsx
  │   │   ├── tabs.tsx
  │   │   ├── dialog.tsx
  │   │   └── ...
  │   ├── layout/
  │   │   ├── Sidebar.tsx        # Навигация (боковая панель)
  │   │   ├── Header.tsx         # Заголовок, поиск (Cmd+K)
  │   │   ├── Toast.tsx          # Уведомления
  │   │   └── Titlebar.tsx       # Кастомный titlebar
  │   ├── pages/                 # в чеклисте изначально здесь; сейчас см. src/pages/
  │   │   ├── DashboardPage.tsx
  │   │   ├── QuickSetupPage.tsx
  │   │   ├── GameModesPage.tsx
  │   │   ├── PresetsPage.tsx
  │   │   ├── CrosshairEditorPage.tsx
  │   │   ├── ComparisonPage.tsx
  │   │   ├── ExportPage.tsx
  │   │   ├── ImportPage.tsx
  │   │   ├── PreviewPage.tsx
  │   │   ├── DiagnosticsPage.tsx
  │   │   ├── SettingsPage.tsx
  │   │   └── ...
  │   └── common/
  │       ├── CfgTextPreview.tsx  # лёгкая подсветка .cfg (без Prism)
  │       ├── CrosshairCanvas.tsx # Canvas-превью прицела
  │       ├── Skeleton.tsx        # Skeleton screens (как в v2.4)
  │       ├── RadarChart.tsx      # Recharts
  │       ├── CrosshairCanvas.tsx # Canvas с прицелом
  │       ├── VirtualTable.tsx    # TanStack Table
  │       └── (реализация: `layout/AppCommandPalette.tsx` + `cmdk`)
  ├── stores/
  │   ├── configStore.ts
  │   ├── profileStore.ts
  │   ├── appStore.ts
  │   └── index.ts
  ├── types/
  │   ├── api.ts
  │   ├── domain.ts
  │   └── index.ts
  ├── lib/
  │   ├── api-client.ts           # Tauri invoke wrapper
  │   ├── validators.ts           # Zod schemas
  │   └── utils.ts
  ├── hooks/
  │   ├── useConfig.ts
  │   ├── useProfiles.ts
  │   ├── useAsync.ts
  │   └── ...
  ├── styles/
  │   ├── globals.css
  │   └── animations.css          # Framer Motion + CSS
  └── App.tsx
  ```

- [~] **Tailwind CSS + Shadcn/ui**:
  - [~] Установка: shadcn CLI `init` не использовался (ошибка доступа к `.pytest_cache`); вручную: `vite` + `@tailwindcss/vite`, `shadcn/tailwind.css`, `components.json`, алиас `@/*`
  - [ ] Кастомизация: отдельный `tailwind.config.ts` (сейчас токены в CSS `@theme inline`)
  - [x] Тема switching: **Настройки** → Switch + Select; класс `dark` на `<html>`, `localStorage` (`appPrefs` + `themeBootstrap.ts`)
  - [x] Шрифты: Segoe UI, Consolas — в `globals.css` (`@layer base`)

- [~] **Компоненты UI**:
  - [x] `Button` — loading, variants
  - [~] `Input` + `Textarea` — без RHF/Zod; **`Slider`** — страница «Просмотр»
  - [~] `Select` — дашборд, мастер, экспорт, настройки; **`RadioGroup`** — экспорт (режим/пресет); `Combobox` нет
  - [x] `Switch` — быстрая настройка (пресет), настройки (тема)
  - [x] `Progress` — мастер (шаги), диагностика (оценка)
  - [x] `Card` — карточки режимов/пресетов
  - [x] `Tabs`
  - [~] `Dialog` — подтверждение сброса на странице импорта; `AlertDialog` отдельно не вынесен
  - [x] `ScrollArea`
  - [x] `Tooltip`
  - [x] `Badge` / `Label` (+ `Separator`)
  - [x] `Skeleton` — базовый shimmer

### Основные страницы

- [~] **Dashboard** — hero, insight-карточки, quick actions, **недавние `.cfg`**, **Select режима** с запоминанием последнего (`localStorage`), генерация и превью с подсветкой; нет статистики профилей из SQLite
- [x] **Quick Setup** — `QuickSetupPage.tsx`: 4 шага, Progress, режим + опциональный пресет (Switch), генерация и сохранение
- [~] **Game Modes** — карточки, генерация, превью с подсветкой (`GameModesPage.tsx`)
- [~] **Pro Presets** — то же (`PresetsPage.tsx`); нет фото 64×64, rating, сортировки
- [~] **Crosshair Editor** — `CrosshairPage.tsx` + `CrosshairCanvas`: слайдеры, цвета, обводка, копирование ориентировочных CVAR; нет side-by-side пресетов / привязки к каталогу CVAR
- [~] **Comparison** — `diffLinesLazy` + два файла; цветные блоки (`ComparisonPage.tsx`)
- [x] **Export** — `ExportPage.tsx`: один файл + **модульный** (`exportModularConfig`, предпросмотр, `deployModularFiles` в Tauri)
- [~] **Import** — превью + **drag-and-drop .cfg**; в Tauri — **`parseImportCfg`**, счётчики разбора, **сохранение в профиль**; URL loader нет
- [x] **Профили** — `ProfilesPage.tsx` (`/profiles`): список SQLite, экспорт одного / модульного из JSON, просмотр, удаление; в сайдбаре и палитре
- [x] **Preview** — `PreviewPage.tsx`: открыть/вставить, Slider размера шрифта, подсветка
- [x] **Diagnostics** — ping, каталоги, localStorage, ленивый `diff`, оценка 0–100; строка про историю недавних `.cfg`
- [~] **Settings** — тема Switch+Select, язык, **поиск папки игры** (Tauri), о приложении, **таблица горячих клавиш** (`keyboardShortcutsMeta`); автосохранение черновика в профили — позже

### Layout / навигация

- [x] **MainLayout** — `TitleBar` (Tauri) + `Sidebar` + `Header` + `Outlet`, палитра команд; **Ctrl+S / ⌘S** → `/export` + toast
- [x] **Header** — кнопка сайдбара, заголовок, **Поиск / ⌘K**; `AppCommandPalette` (`cmdk`); без backend badge
- [x] **TitleBar** — `TitleBar.tsx`: drag-region, свернуть / развернуть / закрыть (`@tauri-apps/api/window`), только при `isTauri()`
- [x] **Toast** — `sonner` + theme sync
- [x] **Sidebar** — узкий режим (иконки + tooltip), состояние в `appStore` + `localStorage`

### Анимации и переходы (Framer Motion)

- [~] **Page transitions** — CSS `page-enter` на смене маршрута (`globals.css`); Framer Motion не подключён
- [~] **Skeleton loading** — базовый `Skeleton` + сетки на режимах/пресетах
- [~] **Button states** — loading spinner; нет scale on press
- [~] **Toast notifications** — Sonner (`bottom-right`, `richColors`); кастомная анимация/позиция опциональна
- [x] **Sidebar collapse** — `transition-[width]` + `w-56` / `w-[3.75rem]`
- [ ] **Slider animation** — smooth value change with spring physics
- [~] **Canvas smooth** — мгновенный пересчёт canvas при смене слайдеров; count-up анимации нет

---

## 🟡 ЖЕЛАТЕЛЬНО — Фаза 3: Функциональность (2–3 недели)

### Формы и валидация

- [~] **React Hook Form** + **Zod** — схема **`greetForm`** и `greet` IPC остаются в коде как образец; на дашборде демо-формы нет — перенос эталона на другие формы — позже

- [ ] **CVAR editor form** — категоризованный список CVAR с:
  - Real-time validation (range check)
  - Live preview изменений в конфиге
  - Undo/Redo для каждого поля

- [ ] **Profile manager form** — создание/редактирование профилей:
  - Имя профиля, описание, теги
  - Выбор режима, пресета, сетевого профиля
  - Сохранение как шаблон для последующего использования

### Асинхронные операции

- [~] **Custom hook `useAsync`** — `hooks/useAsync.ts` (`useAsyncFn`); дашборд использует для **greet**; распространить на остальные IPC
  ```typescript
  const { data, isLoading, error } = useAsync(
    () => invoke('generate_config', { ...params }),
    [params]
  );
  ```

- [ ] **Request deduplication** — не отправлять две одинаковые команды подряд
- [ ] **Timeout handling** — если Tauri command зависает > 5s, показать timeout error
- [ ] **Offline mode** — кэшировать последние данные, работать офлайн с ограничениями

### Таблицы и списки

- [~] **Визуализация diff** — столбчатая диаграмма (Recharts) по числу добавленных/удалённых строк на странице сравнения
- [x] **TanStack Table (React Table)** для сравнения конфигов:
  - Сортировка по столбцам
  - Фильтрация по типу CVAR (эвристика **`cfgLineCategory`**)
  - Пагинация (25–200 строк на страницу); блоки по-прежнему с **виртуализацией** при длинном diff
  - Экспорт в CSV

- [ ] **VirtualList** для больших списков (профили, история):
  - Рендер только видимых элементов
  - Overscan 5 элементов для smooth scrolling

### Горячие клавиши

- [~] **Cmd+K** — навигация + **буфер обмена** (шаблоны CVAR из `cfgClipboardSnippets.ts`) + пункт «Справка»
- [ ] **Cmd+Z / Cmd+Y** — Undo/Redo (Zustand store с history middleware)
- [~] **Cmd+S** — перехват с **toast** («профили в разработке»)
- [x] **Ctrl/⌘+E / +I** — переход на Export / Import (`MainLayout`)
- [x] **F1** — модалка `KeyboardShortcutsDialog`
- [x] **F11** — `setFullscreen` в Tauri; в браузере — подсказка toast
- [~] **F12** — debug overlay: **версия, маршрут, heap, UA** (`DebugOverlay`); расширение (виджеты, таймлайн) — позже

---

## 🟢 БОНУСЫ — Фаза 4: Продвинутые фичи (2 недели)

### Старт Фазы 4 (итерация 1)

- [x] **«Знаете ли вы?»** — каталог советов **`src/lib/didYouKnowTips.ts`** (категории: aim / movement / network / visual / general), карточка на **главной** с кнопкой «Ещё совет»; дальше — расширение до **~50** пунктов.
- [x] **F12 — отладочная панель** — **`DebugOverlay`**: версия приложения, текущий маршрут, Tauri/Web, при наличии — **JS heap** (Chromium), краткий **User-Agent**; повторное **F12** или **Esc** закрывает.
- [~] **Steam / путь к игре** — авто-поиск с **`libraryfolders.vdf`** уже реализован в **`detect_game_installation`** (`src-tauri/.../game_commands.rs`, настройки); отдельные пункты дорожной карты ниже — облако, контекстное меню Windows и т.д.

### Синхронизация и облако

- [ ] **Cloud sync (GitHub Gist API)**:
  - Кнопка «Sync to Cloud» в Settings
  - Personal Access Token вход
  - Автосинхронизация при сохранении профиля (если включено в Settings)
  - Версионирование, rollback старых версий

- [ ] **Community Configs**:
  - Репозиторий на GitHub (`configs-repo`) с JSON API
  - Загрузка чужих конфигов, рейтинг (⭐), фильтры (режим/стиль/язык)
  - Кнопка «Upload My Config» → создание PR или direct push

- [x] **Auto-update данных**:
  - Проверка версии JSON-файлов на GitHub при старте (If-Modified-Since)
  - Скачивание только изменённого (по файлам; 304 не перезаписывает)
  - Backup перед обновлением, откат при ошибке; **Диагностика** — ручной sync / reload с диска; событие `gce-catalog-synced` обновляет каталог в UI

### Встроенные инструменты

- [ ] **Terminal Console** — вкладка с вводом CVAR-команд:
  - Автодополнение (Tab), подсветка синтаксиса
  - История (↑↓), мгновенное применение к конфигу
  - Вывод результата команды (ошибки, успех)

- [ ] **Script Engine** — DSL для сложных алиасов:
  - Условия (if), циклы (for/while), переменные
  - Цепочки действий, delay, wait
  - Визуальный редактор блок-схем или text editor с syntax highlighting

- [ ] **Plugin System**:
  - Папка `plugins/` с `.ts` файлами (Webpack/Vite loader)
  - Каждый плагин = function(api: PluginApi) → {onGenerate, onExport, onImport, customPage}
  - Реестр плагинов в Settings

### Расширенный контент

- [ ] **+10 про-пресетов** — всего 28 (было 18). Новые: XeqtR, ahl, method, zonic, etc.
- [ ] **Фото про-игроков** — 64×64 PNG в assets, отображение в карточке пресета
- [ ] **+5 режимов** — всего 16. Новые: JailBreak, Paintball, BaseBuilder, SuperHero, Knife Arena
- [ ] **Расширенный CVAR словарь** — для каждого CVAR: `pro_range`, `pro_average`, `related_cvars`, `tip_ru`, `tip_en`, `deprecated`
- [~] **50 советов "Did you know?"** — категории в **`didYouKnowTips.ts`**; сейчас **15**, цель — **50**

### Экспорт и интеграция

- [ ] **Markdown / PDF экспорт** — полный отчёт о конфиге с красивым форматированием
- [ ] **Steam integration** — автоматическое определение пути к CS 1.6 через Steam libraryfolders.vdf
- [ ] **Windows Context Menu** — "Generate CS Config" для выбранной папки (shell extension)

---

## 🔵 ИНФРАСТРУКТУРА И ОПТИМИЗАЦИЯ (параллельно)

### Сборка и распределение

- [ ] **Tauri build**:
  - `cargo tauri build` для Windows (MSI installer)
  - `cargo tauri build --target universal-apple-darwin` для macOS (DMG)
  - `cargo tauri build --target x86_64-unknown-linux-gnu` для Linux (AppImage / deb)
  - Code signing и notarization для macOS

- [ ] **Размер оптимизация**:
  - Цель: < 15 MB (Windows MSI) вместо 45 MB (CustomTkinter)
  - Strip Rust symbols, enable LTO в Cargo.toml
  - Remove debug builds, minify CSS/JS

- [ ] **GitHub Actions CI/CD**:
  - Матрица: (Windows, macOS, Linux) × (Python 3.11, 3.12) × (Rust stable, beta)
  - Build, test, lint (ESLint + ruff), upload artifacts
  - Auto-release на GitHub Releases при push tag

- [ ] **Auto-update mechanism** (Tauri updater):
  - Проверка версии на GitHub Releases при старте
  - Загрузка и установка обновления (с уведомлением)
  - Rollback при ошибке

### Тестирование

- [ ] **Unit tests** (Vitest + jsdom):
  - Компоненты React (React Testing Library)
  - Zustand stores
  - Валидаторы (Zod)
  - Утилиты

- [ ] **Integration tests**:
  - API client (mock Tauri commands)
  - End-to-end flows (generate → export → validate)

- [ ] **E2E tests** (Playwright):
  - Основные сценарии пользователя
  - Crosshair editor, export, import

### Код и документация

- [ ] **TypeScript strict mode** — 100% type coverage
- [ ] **ESLint + Prettier** — code formatting и style
- [ ] **JSDoc comments** — для всех публичных функций
- [ ] **API docs** (Rust) — `cargo doc --open` для backend
- [ ] **Wiki на GitHub** — Getting Started, All CVARs, Plugin Development, Troubleshooting

---

## 📊 Метрики успеха v3.0

| Метрика | Было | Цель | Статус |
|---------|------|------|--------|
| Размер .exe (Windows) | 45 MB | < 15 MB | 🔵 |
| Время запуска | ~2.5s | < 1.0s | 🔵 |
| RAM idle | ~120 MB | < 60 MB | 🔵 |
| Дизайн | CustomTkinter (плоский) | Modern Shadcn/ui (glassmorphism) | 🟢 |
| Про-пресеты | 18 | 28 | 🟡 |
| Режимы | 11 | 16 | 🟡 |
| CVAR | ~120 | ~200 | 🟡 |
| Тесты (frontend) | 0 | 100+ | 🟢 |
| Документация | README + CHANGELOG | Wiki + video tutorials | 🟡 |
| Кроссплатформность | Windows только | Windows/macOS/Linux | 🟢 |

---

## 🚀 Рекомендованный путь разработки

1. **Неделя 1–2**: Выделение core логики в Rust, базовая Tauri структура
2. **Неделя 3–5**: Построение UI с Shadcn/ui, основные страницы, миграция функциональности
3. **Неделя 6–7**: Анимации, асинхронные операции, горячие клавиши, оптимизация
4. **Неделя 8–9**: Бонусные фичи, облачная синхронизация, плагины
5. **Неделя 10**: Тестирование, документация, подготовка к выпуску v3.0

**Примерный объём**: 350–400 часов (если работать в паре или solo intensive ~8 недель)

---

## 📚 Нужные зависимости (package.json)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.4.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",
    "framer-motion": "^10.16.0",
    "recharts": "^2.10.0",
    "@tanstack/react-table": "^8.13.0",
    "@radix-ui/primitives": "^1.0.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0",
    "next-themes": "^0.2.1",
    "class-variance-authority": "^0.7.0",
    "cmdk": "^0.2.0",
    "highlight.js": "^11.9.0",
    "@tauri-apps/api": "^2.0.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.3.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "vitest": "^1.0.0",
    "react-testing-library": "^14.1.0",
    "jsdom": "^23.0.0",
    "eslint": "^8.54.0",
    "prettier": "^3.1.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/node": "^20.0.0"
  }
}
```

---

## 🎓 Полезные ресурсы

- **Tauri docs**: https://tauri.app/start/
- **Shadcn/ui**: https://ui.shadcn.com/
- **Tailwind CSS**: https://tailwindcss.com/
- **React Hook Form**: https://react-hook-form.com/
- **Framer Motion**: https://www.framer.com/motion/
- **Recharts**: https://recharts.org/
- **TanStack Table**: https://tanstack.com/table/

---

**Приоритет: 🔴 (фаза 1) → 🟠 (фаза 2) → 🟡 (фаза 3) → 🟢 (фаза 4) → 🔵 (инфра)**

Каждая фаза готовит стабильный, тестируемый код. Релиз v3.0 возможен после фазы 2 (с ограниченным функционалом, но с новым дизайном).
