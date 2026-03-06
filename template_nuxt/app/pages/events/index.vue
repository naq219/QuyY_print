<script setup lang="ts">
const { apiFetch } = useApi()
const { user } = useAuth()
const router = useRouter()
const toast = useToast()

const events = ref<any[]>([])
const loading = ref(true)
const showDialog = ref(false)
const editMode = ref(false)
const saving = ref(false)
const filterStatus = ref('')
const searchText = ref('')

const isAdminOrManager = computed(() => user.value?.role === 'admin' || user.value?.role === 'manager')

const loaiHinhOptions = [
  { label: '🙏 Tụng kinh', value: 'tung_kinh' },
  { label: '💝 Thiện nguyện', value: 'thien_nguyen' },
  { label: '🧘 Khóa tu', value: 'khoa_tu' },
  { label: '🎉 Lễ hội', value: 'le_hoi' },
  { label: '📋 Khác', value: 'khac' }
]

const statusOptions = [
  { label: 'Tất cả', value: '' },
  { label: '📋 Lên kế hoạch', value: 'planned' },
  { label: '▶️ Đang diễn ra', value: 'ongoing' },
  { label: '✅ Đã kết thúc', value: 'completed' },
  { label: '❌ Hủy', value: 'cancelled' }
]

const statusLabel: Record<string, string> = {
  planned: '📋 Lên kế hoạch',
  ongoing: '▶️ Đang diễn ra',
  completed: '✅ Đã kết thúc',
  cancelled: '❌ Hủy'
}
const statusSeverity: Record<string, string> = {
  planned: 'info',
  ongoing: 'warn',
  completed: 'success',
  cancelled: 'danger'
}

const loaiHinhLabel: Record<string, string> = {
  tung_kinh: '🙏 Tụng kinh',
  thien_nguyen: '💝 Thiện nguyện',
  khoa_tu: '🧘 Khóa tu',
  le_hoi: '🎉 Lễ hội',
  khac: '📋 Khác'
}

const form = ref({
  id: '',
  ten_su_kien: '',
  loai_hinh: 'tung_kinh',
  thoi_gian_bat_dau: '',
  thoi_gian_ket_thuc: '',
  dia_diem: '',
  mo_ta: '',
  trang_thai: 'planned'
})

const loadEvents = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filterStatus.value) params.set('trang_thai', filterStatus.value)
    if (searchText.value) params.set('search', searchText.value)
    const data = await apiFetch(`/api/events?${params.toString()}`)
    events.value = data.data
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Không tải được', life: 3000 })
  }
  loading.value = false
}

const openCreate = () => {
  form.value = { id: '', ten_su_kien: '', loai_hinh: 'tung_kinh', thoi_gian_bat_dau: '', thoi_gian_ket_thuc: '', dia_diem: '', mo_ta: '', trang_thai: 'planned' }
  editMode.value = false
  showDialog.value = true
}

const openEdit = (e: any) => {
  form.value = { ...e }
  editMode.value = true
  showDialog.value = true
}

const saveEvent = async () => {
  if (!form.value.ten_su_kien || !form.value.loai_hinh || !form.value.thoi_gian_bat_dau) {
    toast.add({ severity: 'warn', summary: 'Thiếu', detail: 'Điền tên, loại hình, thời gian', life: 3000 })
    return
  }
  saving.value = true
  try {
    if (editMode.value) {
      await apiFetch(`/api/events/${form.value.id}`, { method: 'PUT', body: form.value })
    } else {
      await apiFetch('/api/events', { method: 'POST', body: form.value })
    }
    toast.add({ severity: 'success', summary: 'OK', detail: editMode.value ? 'Cập nhật thành công' : 'Tạo thành công', life: 3000 })
    showDialog.value = false
    loadEvents()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Thất bại', life: 3000 })
  }
  saving.value = false
}

const deleteEvent = async (e: any) => {
  if (!confirm(`Xóa sự kiện "${e.ten_su_kien}"? Toàn bộ dữ liệu điểm danh cũng sẽ bị xóa.`)) return
  try {
    await apiFetch(`/api/events/${e.id}`, { method: 'DELETE' })
    toast.add({ severity: 'success', summary: 'Đã xóa', life: 3000 })
    loadEvents()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message, life: 3000 })
  }
}

const formatDate = (d: string) => {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }
  catch { return d }
}

onMounted(loadEvents)
watch([filterStatus, searchText], loadEvents)
</script>

<template>
  <div>
    <!-- Header compact -->
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg md:text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">Sự kiện</h2>
      <Button v-if="isAdminOrManager" icon="pi pi-plus" class="md:hidden" rounded size="small" @click="openCreate" />
      <Button v-if="isAdminOrManager" label="Tạo sự kiện" icon="pi pi-plus" class="hidden md:inline-flex" @click="openCreate" />
    </div>

    <!-- Search + Filter compact -->
    <div class="flex gap-2 mb-3">
      <InputText v-model="searchText" placeholder="Tìm tên, địa điểm..." class="flex-1" />
      <Select v-model="filterStatus" :options="statusOptions" optionLabel="label" optionValue="value"
        placeholder="Trạng thái" class="w-36 md:w-48" />
    </div>

    <div class="card">
      <DataTable :value="events" :loading="loading" stripedRows>
        <template #empty>Chưa có sự kiện nào</template>
        <Column field="ten_su_kien" header="Sự kiện" sortable>
          <template #body="{ data }">
            <div>
              <NuxtLink :to="`/events/${data.id}`" class="font-semibold text-primary hover:underline cursor-pointer">
                {{ data.ten_su_kien }}
              </NuxtLink>
              <div class="text-sm text-muted-color mt-1">{{ loaiHinhLabel[data.loai_hinh] || data.loai_hinh }}</div>
            </div>
          </template>
        </Column>
        <Column field="thoi_gian_bat_dau" header="Thời gian" sortable class="hidden md:table-cell">
          <template #body="{ data }">
            <div class="text-sm">{{ formatDate(data.thoi_gian_bat_dau) }}</div>
          </template>
        </Column>
        <Column field="dia_diem" header="Địa điểm" class="hidden lg:table-cell">
          <template #body="{ data }">
            <span>{{ data.dia_diem || '—' }}</span>
          </template>
        </Column>
        <Column field="trang_thai" header="" style="width: 70px">
          <template #body="{ data }">
            <Tag :value="statusLabel[data.trang_thai] || data.trang_thai" :severity="statusSeverity[data.trang_thai]" />
          </template>
        </Column>
        <Column field="attendee_count" header="" style="width: 50px">
          <template #body="{ data }">
            <Badge :value="data.attendee_count" severity="info" />
          </template>
        </Column>
        <Column v-if="isAdminOrManager" header="" style="width: 80px">
          <template #body="{ data }">
            <div class="flex gap-1">
              <Button icon="pi pi-pencil" text rounded severity="info" size="small" @click="openEdit(data)" />
              <Button v-if="user?.role === 'admin'" icon="pi pi-trash" text rounded severity="danger" size="small" @click="deleteEvent(data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Dialog tạo/sửa -->
    <Dialog v-model:visible="showDialog" :header="editMode ? 'Sửa sự kiện' : 'Tạo sự kiện mới'" modal :style="{ width: '560px' }">
      <div class="flex flex-col gap-4 pt-2">
        <div class="flex flex-col gap-2">
          <label class="font-medium">Tên sự kiện <span class="text-red-500">*</span></label>
          <InputText v-model="form.ten_su_kien" class="w-full" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">Loại hình <span class="text-red-500">*</span></label>
          <Select v-model="form.loai_hinh" :options="loaiHinhOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Bắt đầu <span class="text-red-500">*</span></label>
            <InputText v-model="form.thoi_gian_bat_dau" type="datetime-local" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Kết thúc</label>
            <InputText v-model="form.thoi_gian_ket_thuc" type="datetime-local" class="w-full" />
          </div>
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">Địa điểm</label>
          <InputText v-model="form.dia_diem" class="w-full" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">Mô tả</label>
          <Textarea v-model="form.mo_ta" rows="3" class="w-full" />
        </div>
        <div v-if="editMode" class="flex flex-col gap-2">
          <label class="font-medium">Trạng thái</label>
          <Select v-model="form.trang_thai" :options="statusOptions.filter(s => s.value)" optionLabel="label" optionValue="value" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Hủy" severity="secondary" text @click="showDialog = false" />
        <Button :label="editMode ? 'Cập nhật' : 'Tạo mới'" icon="pi pi-check" :loading="saving" @click="saveEvent" />
      </template>
    </Dialog>

    <Toast />
  </div>
</template>
