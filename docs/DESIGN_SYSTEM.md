# Дизайн-система v3 (Tauri UI)

> **Актуально для v3.2.0** (2026-04). Версию приложения см. в `package.json`.

Стек: **Tailwind CSS 4**, **shadcn/ui** (варианты через `class-variance-authority`), **Radix UI** (доступность: диалоги, селекты, скролл и т.д.), токены в **OKLCH** в `src/styles/globals.css`.

Публичные контракты **Rust IPC** и экспортируемых **TS**-модулей не меняются без необходимости; при эволюции UI используются адаптеры и обёртки компонентов.

---

## Палитра (семантические роли)

Цвета задаются в `:root` и `.dark` как CSS-переменные и пробрасываются в `@theme inline` для утилит Tailwind (`bg-background`, `text-primary`, `border-destructive` и т.д.).

| Роль | Назначение |
|------|------------|
| `background` / `foreground` | Базовый фон и текст |
| `primary` / `primary-foreground` | Основной акцент (кнопки, ссылки) |
| `secondary` / `muted` | Вторичные поверхности и подписи |
| `accent` | Hover-подложки, выделение |
| `destructive` | Опасные действия |
| `success` | Успех (генерация, подтверждение) |
| `warning` | Предупреждения |
| `border` / `input` / `ring` | Границы, поля, фокус-кольцо |

Контраст ориентируем на **WCAG 2.1 AA** для основного текста и интерактивных элементов; при сомнении проверяйте пары в инструментах контраста.

---

## Типографика

- **Sans:** `Inter` + системный стек (`--font-sans` в `globals.css`).
- **Mono:** `JetBrains Mono` для кода и бэйджей (`--font-mono`).
- **Базовый размер body:** 14px; заголовки `h1`–`h3` и `--text-display` / `--text-lead` / `--text-caption` для согласованной шкалы.

---

## Сетка и отступы

- Базовая сетка **4px** (классы Tailwind `gap-*`, `p-*`, `space-y-*`).
- Поля основного контента: `padding` задаётся в `MainLayout` на `#main-content` через `--space-page`.
- **Оболочка страницы** (единая ширина и вертикальный ритм): `src/lib/layoutTokens.ts`
  - `pageShellClass` — `max-w-5xl`, колонка для большинства разделов (главная, каталоги, сравнение, импорт…).
  - `pageShellNarrowClass` — `max-w-2xl`, узкая колонка для мастера, диагностики, настроек.
  - `pageLeadClass` — вводный абзац под шапкой (`text-sm` + `leading-relaxed` + `text-muted-foreground`).
  - `pageSectionTitleClass` — заголовок секции внутри контента (uppercase, мелкий кегль).
  - `pageSectionGroupTitleClass` — заголовок группы контента крупнее (например команда в списке пресетов).
  - `pageOverlineClass` — строка над метрикой или полем (uppercase, без жирного).
  - `pageCaptionClass` — подписи в карточках и вторичные пояснения (`text-xs` + `leading-relaxed` + `text-muted-foreground`).
- Карточки: `--space-card` в `:root`; сетка каталога — константа `CATALOG_GRID`.

---

## Состояния компонентов

| Состояние | Поведение |
|-----------|-----------|
| **hover** | Утилиты `hover:*` (фон, граница, `scale` с `motion-safe:`) |
| **active** | `active:scale-*` где уместно |
| **focus** | `focus-visible:ring-2 focus-visible:ring-ring` и смещение кольца |
| **disabled** | `disabled:opacity-50 disabled:pointer-events-none` |
| **loading** | Кнопка: `loading` + спиннер; `aria-busy`, `data-loading` |
| **error** | Поля: `aria-invalid`, сообщения через `FormMessage` / подписи |

Глобально: **`prefers-reduced-motion`** и атрибут `data-reduced-motion` отключают лишние анимации (см. `globals.css`).

---

## Тема

- Класс **`.dark`** на корневом элементе переключает тёмную схему.
- **Первый визит** (нет значения в `localStorage`): тема берётся из **`prefers-color-scheme`** (`readTheme` в `src/lib/appPrefs.ts`).
- После явного выбора в настройках значение сохраняется и имеет приоритет.

---

## Производительность

- Длинные списки и diff: виртуализация где уже внедрена (`@tanstack/react-virtual`).
- Тяжёлые карточки списков: `React.memo` (например `CatalogItemCard`).
- Мемоизация хуков — по месту, без преждевременной оптимизации всего дерева.

---

## Ссылки по коду

| Область | Файлы |
|---------|--------|
| Токены и базовые стили | `src/styles/globals.css` |
| Тема / локаль / motion | `src/lib/appPrefs.ts`, `src/themeBootstrap.ts` |
| Кнопка, инпуты | `src/components/ui/button.tsx`, `input.tsx`, … |
| Карточки | `src/components/ui/card.tsx` — `CardDescription` по умолчанию с **`leading-relaxed`** |
| Сайдбар | `src/components/layout/Sidebar.tsx` — токены **`sidebarNavGroupLabelClass`**, **`sidebarStatusOverlineClass`**, **`sidebarBrandMetaClass`**, **`sidebarRecentNameClass`** |
| Заполненность конфига (главная) | `src/lib/configCompleteness.ts`, `DashboardConfigCompletenessCard.tsx` |

Историческая палитра v2 (CustomTkinter): `archive/v2-python-customtkinter/cfg_generator/theme.py`.
