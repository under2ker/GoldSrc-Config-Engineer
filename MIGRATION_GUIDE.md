# Руководство миграции: CustomTkinter → Tauri 2 + React 18

> **См. также:** [QUICK_START.md](QUICK_START.md) · [checklist.md](checklist.md) · [ADDITIONAL_IDEAS.md](ADDITIONAL_IDEAS.md)  
> Детальный пошаговый чеклист задач — в **checklist.md**; идеи «сверх плана» — в **ADDITIONAL_IDEAS.md**.

## 📌 Оглавление
1. [Сравнение фреймворков](#сравнение-фреймворков)
2. [Почему Tauri + React](#почему-tauri--react)
3. [Архитектура приложения](#архитектура-приложения)
4. [Выбор библиотек](#выбор-библиотек)
5. [План миграции](#план-миграции)
6. [Примеры кода](#примеры-кода)

---

## Сравнение фреймворков

### 1. **Tauri 2 + React** ⭐ РЕКОМЕНДУЕТСЯ

| Параметр | Оценка | Детали |
|----------|--------|--------|
| **Размер бинарника** | ⭐⭐⭐⭐⭐ | 8–15 MB (vs CustomTkinter 45 MB) |
| **Скорость запуска** | ⭐⭐⭐⭐⭐ | < 1.0s (vs CustomTkinter ~2.5s) |
| **Потребление памяти** | ⭐⭐⭐⭐⭐ | 40–70 MB idle (vs 120 MB) |
| **Визуальное качество** | ⭐⭐⭐⭐⭐ | Native OS controls, современный дизайн |
| **Производительность UI** | ⭐⭐⭐⭐⭐ | 60 FPS animations, smooth transitions |
| **Кроссплатформенность** | ⭐⭐⭐⭐⭐ | Windows / macOS / Linux (одним кодом) |
| **Экосистема** | ⭐⭐⭐⭐⭐ | React, npm packages, огромное сообщество |
| **Type Safety** | ⭐⭐⭐⭐⭐ | TypeScript + Zod |
| **Кривая обучения** | ⭐⭐⭐ | Есть что учить, но знаешь React |
| **Документация** | ⭐⭐⭐⭐ | Хорошая, растущая |

**Подходит для**: Профессионального приложения с современным дизайном

---

### 2. PyQt6 / PySide6

| Параметр | Оценка | Детали |
|----------|--------|--------|
| **Размер бинарника** | ⭐⭐⭐ | 60–80 MB (vs CustomTkinter 45 MB, но функциональнее) |
| **Скорость запуска** | ⭐⭐⭐ | 1.5–2.0s |
| **Потребление памяти** | ⭐⭐ | 150–200 MB idle |
| **Визуальное качество** | ⭐⭐⭐⭐ | Native платформенные стили, профессиональный вид |
| **Производительность UI** | ⭐⭐⭐⭐ | 60 FPS, но требует оптимизации |
| **Кроссплатформенность** | ⭐⭐⭐⭐ | Windows / macOS / Linux хорошо |
| **Экосистема** | ⭐⭐⭐ | Небольшой мир Python-GUI |
| **Type Safety** | ⭐⭐ | Типизация слабая, нужны type stubs |
| **Кривая обучения** | ⭐⭐⭐⭐ | Сложнее чем CustomTkinter, много boilerplate |
| **Документация** | ⭐⭐⭐⭐ | Хорошая (но не как для web) |

**Подходит для**: Если нужен Pure Python (не хочешь JavaScript)

---

### 3. Electron + React

| Параметр | Оценка | Детали |
|----------|--------|--------|
| **Размер бинарника** | ⭐ | 150–200 MB |
| **Скорость запуска** | ⭐⭐ | 3–5s (Chromium медленнее) |
| **Потребление памяти** | ⭐ | 300–400 MB idle |
| **Визуальное качество** | ⭐⭐⭐⭐⭐ | Идеальный дизайн, любая CSS |
| **Производительность UI** | ⭐⭐⭐⭐⭐ | Отличная (Chromium engine) |
| **Кроссплатформенность** | ⭐⭐⭐⭐⭐ | Windows / macOS / Linux идеально |
| **Экосистема** | ⭐⭐⭐⭐⭐ | npm packages, React, огромное сообщество |
| **Type Safety** | ⭐⭐⭐⭐⭐ | TypeScript + React |
| **Кривая обучения** | ⭐⭐ | Легче всего (знаешь React) |
| **Документация** | ⭐⭐⭐⭐⭐ | Отличная |

**Подходит для**: Если размер и память не критичны

---

### 4. Dear ImGui (C++ / Rust)

| Параметр | Оценка | Детали |
|----------|--------|--------|
| **Размер бинарника** | ⭐⭐⭐⭐⭐ | < 5 MB |
| **Скорость запуска** | ⭐⭐⭐⭐⭐ | < 500ms |
| **Потребление памяти** | ⭐⭐⭐⭐ | 10–20 MB idle |
| **Визуальное качество** | ⭐⭐ | Утилитарный, игровой стиль |
| **Производительность UI** | ⭐⭐⭐⭐⭐ | 120+ FPS (не нужно) |
| **Кроссплатформенность** | ⭐⭐⭐⭐ | Windows / macOS / Linux с поддержкой |
| **Экосистема** | ⭐⭐ | Маленькая, специалистов мало |
| **Type Safety** | ⭐⭐⭐⭐ | Rust type safety |
| **Кривая обучения** | ⭐ | Очень крутая (C++/Rust + ImGui парадигма) |
| **Документация** | ⭐⭐⭐ | Есть, но мало tutorials |

**Подходит для**: Инструментов, если нужен минимальный footprint

---

## 🏆 Вывод: Tauri 2 + React

**Для CS 1.6 Config Engineer рекомендуется именно этот стек**, потому что:

1. ✅ Знаешь React (как в DevFlow)
2. ✅ Современный, профессиональный дизайн (Shadcn/ui + Tailwind)
3. ✅ Оптимальный размер (8–15 MB vs 45–150 MB)
4. ✅ Кроссплатформенность в одном коде
5. ✅ Асинхронность и state management (Zustand + React Hooks)
6. ✅ Огромная экосистема npm (animations, forms, charts, tables)
7. ✅ Type-safe (TypeScript + Zod)
8. ✅ Легко масштабировать и добавлять новые фичи

---

## Архитектура приложения

### Структура проекта

```
goldsr-config-engineer/
│
├── src-tauri/                          # Rust backend (Tauri)
│   ├── src/
│   │   ├── main.rs                     # Точка входа, инициализация окна
│   │   ├── lib.rs                      # Public API
│   │   ├── commands/
│   │   │   ├── mod.rs
│   │   │   ├── config.rs               # generate_config, validate, etc.
│   │   │   ├── profile.rs              # save/load/delete profiles
│   │   │   ├── game.rs                 # game path, deploy
│   │   │   ├── export.rs               # export single/modular
│   │   │   └── import.rs               # import with validation
│   │   ├── models/
│   │   │   ├── mod.rs
│   │   │   ├── config.rs               # CfgConfig struct
│   │   │   ├── profile.rs              # Profile struct
│   │   │   └── error.rs                # ApiError type
│   │   ├── services/
│   │   │   ├── mod.rs
│   │   │   ├── generator.rs            # Config generation logic
│   │   │   ├── validator.rs            # CVAR validation
│   │   │   ├── exporter.rs             # Export to .cfg
│   │   │   ├── importer.rs             # Import with security
│   │   │   └── database.rs             # SQLite operations
│   │   ├── data/
│   │   │   ├── mod.rs
│   │   │   ├── cvars.rs                # CVAR definitions (or JSON)
│   │   │   ├── modes.rs                # Game modes
│   │   │   └── presets.rs              # Pro presets
│   │   └── utils/
│   │       ├── mod.rs
│   │       └── security.rs             # Input validation
│   ├── Cargo.toml
│   └── tauri.conf.json                 # Tauri configuration
│
├── src/                                # React frontend (TypeScript)
│   ├── components/
│   │   ├── ui/                         # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── slider.tsx
│   │   │   ├── card.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── command.tsx             # Command palette
│   │   │   ├── context-menu.tsx
│   │   │   ├── scroll-area.tsx
│   │   │   ├── tooltip.tsx
│   │   │   ├── badge.tsx
│   │   │   └── [более 20 компонентов]
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx             # Боковая навигация
│   │   │   ├── Header.tsx              # Топ-панель с поиском
│   │   │   ├── Toaster.tsx             # Toast контейнер
│   │   │   ├── Titlebar.tsx            # Кастомный titlebar
│   │   │   └── MainLayout.tsx          # Layout обёртка
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx       # Главная
│   │   │   ├── QuickSetupPage.tsx      # Быстрая настройка
│   │   │   ├── GameModesPage.tsx       # Режимы
│   │   │   ├── PresetsPage.tsx         # Пресеты
│   │   │   ├── CrosshairPage.tsx       # Редактор прицела
│   │   │   ├── ComparisonPage.tsx      # Сравнение
│   │   │   ├── ExportPage.tsx          # Экспорт
│   │   │   ├── ImportPage.tsx          # Импорт
│   │   │   ├── PreviewPage.tsx         # Preview конфига
│   │   │   ├── DiagnosticsPage.tsx     # Диагностика
│   │   │   ├── ProfilesPage.tsx        # Профили
│   │   │   ├── HistoryPage.tsx         # История
│   │   │   ├── SettingsPage.tsx        # Настройки
│   │   │   └── HelpPage.tsx            # Справка (F1)
│   │   └── common/
│   │       ├── SkeletonScreen.tsx      # Skeleton loader
│   │       ├── RadarChart.tsx          # Recharts radar
│   │       ├── CrosshairCanvas.tsx     # Canvas для прицела
│   │       ├── VirtualTable.tsx        # TanStack table
│   │       ├── SearchPalette.tsx       # Cmd+K палитра
│   │       ├── SyntaxHighlighter.tsx   # Подсветка синтаксиса
│   │       └── [другие полезные]
│   ├── stores/
│   │   ├── index.ts
│   │   ├── configStore.ts              # Zustand: текущий конфиг
│   │   ├── profileStore.ts             # Zustand: профили, история
│   │   ├── appStore.ts                 # Zustand: язык, тема, etc.
│   │   └── middleware/
│   │       ├── persist.ts              # Persistence middleware
│   │       └── history.ts              # History/Undo middleware
│   ├── types/
│   │   ├── index.ts
│   │   ├── api.ts                      # API response types
│   │   ├── domain.ts                   # Domain models (Config, Profile, etc.)
│   │   └── schema.ts                   # Zod schemas for validation
│   ├── lib/
│   │   ├── api-client.ts               # Tauri invoke wrapper
│   │   ├── validators.ts               # Zod validation schemas
│   │   ├── utils.ts                    # Утилиты
│   │   └── hooks.ts                    # Custom hooks
│   ├── hooks/
│   │   ├── useConfig.ts                # Hook для конфига
│   │   ├── useProfiles.ts              # Hook для профилей
│   │   ├── useAsync.ts                 # Hook для async операций
│   │   ├── useHotkeys.ts               # Hook для горячих клавиш
│   │   └── [другие hooks]
│   ├── styles/
│   │   ├── globals.css                 # Глобальные стили
│   │   ├── animations.css              # Framer Motion + CSS анимации
│   │   └── theme.css                   # CSS переменные (темы)
│   ├── App.tsx                         # Главный компонент
│   ├── main.tsx                        # React mount point
│   └── index.css                       # Tailwind import
│
├── public/
│   ├── favicon.ico
│   ├── icons/                          # Иконки для различных платформ
│   └── assets/
│       ├── players/                    # Фото про-игроков
│       ├── fonts/                      # Кастомные шрифты
│       └── data/                       # JSON: cvars, modes, presets (если не в Rust)
│
├── tests/
│   ├── unit/
│   │   ├── stores.test.ts
│   │   ├── hooks.test.ts
│   │   └── utils.test.ts
│   └── e2e/
│       ├── config-generation.spec.ts
│       ├── export.spec.ts
│       └── crosshair-editor.spec.ts
│
├── .github/workflows/
│   ├── ci.yml                          # Lint + tests
│   ├── build.yml                       # Build для Windows/macOS/Linux
│   └── release.yml                     # Publish на GitHub Releases
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── vite.config.ts
├── vitest.config.ts
├── eslint.config.js
├── prettier.config.js
└── README.md
```

---

## Выбор библиотек

### UI Framework & Design System

#### ✅ **Shadcn/ui + Tailwind CSS**

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npx shadcn-ui@latest init
```

**Почему Shadcn/ui?**
- Базируется на Radix UI (accessibility, no JS deps)
- 100% кастомизация (all code in your repo)
- Tailwind для styling (no CSS conflicts)
- Копируй-вставляй компоненты (не node_modules)
- Идеален для быстрого прототипирования

**Кастомизация (`tailwind.config.ts`)**:
```typescript
export default {
  theme: {
    extend: {
      colors: {
        // Твоя палитра
        'midnight': '#0D1117',
        'sidebar': '#161B22',
        'card': '#1C2333',
        'accent': '#1F6FEB',
        'success': '#2EA043',
        'warning': '#D29922',
        'error': '#F85149',
      },
      fontFamily: {
        'sans': ['Segoe UI', 'system-ui'],
        'mono': ['Consolas', 'monospace'],
      },
      animation: {
        'shimmer': 'shimmer 2s infinite',
      },
    },
  },
};
```

---

### State Management

#### ✅ **Zustand**

```typescript
// src/stores/configStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface ConfigState {
  currentConfig: Config | null;
  mode: GameMode;
  preset: ProPreset;
  
  // Actions
  generateConfig: (mode: GameMode, preset: ProPreset) => Promise<void>;
  updateCvar: (key: string, value: any) => void;
  resetConfig: () => void;
}

export const useConfigStore = create<ConfigState>()(
  devtools(
    persist(
      (set, get) => ({
        currentConfig: null,
        mode: 'classic',
        preset: 'f0rest',
        
        generateConfig: async (mode, preset) => {
          const config = await invoke('generate_config', { mode, preset });
          set({ currentConfig: config });
        },
        
        updateCvar: (key, value) => {
          set(state => ({
            currentConfig: {
              ...state.currentConfig,
              settings: {
                ...state.currentConfig?.settings,
                [key]: value,
              },
            },
          }));
        },
        
        resetConfig: () => set({ currentConfig: null }),
      }),
      {
        name: 'config-storage',
      }
    )
  )
);
```

**Почему Zustand?**
- Минимальный boilerplate (vs Redux)
- Встроенные middleware (persist, devtools)
- TypeScript-первый
- Знаешь из DevFlow
- < 2KB gzipped

---

### Forms & Validation

#### ✅ **React Hook Form + Zod**

```typescript
// src/lib/validators.ts
import { z } from 'zod';

export const ConfigSchema = z.object({
  sensitivity: z.number().min(0.1).max(20),
  fps_max: z.number().min(30).max(1000),
  rate: z.number().min(2500).max(30000),
  cl_cmdrate: z.number().min(10).max(128),
  cl_updaterate: z.number().min(10).max(128),
  volume: z.number().min(0).max(1),
  cl_lc: z.boolean(),
  cl_lw: z.boolean(),
});

export type ConfigInput = z.infer<typeof ConfigSchema>;
```

```typescript
// src/components/pages/QuickSetupPage.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ConfigSchema, ConfigInput } from '@/lib/validators';

export function QuickSetupPage() {
  const { control, handleSubmit, formState: { errors } } = useForm<ConfigInput>({
    resolver: zodResolver(ConfigSchema),
    defaultValues: {
      sensitivity: 2.0,
      fps_max: 144,
      rate: 30000,
    },
  });

  return (
    <form onSubmit={handleSubmit(async (data) => {
      await invoke('generate_config', data);
    })}>
      {/* Form fields */}
    </form>
  );
}
```

**Почему React Hook Form + Zod?**
- Минимальные re-renders (form library)
- Встроенная валидация (Zod)
- Type-safe (TypeScript inference)
- Лучше производительность vs Formik

---

### Animations

#### ✅ **Framer Motion**

```typescript
// src/components/pages/QuickSetupPage.tsx
import { motion } from 'framer-motion';

export function QuickSetupPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.15, ease: 'easeOut' }}
    >
      {/* Page content */}
    </motion.div>
  );
}
```

**Почему Framer Motion?**
- Spring physics для естественных движений
- Layout animations (shared layout)
- Gesture support (drag, pan)
- Хорошая документация

---

### Charts & Data Visualization

#### ✅ **Recharts** (для сравнения конфигов)

```typescript
// src/components/common/RadarChart.tsx
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts';

export function ConfigRadarChart({ yourConfig, proPreset }) {
  const data = [
    { category: 'Aim', you: 75, pro: 85 },
    { category: 'Network', you: 60, pro: 90 },
    { category: 'Visuals', you: 70, pro: 75 },
    { category: 'Audio', you: 65, pro: 80 },
    { category: 'Movement', you: 80, pro: 85 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid stroke="var(--border)" />
        <PolarAngleAxis dataKey="category" />
        <Radar name="Your Config" dataKey="you" stroke="var(--accent)" />
        <Radar name="Pro Preset" dataKey="pro" stroke="var(--success)" />
      </RadarChart>
    </ResponsiveContainer>
  );
}
```

**Почему Recharts?**
- React-ориентированная
- Responsive
- Легко кастомизировать с Tailwind
- Хорошо интегрируется с TypeScript

#### Альтернатива: **Chart.js**
Если нужна большая функциональность, но тяжелее (~30KB gzipped vs Recharts ~15KB).

---

### Tables (для сравнения конфигов)

#### ✅ **TanStack Table (React Table)**

```typescript
// src/components/common/ComparisonTable.tsx
import { useReactTable, createColumnHelper } from '@tanstack/react-table';

interface ComparisonRow {
  cvar: string;
  yourValue: string;
  proValue: string;
  difference: string;
}

const columnHelper = createColumnHelper<ComparisonRow>();

const columns = [
  columnHelper.accessor('cvar', {
    header: 'CVAR',
    cell: info => <code className="font-mono">{info.getValue()}</code>,
  }),
  columnHelper.accessor('yourValue', {
    header: 'Your Config',
    cell: info => <span className="text-blue-500">{info.getValue()}</span>,
  }),
  columnHelper.accessor('proValue', {
    header: 'Pro Preset',
    cell: info => <span className="text-green-500">{info.getValue()}</span>,
  }),
  columnHelper.accessor('difference', {
    header: 'Difference',
    cell: info => <Badge variant={info.getValue() === 'Same' ? 'default' : 'destructive'}>{info.getValue()}</Badge>,
  }),
];

export function ComparisonTable({ data }: { data: ComparisonRow[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => (
                <th key={header.id} className="p-2 text-left border-b">
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map(row => (
            <tr key={row.id} className="hover:bg-card/50">
              {row.getVisibleCells().map(cell => (
                <td key={cell.id} className="p-2 border-b">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**Почему TanStack Table?**
- Headless (полный контроль над UI)
- Виртуализация (для больших данных)
- Сортировка, фильтрация, пагинация встроены
- Zero dependencies (кроме React)

---

### Syntax Highlighting (для Preview)

#### ✅ **highlight.js** или **Prismjs**

```typescript
// src/components/common/SyntaxHighlighter.tsx
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';

export function ConfigHighlighter({ code }: { code: string }) {
  const highlighted = hljs.highlight(code, { language: 'bash' }).value;

  return (
    <pre className="bg-card p-4 rounded-lg overflow-x-auto">
      <code dangerouslySetInnerHTML={{ __html: highlighted }} className="text-sm" />
    </pre>
  );
}
```

**Почему highlight.js?**
- Легко встраивается
- Хорошая поддержка конфиг-синтаксиса
- Маленький footprint (можно выбрать языки)

---

### Keyboard Shortcuts

#### ✅ **cmdk** (Command Palette)

```typescript
// src/components/common/SearchPalette.tsx
import { Command } from 'cmdk';

export function SearchPalette() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen(!open);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="p-0 shadow-md">
        <Command>
          <CommandInput placeholder="Search CVARs, modes, presets..." />
          <CommandList>
            <CommandGroup heading="Modes">
              <CommandItem onSelect={() => handleSelectMode('classic')}>
                Classic (5v5)
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </Command>
      </DialogContent>
    </Dialog>
  );
}
```

**Почему cmdk?**
- Встроено в shadcn/ui
- Fuzzy search
- Keyboard navigation
- Категоризация результатов

---

### API Communication

#### ✅ **Tauri `invoke` + wrapper**

```typescript
// src/lib/api-client.ts
import { invoke } from '@tauri-apps/api/tauri';
import { ConfigSchema, type ConfigInput } from './validators';
import type { Config, Profile } from '@/types/domain';

export const api = {
  config: {
    generate: async (params: ConfigInput): Promise<Config> => {
      const result = await invoke('generate_config', params);
      return ConfigSchema.parse(result);
    },
    
    validate: async (config: Config): Promise<{ score: number; issues: string[] }> => {
      return invoke('validate_config', { config });
    },
    
    exportSingle: async (config: Config, path: string): Promise<void> => {
      return invoke('export_single', { config, path });
    },
  },

  profile: {
    list: async (): Promise<Profile[]> => {
      return invoke('list_profiles');
    },
    
    save: async (profile: Profile): Promise<void> => {
      return invoke('save_profile', { profile });
    },
    
    load: async (id: string): Promise<Profile> => {
      return invoke('load_profile', { id });
    },
  },
};
```

**Почему wrapper?**
- Type-safe (TypeScript inference)
- Валидация ответов (Zod)
- Единая точка для error handling
- Легко тестировать (mock api)

---

## План миграции

### Фаза 1: Setup & Core (2–3 недели)

#### Неделя 1
- [ ] Создать Tauri проект: `cargo tauri init`
- [ ] Настроить TypeScript, Vite, Tailwind CSS
- [ ] Установить все зависимости
- [ ] Инициализировать shadcn/ui: `npx shadcn-ui@latest init`
- [ ] Настроить GitHub Actions CI/CD

#### Неделя 2
- [ ] Выделить core логику из Python в Rust (generator.rs, validator.rs, exporter.rs)
- [ ] Реализовать SQLite database layer (profiles, history)
- [ ] Написать Tauri commands (config, profile, game commands)
- [ ] Создать TypeScript types и API client

#### Неделя 3
- [ ] Создать базовую Tauri структуру (Sidebar, MainLayout, Titlebar)
- [ ] Реализовать Zustand stores (configStore, profileStore, appStore)
- [ ] Написать custom hooks (useConfig, useProfiles, useAsync)
- [ ] Настроить горячие клавиши (useHotkeys hook, cmdk palette)

---

### Фаза 2: Pages & UI (3–4 недели)

#### Неделя 4–5
- [ ] Dashboard Page (быстрые действия, статистика)
- [ ] Quick Setup Page (шаблоны, режимы, сжатые настройки)
- [ ] Game Modes Page (сетка режимов)
- [ ] Pro Presets Page (сетка пресетов с фото)

#### Неделя 6–7
- [ ] Crosshair Editor Page (Canvas + слайдеры + Framer Motion)
- [ ] Comparison Page (Radar Chart + TanStack Table)
- [ ] Export Page (выбор формата, очистка)
- [ ] Import Page (drag-and-drop, URL loader)

#### Неделя 8
- [ ] Preview Page (код с подсветкой синтаксиса)
- [ ] Diagnostics Page (чеклист проверок, Fix buttons)
- [ ] Profiles & History Page (список, откат)
- [ ] Settings Page (язык, тема, горячие клавиши)

---

### Фаза 3: Polish & Optimization (2 недели)

#### Неделя 9
- [ ] Добавить animations (Framer Motion page transitions, button states, skeleton loading)
- [ ] Оптимизировать рендер (мемоизация, lazy loading)
- [ ] Написать unit tests (Vitest + React Testing Library)
- [ ] Настроить error handling и loading states

#### Неделя 10
- [ ] Написать E2E tests (Playwright)
- [ ] Оптимизировать размер бинарника (< 15 MB)
- [ ] Подготовить документацию и дорожную карту для релиза
- [ ] Тестирование на Windows/macOS/Linux

---

## Примеры кода

### Пример 1: Custom Hook для конфига

```typescript
// src/hooks/useConfig.ts
import { useConfigStore } from '@/stores/configStore';
import { api } from '@/lib/api-client';
import { useState, useCallback } from 'react';

export function useConfig() {
  const { currentConfig, generateConfig, updateCvar } = useConfigStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = useCallback(async (mode: GameMode, preset: ProPreset) => {
    setIsLoading(true);
    setError(null);
    try {
      await generateConfig(mode, preset);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [generateConfig]);

  const validate = useCallback(async () => {
    if (!currentConfig) return;
    try {
      return await api.config.validate(currentConfig);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Validation failed');
    }
  }, [currentConfig]);

  return { currentConfig, generate, updateCvar, validate, isLoading, error };
}
```

### Пример 2: Компонент страницы (Crosshair Editor)

```typescript
// src/components/pages/CrosshairEditorPage.tsx
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { CrosshairCanvas } from '@/components/common/CrosshairCanvas';
import { useConfig } from '@/hooks/useConfig';

export function CrosshairEditorPage() {
  const { currentConfig, updateCvar } = useConfig();
  const [zoom, setZoom] = useState(1);
  const [thickness, setThickness] = useState(1);
  const [gap, setGap] = useState(0);
  const [length, setLength] = useState(10);

  const handleExportPNG = async () => {
    // Экспорт PNG через canvas.toDataURL()
  };

  const handleSideBySide = () => {
    // Открыть modal с двумя Canvas'ами
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-3 gap-6">
        {/* Canvas */}
        <Card className="col-span-2 p-6">
          <h3 className="font-semibold mb-4">Live Preview</h3>
          <CrosshairCanvas
            zoom={zoom}
            thickness={thickness}
            gap={gap}
            length={length}
          />
        </Card>

        {/* Sliders */}
        <Card className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Zoom</label>
            <Slider
              value={[zoom]}
              onValueChange={([v]) => setZoom(v)}
              min={0.5}
              max={3}
              step={0.1}
            />
          </div>
          {/* More sliders... */}
        </Card>
      </div>

      <div className="flex gap-2">
        <Button onClick={handleExportPNG}>📷 Export PNG</Button>
        <Button variant="outline" onClick={handleSideBySide}>↔ Side-by-Side</Button>
      </div>
    </motion.div>
  );
}
```

### Пример 3: Zustand Store с Persist

```typescript
// src/stores/profileStore.ts
import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';
import { api } from '@/lib/api-client';
import type { Profile } from '@/types/domain';

interface ProfileState {
  profiles: Profile[];
  history: Array<{ id: string; timestamp: number; config: any }>;
  selectedProfileId: string | null;

  // Actions
  loadProfiles: () => Promise<void>;
  saveProfile: (profile: Profile) => Promise<void>;
  deleteProfile: (id: string) => Promise<void>;
  selectProfile: (id: string) => void;
  addToHistory: (config: any) => void;
  undoToHistory: (index: number) => Promise<void>;
}

export const useProfileStore = create<ProfileState>()(
  devtools(
    persist(
      (set, get) => ({
        profiles: [],
        history: [],
        selectedProfileId: null,

        loadProfiles: async () => {
          const profiles = await api.profile.list();
          set({ profiles });
        },

        saveProfile: async (profile: Profile) => {
          await api.profile.save(profile);
          set(state => ({
            profiles: state.profiles.some(p => p.id === profile.id)
              ? state.profiles.map(p => p.id === profile.id ? profile : p)
              : [...state.profiles, profile],
          }));
        },

        deleteProfile: async (id: string) => {
          await api.profile.delete(id);
          set(state => ({
            profiles: state.profiles.filter(p => p.id !== id),
          }));
        },

        selectProfile: (id: string) => set({ selectedProfileId: id }),

        addToHistory: (config: any) => {
          set(state => ({
            history: [
              ...state.history,
              { id: `hist-${Date.now()}`, timestamp: Date.now(), config },
            ].slice(-50), // Keep last 50
          }));
        },

        undoToHistory: async (index: number) => {
          const historyItem = get().history[index];
          if (historyItem) {
            const profile = { ...get().profiles[0], ...historyItem.config };
            await get().saveProfile(profile);
          }
        },
      }),
      {
        name: 'profile-storage',
      }
    )
  )
);
```

---

## 🎯 Итоговая рекомендация

| Выбор | Таури + React |
|-------|---|
| **UI Framework** | Shadcn/ui + Tailwind CSS |
| **State** | Zustand + Persist middleware |
| **Forms** | React Hook Form + Zod |
| **Animations** | Framer Motion |
| **Charts** | Recharts (сравнение) |
| **Tables** | TanStack Table |
| **Syntax** | highlight.js |
| **Hotkeys** | cmdk + useHotkeys |
| **API** | Tauri invoke + typed wrapper |
| **Database** | SQLite + sqlx (Rust) |
| **Testing** | Vitest + Playwright |
| **CI/CD** | GitHub Actions |

---

**Полный стек готов, можешь начинать разработку! 🚀**
