# Hướng dẫn code: Phân bổ & Quản lý Nhóm

## Tổng quan

Tính năng gồm:
1. Xem thành viên chưa có nhóm
2. Gán hàng loạt vào nhóm
3. Chuyển thành viên giữa 2 nhóm

---

## Bước 1 — Backend: Filter `group_id=none`

**File:** `server/api/members/index.get.ts`

Tìm chỗ xử lý `group_id` filter, thay như sau:

```typescript
if (group_id === 'none') {
    // Lọc thành viên chưa có nhóm
    selectSql += ` AND m.group_id IS NULL`
    countSql  += ` AND m.group_id IS NULL`
} else if (group_id) {
    selectSql += ` AND m.group_id = ?`
    countSql  += ` AND m.group_id = ?`
    args.push(group_id)
    countArgs.push(group_id)
}
```

---

## Bước 2 — Backend: API Bulk Assign

**File mới:** `server/api/members/bulk-group.post.ts`

```typescript
// POST /api/members/bulk-group
export default defineEventHandler(async (event) => {
    const payload = await requireAuth(event)
    requireRole(payload, ['admin', 'manager'])
    const orgId = getOrgId(payload)
    const { member_ids, group_id } = await readBody(event)

    if (!member_ids?.length)
        throw createError({ statusCode: 400, message: 'Cần chọn ít nhất 1 thành viên' })

    const db = useDB(event)

    // Kiểm tra nhóm đích hợp lệ
    if (group_id) {
        const g = await db.execute({
            sql: `SELECT id FROM groups WHERE id = ? AND org_id = ?`,
            args: [group_id, orgId]
        })
        if (!g.rows.length)
            throw createError({ statusCode: 404, message: 'Nhóm không tồn tại' })
    }

    const ph = member_ids.map(() => '?').join(',')
    const result = await db.execute({
        sql: `UPDATE members SET group_id = ?, updated_at = datetime('now')
              WHERE id IN (${ph}) AND org_id = ?`,
        args: [group_id || null, ...member_ids, orgId]
    })

    return { success: true, updated: result.rowsAffected }
})
```

---

## Bước 3 — Menu & Title

**File:** `app/layouts/AppMenu.vue`

Tìm item "Nhóm", thêm sub-item (chỉ admin/manager):

```typescript
// Trong mảng items của Nhóm:
...(isManager.value
    ? [{ label: 'Phân bổ nhóm', icon: 'pi pi-arrows-h', to: '/groups/assign' }]
    : [])
```

**File:** `app/layouts/AppTopbar.vue` — thêm title:

```typescript
'/groups/assign': 'Phân bổ nhóm',
```

---

## Bước 4 — Frontend: `/groups/assign`

**File mới:** `app/pages/groups/assign.vue`

### Script

```vue
<script setup>
const { apiFetch } = useApi()
const toast = useToast()

const tab = ref(0)          // 0 = Phân bổ, 1 = Chuyển nhóm
const groups = ref([])

// Tab 0 — Gán từ "chưa có nhóm"
const ungrouped = ref([])
const selectedUnassigned = ref([])

// Tab 1 — Chuyển nhóm
const sourceGroupId = ref(null)
const sourceMembers = ref([])
const selectedSource = ref([])

// Chung
const targetGroupId = ref(null)
const saving = ref(false)

const loadGroups = async () => {
    const data = await apiFetch('/api/groups')
    groups.value = data.data || []
}

const loadUngrouped = async () => {
    const data = await apiFetch('/api/members?group_id=none&limit=200')
    ungrouped.value = data.data || []
}

const loadSourceMembers = async () => {
    if (!sourceGroupId.value) return
    const data = await apiFetch(`/api/members?group_id=${sourceGroupId.value}&limit=200`)
    sourceMembers.value = data.data || []
    selectedSource.value = []
}

const doAssign = async () => {
    const ids = tab.value === 0
        ? selectedUnassigned.value.map(m => m.id)
        : selectedSource.value.map(m => m.id)

    if (!ids.length || !targetGroupId.value) return

    saving.value = true
    try {
        await apiFetch('/api/members/bulk-group', {
            method: 'POST',
            body: { member_ids: ids, group_id: targetGroupId.value }
        })
        toast.add({ severity: 'success', summary: `Đã gán ${ids.length} người`, life: 2000 })
        if (tab.value === 0) { await loadUngrouped(); selectedUnassigned.value = [] }
        else { await loadSourceMembers(); selectedSource.value = [] }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message, life: 3000 })
    }
    saving.value = false
}

onMounted(async () => {
    await Promise.all([loadGroups(), loadUngrouped()])
})
</script>
```

### Template

```vue
<template>
  <div>
    <Tabs v-model:value="tab">
      <TabList>
        <Tab :value="0">Chưa có nhóm ({{ ungrouped.length }})</Tab>
        <Tab :value="1">Chuyển nhóm</Tab>
      </TabList>

      <TabPanels>
        <!-- ── Tab 0: Phân bổ ── -->
        <TabPanel :value="0">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
            <!-- Danh sách chưa có nhóm -->
            <DataTable
              v-model:selection="selectedUnassigned"
              :value="ungrouped"
              selectionMode="multiple"
              dataKey="id"
              size="small"
              scrollable scrollHeight="60vh"
            >
              <Column selectionMode="multiple" style="width:2.5rem" />
              <Column field="ho_ten" header="Họ tên" />
              <Column field="phone" header="SĐT" />
            </DataTable>

            <!-- Chọn nhóm đích -->
            <div class="flex flex-col gap-3">
              <p class="text-sm font-medium">
                Đã chọn: <strong>{{ selectedUnassigned.length }}</strong> người
              </p>
              <Select
                v-model="targetGroupId"
                :options="groups"
                optionLabel="ten_nhom"
                optionValue="id"
                placeholder="Chọn nhóm đích..."
                class="w-full"
              />
              <Button
                label="Gán vào nhóm"
                icon="pi pi-check"
                :disabled="!selectedUnassigned.length || !targetGroupId"
                :loading="saving"
                @click="doAssign"
              />
            </div>
          </div>
        </TabPanel>

        <!-- ── Tab 1: Chuyển nhóm ── -->
        <TabPanel :value="1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
            <!-- Cột trái: chọn nhóm nguồn -->
            <div class="flex flex-col gap-3">
              <Select
                v-model="sourceGroupId"
                :options="groups"
                optionLabel="ten_nhom"
                optionValue="id"
                placeholder="Chọn nhóm nguồn..."
                class="w-full"
                @change="loadSourceMembers"
              />
              <DataTable
                v-model:selection="selectedSource"
                :value="sourceMembers"
                selectionMode="multiple"
                dataKey="id"
                size="small"
                scrollable scrollHeight="55vh"
              >
                <Column selectionMode="multiple" style="width:2.5rem" />
                <Column field="ho_ten" header="Họ tên" />
                <Column field="phone" header="SĐT" />
              </DataTable>
            </div>

            <!-- Cột phải: chọn nhóm đích -->
            <div class="flex flex-col gap-3">
              <p class="text-sm font-medium">
                Đã chọn: <strong>{{ selectedSource.length }}</strong> người
              </p>
              <Select
                v-model="targetGroupId"
                :options="groups.filter(g => g.id !== sourceGroupId)"
                optionLabel="ten_nhom"
                optionValue="id"
                placeholder="Chọn nhóm đích..."
                class="w-full"
              />
              <Button
                label="Chuyển sang nhóm đích"
                icon="pi pi-arrow-right"
                :disabled="!selectedSource.length || !targetGroupId"
                :loading="saving"
                @click="doAssign"
              />
            </div>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>

    <Toast />
  </div>
</template>
```

---

## Bước 5 — Test checklist

| Kịch bản | Kết quả mong đợi |
|---|---|
| Tab "Chưa có nhóm" | Hiện đúng thành viên `group_id IS NULL` |
| Tick 3 người → chọn nhóm → Gán | 3 người biến khỏi danh sách |
| Tab "Chuyển nhóm" → chọn nguồn → tick → chọn đích → Chuyển | Thành viên đổi nhóm |
| `leader` truy cập `/groups/assign` | Menu ẩn, API trả 403 |
| `group_id` không thuộc org | API trả 404 "Nhóm không tồn tại" |
