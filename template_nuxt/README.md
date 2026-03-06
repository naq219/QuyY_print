# Chăm sóc Thành viên — Hệ thống Quản lý Tổ chức Phật giáo

Nền tảng web quản lý thông tin và chăm sóc thành viên tổ chức Phật giáo.

## Tech Stack

- **Nuxt 4** (SPA mode)
- **PrimeVue 4** + **PrimeIcons** — UI Components
- **TailwindCSS** + **tailwindcss-primeui** — Styling
- **PocketBase** — Backend API & Database
- **SCSS** — Layout styling

## Cài đặt

```bash
npm install
npm run dev
```

## Cấu trúc thư mục

```
app/
├── assets/layout/    # SCSS layout (topbar, sidebar, menu...)
├── composables/      # usePocketBase, useLayout
├── layouts/          # AppLayout, AppTopbar, AppMenu, AppFooter
├── pages/            # Các trang
│   └── index.vue     # Dashboard
```
