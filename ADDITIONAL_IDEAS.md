# Дополнительные идеи и улучшения для v3.0+

> **См. также:** [QUICK_START.md](QUICK_START.md) · [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) · [checklist.md](checklist.md)  
> Этот файл — **не** обязательный объём релиза: бонусы, UX-эксперименты и контент после базовой миграции на Tauri/React.

## 🎨 UI/UX Идеи

### 1. Glassmorphism дизайн (тренд 2024–2025)

Вместо стандартного flat design, использовать **glassmorphism** (полупрозрачные панели с размытием):

```css
/* tailwind.config.ts */
backdropBlur: {
  'glass': '10px',
}

.glass-card {
  @apply bg-white/10 dark:bg-black/20 backdrop-blur-glass border border-white/20;
}
```

**Преимущества**:
- Современный визуальный стиль
- Отличает CS 1.6 Config Engineer от скучных утилит
- Идеален для полупрозрачных overlays (modals, tooltips, notifications)
- Хорошо смотрится в тёмной теме (midnight)

**Места для glassmorphism**:
- Card компоненты для режимов и пресетов
- Modal диалоги (import, export, settings)
- Tooltip-ы и popover-ы
- Search palette background

---

### 2. Динамический фон с частицами (Canvas)

Добавить subtle animated particle effects в фон (особенно в Sidebar):

```typescript
// src/components/layout/ParticleBackground.tsx
import { useEffect, useRef } from 'react';

export function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Создать ~20 частиц, которые медленно движутся
    // Скорость: очень медленная (~1px/frame)
    // Opacity: 0.1–0.3 (не отвлекает)
    // Цвет: accent цвет приложения

    // Частицы связаны между собой линиями (сеть) на расстоянии 100px
    // При наведении курсора на частицу — она ярче светит

    const animate = () => {
      // Clear canvas
      ctx.fillStyle = 'transparent';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Draw particles and connections
      // requestAnimationFrame(animate)
    };

    animate();
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none opacity-20"
    />
  );
}
```

**Где использовать**: Sidebar, Dashboard фон

**Примеры**:
- https://github.com/Vimeo/player-js (particles)
- Вдохновение: https://particles.js.org/

---

### 3. Кастомный куро Titlebar с анимацией

Вместо стандартного Windows titlebar, использовать собственный (как в Figma, VS Code, Slack):

```typescript
// src/components/layout/Titlebar.tsx
import { appWindow } from '@tauri-apps/api/window';
import { motion } from 'framer-motion';

export function Titlebar() {
  const [isMaximized, setIsMaximized] = useState(false);

  return (
    <motion.div
      className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-sidebar to-card border-b border-white/5 drag"
      initial={{ y: -50 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      {/* Logo + App Title */}
      <div className="flex items-center gap-2 select-none">
        <div className="w-6 h-6 rounded-md bg-gradient-to-br from-accent to-blue-600 flex items-center justify-center">
          ⚙️
        </div>
        <span className="font-semibold text-sm">GoldSrc Config Engineer</span>
      </div>

      {/* Center: Search + Notifications */}
      <SearchPalette />

      {/* Right: Window Controls */}
      <div className="flex items-center gap-1">
        <button
          onClick={() => appWindow.minimize()}
          className="p-1 hover:bg-white/10 rounded"
        >
          −
        </button>
        <button
          onClick={() => {
            appWindow.isMaximized().then(setIsMaximized);
            appWindow.toggleMaximize();
          }}
          className="p-1 hover:bg-white/10 rounded"
        >
          {isMaximized ? '❒' : '□'}
        </button>
        <button
          onClick={() => appWindow.close()}
          className="p-1 hover:bg-red-500/20 rounded text-red-400"
        >
          ✕
        </button>
      </div>
    </motion.div>
  );
}
```

**Преимущества**:
- Контроль над внешним видом
- Интеграция поиска в titlebar (экономия места)
- Кастомная анимация
- Лучше выглядит на macOS (нет красного/жёлтого/зелёного)

---

### 4. Сбокного меню (Context Menu)

Добавить контекстное меню (ПКМ) на основные элементы:

```typescript
// src/components/common/ContextMenu.tsx
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
} from '@/components/ui/context-menu';

// На слайдерах CVAR
<ContextMenu>
  <ContextMenuTrigger asChild>
    <Slider {...} />
  </ContextMenuTrigger>
  <ContextMenuContent>
    <ContextMenuItem onClick={resetToDefault}>
      ↻ Reset to Default
    </ContextMenuItem>
    <ContextMenuItem onClick={copyCvar}>
      📋 Copy Value
    </ContextMenuItem>
    <ContextMenuItem onClick={pasteCvar}>
      📌 Paste Value
    </ContextMenuItem>
  </ContextMenuContent>
</ContextMenu>

// На карточках пресетов
<ContextMenu>
  <ContextMenuTrigger asChild>
    <Card {...} />
  </ContextMenuTrigger>
  <ContextMenuContent>
    <ContextMenuItem onClick={loadPreset}>
      ⚙️ Load Preset
    </ContextMenuItem>
    <ContextMenuItem onClick={duplicatePreset}>
      📋 Duplicate
    </ContextMenuItem>
    <ContextMenuItem onClick={deletePreset}>
      🗑️ Delete
    </ContextMenuItem>
  </ContextMenuContent>
</ContextMenu>
```

---

### 5. Breadcrumbs навигация

Добавить breadcrumbs под заголовком каждой страницы для быстрой навигации:

```typescript
// src/components/common/Breadcrumbs.tsx
import { ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export function Breadcrumbs({ items }: { items: { label: string; href: string }[] }) {
  return (
    <nav className="flex items-center gap-1 text-sm text-muted-foreground">
      {items.map((item, i) => (
        <div key={item.href} className="flex items-center gap-1">
          <Link to={item.href} className="hover:text-foreground transition">
            {item.label}
          </Link>
          {i < items.length - 1 && <ChevronRight className="w-4 h-4" />}
        </div>
      ))}
    </nav>
  );
}

// Использование:
<Breadcrumbs items={[
  { label: 'Home', href: '/' },
  { label: 'Configuration', href: '/config' },
  { label: 'Crosshair Editor', href: '/config/crosshair' },
]} />
```

---

## 🔧 Технические улучшения

### 1. Дифф-алгоритм конфигов (advanced)

Вместо простого побайтового сравнения, использовать **semantic diff**:

```rust
// src-tauri/src/services/diff.rs
use similar::{ChangeTag, TextDiff};

pub fn semantic_diff(config_a: &str, config_b: &str) -> Vec<DiffLine> {
  let diff = TextDiff::from_lines(config_a, config_b);
  
  diff.iter_all_changes()
    .map(|change| match change.tag() {
      ChangeTag::Delete => DiffLine::Removed(change.value()),
      ChangeTag::Insert => DiffLine::Added(change.value()),
      ChangeTag::Equal => DiffLine::Unchanged(change.value()),
    })
    .collect()
}
```

**Зачем**: Для красивого отображения различий в Compare tab с цветным diff (красный = убрано, зелёный = добавлено)

---

### 2. Incremental Generation (для больших наборов CVAR)

Кэшировать результаты генерации для быстрого перегенерирования при небольших изменениях:

```rust
// src-tauri/src/services/cache.rs
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;

struct CacheEntry {
  config_hash: u64,
  generated_at: Instant,
  config: CfgConfig,
}

pub struct GenerationCache {
  cache: HashMap<u64, CacheEntry>,
  max_age: Duration,
}

impl GenerationCache {
  pub fn get_or_generate(
    &mut self,
    params: &GenerateParams,
  ) -> Result<CfgConfig> {
    let hash = Self::hash_params(params);
    
    // Если есть в кэше и свежее — вернуть
    if let Some(entry) = self.cache.get(&hash) {
      if entry.generated_at.elapsed() < self.max_age {
        return Ok(entry.config.clone());
      }
    }
    
    // Иначе — генерировать и кэшировать
    let config = generate_config(params)?;
    self.cache.insert(hash, CacheEntry { config_hash: hash, generated_at: Instant::now(), config: config.clone() });
    
    Ok(config)
  }
}
```

**Преимущество**: UI не фризит при быстрых кликах на пресеты

---

### 3. Multi-monitor поддержка

Для Windows пользователей — запоминать позицию окна на каждом мониторе:

```typescript
// src/stores/appStore.ts
interface WindowState {
  x: number;
  y: number;
  width: number;
  height: number;
  maximized: boolean;
  monitorId: string; // Сохранять ID монитора
}

export const useAppStore = create(
  persist(
    (set) => ({
      windowState: null as WindowState | null,
      
      saveWindowState: async () => {
        const appWindow = await getCurrent();
        const position = await appWindow.innerPosition();
        const size = await appWindow.innerSize();
        const isMaximized = await appWindow.isMaximized();
        
        // Определить текущий монитор (Tauri API)
        const monitor = await appWindow.onFocused(() => { /* ... */ });
        
        set({
          windowState: {
            x: position.x,
            y: position.y,
            width: size.width,
            height: size.height,
            maximized: isMaximized,
            monitorId: monitor?.name || 'default',
          },
        });
      },
    }),
    { name: 'window-state' }
  )
);
```

---

### 4. WebSocket для реал-тайм синхронизации (облако)

Если реализуешь Community Configs, можешь использовать WebSocket для реал-тайма:

```rust
// src-tauri/src/services/websocket.rs
use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::StreamExt;

pub async fn sync_with_server(config: &CfgConfig) -> Result<()> {
  let (ws_stream, _) = connect_async("wss://configs.example.com/sync").await?;
  let (mut write, mut read) = ws_stream.split();
  
  // Отправить текущий конфиг
  write.send(Message::Text(serde_json::to_string(config)?)).await?;
  
  // Слушать обновления от других пользователей
  while let Some(msg) = read.next().await {
    if let Ok(Message::Text(text)) = msg {
      let remote_config: CfgConfig = serde_json::from_str(&text)?;
      // Merge или show notification
    }
  }
  
  Ok(())
}
```

---

## 📊 Новый контент для v3.0

### 1. Pro Players Expansion

Добавить **28 про-пресетов** вместо нынешних 18:

**Новые игроки**:
- **SK/MIBR**: coldzera, fer, HEN1, TACO, kng
- **Fnatic**: JW, flusha, Lekr0, Gla1ve, MSL
- **FaZe**: Rain, AdreN, NiKo, ZywOo, Twistzz
- **Astralis**: Device, Xyp9x, Magisk, dupreeh
- **Liquid**: Stewie2K, ELiGE, Nitro, FalleN, tarik
- **Virtus.Pro**: TaZ, NEO, Snax, Potti, SpawN

**Для каждого пресета**:
- Фото 64×64 PNG (хорошее качество)
- Краткая биография (2–3 строки)
- Команда, роль, стиль игры
- Основные характеристики (sensitivity, rate, fps_max, volume, и т.д.)

---

### 2. Game Modes Expansion

**+5 новых режимов**:

- **Jailbreak** — один охранник, остальные заключённые. KZ-элементы.
  - Настройки: низкий fps_max (100), minimal network lag
  
- **Paintball** — стреляют обычными пулями, но виски видят куда они летят
  - Настройки: максимальная visual clarity (cl_dynamiccrosshair 0)
  
- **BaseBuilder** — вариант CTF с постройками
  - Настройки: сбалансированные
  
- **SuperHero** — мод с супер-способностями, нужна высокая реакция
  - Настройки: максимум fps_max, чувствительность по максимуму
  
- **Knife Arena** — только ножи, fast-paced
  - Настройки: максимум fps_max, звук максимум

---

### 3. Interactive Tutorials (видео)

Встроить ссылки на видео-туториалы (YouTube embeds):

```typescript
// src/components/common/VideoTutorial.tsx
interface VideoTutorialProps {
  videoId: string;
  title: string;
  duration: string;
}

export function VideoTutorial({ videoId, title, duration }: VideoTutorialProps) {
  return (
    <div className="group relative overflow-hidden rounded-lg">
      <iframe
        width="100%"
        height="200"
        src={`https://www.youtube.com/embed/${videoId}`}
        title={title}
        allowFullScreen
        className="rounded-lg"
      />
      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition">
        <Button size="lg" variant="secondary">
          ▶ Watch ({duration})
        </Button>
      </div>
    </div>
  );
}

// На Dashboard
<VideoTutorial
  videoId="dQw4w9WgXcQ"
  title="Quick Start: First Config (2 min)"
  duration="2:00"
/>
```

**Видео-контент**:
- Quick Start (2 min) — создание первого конфига
- Advanced Config (10 min) — тонкая настройка CVAR
- Pro Settings Explained (15 min) — что значат про-пресеты
- Crosshair Editor Tutorial (5 min) — как настроить прицел

---

### 4. CVAR Dictionary Expansion

Расширить базу CVAR с новыми полями:

```json
{
  "cl_cmdrate": {
    "name": "cl_cmdrate",
    "category": "network",
    "description": "How many command packets per second the client should send to the server",
    "default": 100,
    "min": 10,
    "max": 128,
    "pro_range": [60, 128],
    "pro_average": 100,
    "related_cvars": ["cl_updaterate", "ex_interp"],
    "tips_ru": "Важна для сетевой синхронизации. На LAN — максимум (128), на плохой сети — 60–80",
    "tips_en": "Critical for network sync. LAN: max (128), poor connection: 60–80",
    "deprecated": false,
    "since_version": "1.0",
    "pro_presets": {
      "f0rest": 100,
      "neo": 128,
      "SpawN": 100
    }
  }
}
```

---

## 🚀 Features за рамками базовой функциональности

### 1. Config Templates Library

Встроенная библиотека готовых конфигов для разных сценариев:

```typescript
// src/data/templates.ts
export const TEMPLATES = {
  'newbie': {
    name: 'Для новичков',
    description: 'Простой конфиг с базовыми настройками',
    settings: {
      sensitivity: 1.5,
      fps_max: 60,
      volume: 0.5,
      // ...
    },
  },
  'competitive': {
    name: 'Соревновательный',
    description: 'Конфиг для турниров с оптимальными балансом',
    // ...
  },
  'high-end-pc': {
    name: 'Высокопроизводительный',
    description: 'На мощном ПК — максимум графики и FPS',
    settings: {
      gl_overbright: 2,
      gl_d3d9to10: 1, // Если поддерживается
      fps_max: 1000,
      // ...
    },
  },
  'potato-pc': {
    name: 'Слабый ПК',
    description: 'Для старых машин — минимум графики, максимум FPS',
    settings: {
      gl_overbright: 0,
      fps_max: 100,
      resolution: '640x480',
      // ...
    },
  },
  'lan-tournament': {
    name: 'LAN турнир',
    description: 'Оптимальный конфиг для локальной сети',
    settings: {
      rate: 30000,
      cl_cmdrate: 128,
      cl_updaterate: 128,
      // ...
    },
  },
};
```

---

### 2. Config Marketplace (Community Configs)

Позволить пользователям делиться конфигами:

```typescript
// src/components/pages/CommunityConfigsPage.tsx
export function CommunityConfigsPage() {
  const [configs, setConfigs] = useState<CommunityConfig[]>([]);
  const [filters, setFilters] = useState({ mode: 'all', rating: 4 });

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        <Select value={filters.mode} onValueChange={(mode) => setFilters({ ...filters, mode })}>
          <SelectTrigger>All Modes</SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Modes</SelectItem>
            <SelectItem value="classic">Classic</SelectItem>
            <SelectItem value="kz">KZ</SelectItem>
            {/* ... */}
          </SelectContent>
        </Select>
        
        <Select value={String(filters.rating)} onValueChange={(rating) => setFilters({ ...filters, rating: Number(rating) })}>
          <SelectTrigger>Minimum Rating</SelectTrigger>
          <SelectContent>
            <SelectItem value="3">⭐⭐⭐+</SelectItem>
            <SelectItem value="4">⭐⭐⭐⭐+</SelectItem>
            <SelectItem value="5">⭐⭐⭐⭐⭐</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {configs.map((config) => (
          <ConfigCard
            key={config.id}
            config={config}
            onDownload={() => importConfig(config)}
          />
        ))}
      </div>
    </div>
  );
}
```

---

### 3. Config Diff Export (Markdown / PDF)

Экспортировать полный отчёт сравнения в Markdown или PDF:

```typescript
// src/lib/export-diff.ts
import html2pdf from 'html2pdf.js';

export async function exportDiffAsPDF(
  yourConfig: Config,
  proPreset: ProPreset
) {
  const element = document.createElement('div');
  element.innerHTML = `
    <h1>Comparison Report</h1>
    <h2>Your Config vs ${proPreset.name}</h2>
    
    <h3>Summary</h3>
    <table>
      <tr>
        <th>CVAR</th>
        <th>Your Value</th>
        <th>Pro Value</th>
        <th>Difference</th>
      </tr>
      <!-- ... generate rows ... -->
    </table>
    
    <h3>Radar Chart</h3>
    <!-- ... embed canvas as image ... -->
  `;

  html2pdf()
    .set({
      margin: 10,
      filename: `comparison-${proPreset.name}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' },
    })
    .save();
}
```

---

### 4. Launch Counter-Strike из приложения

Добавить кнопку для быстрого запуска CS 1.6 с экспортированным конфигом:

```typescript
// src/commands/game.rs (Tauri)
#[tauri::command]
pub async fn launch_game(game_path: String, config_name: String) -> Result<(), String> {
  let hl_exe = Path::new(&game_path).join("hl.exe");
  
  if !hl_exe.exists() {
    return Err("hl.exe not found".into());
  }

  // Запустить с параметрами
  std::process::Command::new(&hl_exe)
    .arg("-game")
    .arg("cstrike")
    .arg("-console")
    .arg("-nobots")
    .arg(format!("+exec {}.cfg", config_name))
    .spawn()
    .map_err(|e| e.to_string())?;

  Ok(())
}
```

```typescript
// React component
<Button onClick={() => invoke('launch_game', { game_path, config_name })}>
  🎮 Launch CS 1.6
</Button>
```

---

## 📈 Метрики для отслеживания

### Performance

```
Startup Time:       < 1.0s
Memory (idle):      < 60 MB
Memory (all tabs):  < 150 MB
Generate config:    < 50ms
Export 11 files:    < 100ms
Canvas redraw:      < 2ms
Page transition:    < 150ms (with animation)
.exe size:          < 15 MB
```

### User Engagement

```
Profiles created:   Среднее значение на пользователя
Templates used:     % пользователей, использующих встроенные шаблоны
Community configs:  Количество загруженных конфигов
Export frequency:   Среднее количество экспортов в день
```

---

**Всё готово для полной миграции на Tauri + React! 🚀**
