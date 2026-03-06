---
description: Rules để tránh lỗi khi code Nuxt + Vue + Cloudflare Pages
---

# Nuxt + Vue + Cloudflare Pages — Coding Rules

## 1. Vue SFC: Luôn dùng `lang="ts"` nếu có TypeScript syntax

```vue
<!-- ❌ SAI — `as string`, generics sẽ lỗi compile -->
<script setup>
const x = route.params.id as string
</script>

<!-- ✅ ĐÚNG -->
<script setup lang="ts">
const x = route.params.id as string
</script>
```

**Lý do:** Vue SFC mặc định là JavaScript. Nếu dùng `as`, generics, interface... mà không có `lang="ts"` sẽ bị lỗi `Unexpected token`.

## 2. Local dev trước, deploy sau

```bash
# Workflow đúng:
npm run dev          # Test ở localhost:3000
# OK rồi mới:
npm run build && npx wrangler pages deploy dist --project-name=huynhde
```

**Không bao giờ** deploy rồi mới test. Luôn test local trước.

## 3. File `.env` cho dev local

Nuxt tự động load `.env` khi `npm run dev`. Đặt biến với prefix `NUXT_`:

```env
NUXT_TURSO_URL=libsql://...
NUXT_TURSO_TOKEN=eyJ...
NUXT_JWT_SECRET=secret-key
```

Tương ứng với `runtimeConfig` trong `nuxt.config.ts`:
```ts
runtimeConfig: {
  tursoUrl: '',    // → NUXT_TURSO_URL
  tursoToken: '',  // → NUXT_TURSO_TOKEN
  jwtSecret: '',   // → NUXT_JWT_SECRET
}
```

## 4. Server utils auto-import

Nuxt auto-import các file trong `server/utils/`. Không cần `import` trong API routes:

```ts
// server/api/example.ts
// ❌ SAI — không cần import
import { useDB } from '~/server/utils/db'

// ✅ ĐÚNG — tự có, IDE sẽ warning nhưng build OK
const db = useDB(event)
```

## 5. Cloudflare Pages: dùng `@libsql/client/web`

```ts
// ✅ Edge-compatible (Cloudflare Workers / Pages)
import { createClient } from '@libsql/client/web'

// ❌ Chỉ chạy trên Node.js
import { createClient } from '@libsql/client'
```

## 6. Crypto trên Edge: dùng Web Crypto API + jose

```ts
// ❌ Không chạy trên Edge
import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'

// ✅ Edge-compatible
import { SignJWT, jwtVerify } from 'jose'
// Password hash: dùng crypto.subtle.importKey + deriveBits (PBKDF2)
```

## 7. PowerShell curl: dùng `curl.exe` không phải `curl`

```powershell
# ❌ SAI — PowerShell alias curl = Invoke-WebRequest
curl -X POST http://localhost:3000/api/init

# ✅ ĐÚNG — gọi curl thật
curl.exe -X POST http://localhost:3000/api/init -H "Content-Type: application/json"
```

## 8. Deploy Cloudflare Pages: URL production vs preview

- `huynhde.pages.dev` = production (branch main)
- `<hash>.huynhde.pages.dev` = preview (mỗi lần deploy)
- Cả hai đều hoạt động, nhưng env vars phải được set đúng trên Cloudflare dashboard

## 9. NuxtHub: Không cần nếu dùng Turso

NuxtHub dành cho Cloudflare D1. Nếu dùng Turso thì giữ Nuxt + nitro preset `cloudflare-pages` là đủ.
