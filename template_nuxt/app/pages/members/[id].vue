<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const { apiFetch } = useApi()
const toast = useToast()

const member = ref(null)
const loading = ref(true)
const activeTab = ref(0)

// Edit mode
const editMode = ref(false)
const groups = ref([])
const saving = ref(false)
const editForm = ref({})

// Care Notes
const careNotes = ref([])
const careLoading = ref(false)
const showCareDialog = ref(false)
const careSaving = ref(false)
const careFilter = ref('')
const careSearch = ref('')

// === MỚI: Lọc theo sự kiện ===
const events = ref<any[]>([])
const selectedEventId = ref('')       // '' = tất cả, có ID = lọc theo sự kiện này
const selectedEventAttendee = ref(null) // kết quả check-in thực tế (nếu có)

// Activities (điểm danh)
const activities = ref<any[]>([])
const activitiesLoading = ref(false)

const careForm = ref({
  hinh_thuc: 'call',
  noi_dung: '',
  phan_hoi: null,
  follow_up: false,
  follow_up_date: null,
  event_id: null,           // MỚI: gắn sự kiện
  trang_thai_sk: 'chua_lien_lac'   // MỚI: trạng thái tham dự
})

// === Options ===
const gioiTinhOptions = [{ label: 'Nam', value: 'nam' }, { label: 'Nữ', value: 'nu' }]
const statusOptions = [
  { label: 'Đang hoạt động', value: 'active' },
  { label: 'Tạm nghỉ', value: 'paused' },
  { label: 'Đã rời nhóm', value: 'left' }
]
const statusSeverity = { active: 'success', paused: 'warn', left: 'danger' }
const statusLabel = { active: 'Hoạt động', paused: 'Tạm nghỉ', left: 'Đã rời' }

const hinhThucOptions = [
  { label: '📞 Gọi điện', value: 'call' },
  { label: '💬 Nhắn tin', value: 'message' },
  { label: '🏠 Thăm trực tiếp', value: 'visit' },
  { label: '🎁 Gửi quà', value: 'gift' },
  { label: '📋 Khác', value: 'other' }
]
const hinhThucLabel = {
  call: '📞 Gọi điện', message: '💬 Nhắn tin', visit: '🏠 Thăm trực tiếp',
  gift: '🎁 Gửi quà', other: '📋 Khác'
}
const phanHoiOptions = [
  { label: '😊 Vui vẻ', value: 'happy' },
  { label: '😐 Bình thường', value: 'normal' },
  { label: '😟 Cần hỗ trợ thêm', value: 'need_help' },
  { label: '📵 Không liên lạc được', value: 'no_contact' }
]
const phanHoiLabel = {
  happy: '😊 Vui vẻ', normal: '😐 Bình thường',
  need_help: '😟 Cần hỗ trợ', no_contact: '📵 Không liên lạc được'
}

// === MỚI: Trạng thái tham dự sự kiện ===
const trangThaiSkOptions = [
  { label: '📵 Chưa liên lạc được', value: 'chua_lien_lac' },
  { label: '✅ Sẽ tham gia', value: 'se_tham_gia' },
  { label: '❌ Không tham gia', value: 'khong_tham_gia' },
  { label: '🎯 Đã tham gia', value: 'da_tham_gia' }
]
const trangThaiSkLabel: Record<string, string> = {
  chua_lien_lac: '📵 Chưa liên lạc',
  se_tham_gia: '✅ Sẽ tham gia',
  khong_tham_gia: '❌ Không tham gia',
  da_tham_gia: '🎯 Đã tham gia'
}
const trangThaiSkSeverity: Record<string, string> = {
  chua_lien_lac: 'secondary',
  se_tham_gia: 'success',
  khong_tham_gia: 'danger',
  da_tham_gia: 'info'
}

const loaiHinhEventLabel: Record<string, string> = {
  tung_kinh: '🙏 Tụng kinh', thien_nguyen: '💝 Thiện nguyện',
  khoa_tu: '🧘 Khóa tu', le_hoi: '🎉 Lễ hội', khac: '📋 Khác'
}

// === Load functions ===
const loadMember = async () => {
  loading.value = true
  try {
    const data = await apiFetch(`/api/members/${route.params.id}`)
    member.value = data.data
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: 'Không tìm thấy thành viên', life: 3000 })
    router.push('/members')
  }
  loading.value = false
}

const loadGroups = async () => {
  try { groups.value = (await apiFetch('/api/groups')).data } catch {}
}

const loadEvents = async () => {
  try {
    const data = await apiFetch('/api/events')
    events.value = data.data || []
  } catch {}
}

const loadCareNotes = async () => {
  careLoading.value = true
  try {
    const params: Record<string, string> = { member_id: route.params.id as string }
    if (careFilter.value) params.hinh_thuc = careFilter.value
    if (careSearch.value) params.search = careSearch.value
    if (selectedEventId.value) params.event_id = selectedEventId.value

    const data = await apiFetch(`/api/care-notes?${new URLSearchParams(params)}`)
    careNotes.value = data.data

    // Nếu đang lọc theo sự kiện → kiểm tra member có check-in không
    if (selectedEventId.value) {
      selectedEventAttendee.value = activities.value.find(
        (a: any) => a.event_id === selectedEventId.value
      ) || null
    } else {
      selectedEventAttendee.value = null
    }
  } catch {}
  careLoading.value = false
}

const loadActivities = async () => {
  activitiesLoading.value = true
  try {
    const data = await apiFetch(`/api/attendance/member/${route.params.id}`)
    activities.value = data.data
  } catch {}
  activitiesLoading.value = false
}

// === Edit member ===
const startEdit = () => {
  editForm.value = { ...member.value, ngay_sinh: member.value.ngay_sinh || '' }
  editMode.value = true
  loadGroups()
}
const cancelEdit = () => { editMode.value = false }
const saveEdit = async () => {
  saving.value = true
  try {
    await apiFetch(`/api/members/${route.params.id}`, { method: 'PUT', body: editForm.value })
    toast.add({ severity: 'success', summary: 'Thành công', detail: 'Cập nhật thành công', life: 3000 })
    editMode.value = false
    loadMember()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Cập nhật thất bại', life: 3000 })
  }
  saving.value = false
}

// === Care Note CRUD ===
const openCareDialog = (presetEventId?: string) => {
  careForm.value = {
    hinh_thuc: 'call', noi_dung: '', phan_hoi: null,
    follow_up: false, follow_up_date: null,
    event_id: presetEventId || selectedEventId.value || null,
    trang_thai_sk: 'chua_lien_lac'
  }
  showCareDialog.value = true
}

const saveCareNote = async () => {
  if (!careForm.value.noi_dung) {
    toast.add({ severity: 'warn', summary: 'Thiếu thông tin', detail: 'Vui lòng nhập nội dung', life: 3000 })
    return
  }
  careSaving.value = true
  try {
    await apiFetch('/api/care-notes', {
      method: 'POST',
      body: {
        member_id: route.params.id,
        ...careForm.value,
        follow_up_date: careForm.value.follow_up_date instanceof Date
          ? careForm.value.follow_up_date.toISOString().split('T')[0]
          : careForm.value.follow_up_date
      }
    })
    toast.add({ severity: 'success', summary: 'Đã lưu', detail: 'Ghi chú chăm sóc đã được lưu', life: 3000 })
    showCareDialog.value = false
    loadCareNotes()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Lưu thất bại', life: 3000 })
  }
  careSaving.value = false
}

const deleteCareNote = async (note: any) => {
  if (!confirm('Xóa ghi chú chăm sóc này?')) return
  try {
    await apiFetch(`/api/care-notes/${note.id}`, { method: 'DELETE' })
    toast.add({ severity: 'success', summary: 'Đã xóa', detail: 'Xóa ghi chú thành công', life: 3000 })
    loadCareNotes()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Xóa thất bại', life: 3000 })
  }
}

const deleteMember = async () => {
  if (!confirm(`Xóa thành viên "${member.value?.ho_ten}"?`)) return
  try {
    await apiFetch(`/api/members/${route.params.id}`, { method: 'DELETE' })
    router.push('/members')
  } catch {}
}

const formatDateTime = (dt: any) => {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleDateString('vi-VN') + ' ' + d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
}

// Tên sự kiện đang lọc
const selectedEventName = computed(() => {
  if (!selectedEventId.value) return ''
  return events.value.find((e: any) => e.id === selectedEventId.value)?.ten_su_kien || ''
})

onMounted(async () => {
  await Promise.all([loadMember(), loadEvents(), loadActivities()])
  loadCareNotes()
})

let careSearchTimeout: any
const onCareSearch = () => {
  clearTimeout(careSearchTimeout)
  careSearchTimeout = setTimeout(loadCareNotes, 400)
}

watch(careFilter, loadCareNotes)
watch(selectedEventId, loadCareNotes)
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8"><ProgressSpinner /></div>

    <div v-else-if="member">
      <!-- Header -->
      <div class="card mb-4">
        <div class="flex items-center gap-4 flex-wrap">
          <NuxtLink to="/members"><Button icon="pi pi-arrow-left" text rounded /></NuxtLink>
          <div class="flex items-center justify-center bg-primary/10 rounded-full" style="width: 3.5rem; height: 3.5rem">
            <i class="pi pi-user text-primary text-2xl"></i>
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-1">{{ member.ho_ten }}</h2>
            <div class="flex items-center gap-3 text-muted-color flex-wrap">
              <span v-if="member.phap_danh">PD: {{ member.phap_danh }}</span>
              <Tag :value="member.group_name || '—'" severity="info" />
              <Tag :value="statusLabel[member.trang_thai]" :severity="statusSeverity[member.trang_thai]" />
            </div>
          </div>
          <div class="flex gap-2">
            <Button label="📝 Ghi chú" icon="pi pi-plus" @click="openCareDialog()" />
            <Button v-if="!editMode" label="Sửa" icon="pi pi-pencil" severity="info" outlined @click="startEdit" />
            <Button icon="pi pi-trash" severity="danger" text rounded @click="deleteMember" />
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <Tabs v-model:value="activeTab">
        <TabList>
          <Tab :value="0"><i class="pi pi-id-card mr-2"></i>Thông tin</Tab>
          <Tab :value="1">
            <i class="pi pi-comments mr-2"></i>Lịch sử chăm sóc
            <Badge v-if="careNotes.length" :value="careNotes.length" class="ml-2" />
          </Tab>
          <Tab :value="2"><i class="pi pi-calendar mr-2"></i>Hoạt động</Tab>
        </TabList>

        <TabPanels>
          <!-- Tab Thông tin -->
          <TabPanel :value="0">
            <div v-if="!editMode" class="grid mt-4">
              <div class="col-12 md:col-6">
                <div class="card">
                  <h3 class="font-semibold text-lg mb-4"><i class="pi pi-user mr-2"></i>Thông tin cơ bản</h3>
                  <div class="flex flex-col gap-3">
                    <div class="flex justify-between"><span class="text-muted-color">Họ và tên</span><span class="font-medium">{{ member.ho_ten }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">Pháp danh</span><span class="font-medium">{{ member.phap_danh || '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">Giới tính</span><span class="font-medium">{{ member.gioi_tinh === 'nam' ? 'Nam' : member.gioi_tinh === 'nu' ? 'Nữ' : '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">Năm sinh</span><span class="font-medium">{{ member.ngay_sinh || '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">Nhóm</span><span class="font-medium">{{ member.group_name || '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">Gia nhập</span><span class="font-medium">{{ member.ngay_gia_nhap ? new Date(member.ngay_gia_nhap).toLocaleDateString('vi-VN') : '—' }}</span></div>
                  </div>
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="card">
                  <h3 class="font-semibold text-lg mb-4"><i class="pi pi-phone mr-2"></i>Liên lạc</h3>
                  <div class="flex flex-col gap-3">
                    <div class="flex justify-between"><span class="text-muted-color">SĐT chính</span><span class="font-medium">{{ member.phone }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">SĐT phụ</span><span class="font-medium">{{ member.phone2 || '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">Zalo/FB</span><span class="font-medium">{{ member.zalo_fb || '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">Tỉnh/TP</span><span class="font-medium">{{ member.tinh_tp || '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">Xã/Phường</span><span class="font-medium">{{ member.xa_phuong || '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-muted-color">Địa chỉ</span><span class="font-medium">{{ member.dia_chi || '—' }}</span></div>
                  </div>
                </div>
              </div>
              <div class="col-12">
                <div class="card">
                  <h3 class="font-semibold text-lg mb-4"><i class="pi pi-info-circle mr-2"></i>Bổ sung</h3>
                  <div class="grid">
                    <div class="col-12 md:col-4"><div class="text-muted-color mb-1">Công việc</div><div class="font-medium">{{ member.cong_viec || '—' }}</div></div>
                    <div class="col-12 md:col-4"><div class="text-muted-color mb-1">Sức khỏe</div><div class="font-medium">{{ member.suc_khoe || '—' }}</div></div>
                    <div class="col-12 md:col-4"><div class="text-muted-color mb-1">Kỹ năng</div><div class="font-medium">{{ member.ky_nang || '—' }}</div></div>
                    <div v-if="member.nguoi_gioi_thieu" class="col-12 md:col-6"><div class="text-muted-color mb-1">Người giới thiệu</div><div class="font-medium">{{ member.nguoi_gioi_thieu }}</div></div>
                    <div v-if="member.ghi_chu" class="col-12"><div class="text-muted-color mb-1">Ghi chú</div><div class="font-medium whitespace-pre-wrap">{{ member.ghi_chu }}</div></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Edit Mode -->
            <div v-else class="mt-4">
              <div class="card mb-4">
                <div class="font-semibold text-lg mb-4">Sửa thông tin</div>
                <div class="grid">
                  <div class="col-12 md:col-6"><label class="font-medium mb-2 block">Họ và tên *</label><InputText v-model="editForm.ho_ten" class="w-full" /></div>
                  <div class="col-12 md:col-6"><label class="font-medium mb-2 block">Pháp danh</label><InputText v-model="editForm.phap_danh" class="w-full" /></div>
                  <div class="col-12 md:col-4"><label class="font-medium mb-2 block">Giới tính *</label><Select v-model="editForm.gioi_tinh" :options="gioiTinhOptions" optionLabel="label" optionValue="value" class="w-full" /></div>
                  <div class="col-12 md:col-4"><label class="font-medium mb-2 block">Năm sinh</label><InputText v-model="editForm.ngay_sinh" class="w-full" placeholder="1990 hoặc 01/02/1990" /></div>
                  <div class="col-12 md:col-4"><label class="font-medium mb-2 block">Nhóm *</label><Select v-model="editForm.group_id" :options="groups" optionLabel="ten_nhom" optionValue="id" class="w-full" /></div>
                  <div class="col-12 md:col-4"><label class="font-medium mb-2 block">Trạng thái</label><Select v-model="editForm.trang_thai" :options="statusOptions" optionLabel="label" optionValue="value" class="w-full" /></div>
                  <div class="col-12 md:col-4"><label class="font-medium mb-2 block">SĐT chính *</label><InputText v-model="editForm.phone" class="w-full" /></div>
                  <div class="col-12 md:col-4"><label class="font-medium mb-2 block">SĐT phụ</label><InputText v-model="editForm.phone2" class="w-full" /></div>
                  <div class="col-12 md:col-4"><label class="font-medium mb-2 block">Zalo/FB</label><InputText v-model="editForm.zalo_fb" class="w-full" /></div>
                  <div class="col-12 md:col-4"><label class="font-medium mb-2 block">Tỉnh/TP</label><InputText v-model="editForm.tinh_tp" class="w-full" /></div>
                  <div class="col-12 md:col-4"><label class="font-medium mb-2 block">Xã/Phường</label><InputText v-model="editForm.xa_phuong" class="w-full" /></div>
                  <div class="col-12 md:col-6"><label class="font-medium mb-2 block">Địa chỉ</label><InputText v-model="editForm.dia_chi" class="w-full" /></div>
                  <div class="col-12 md:col-6"><label class="font-medium mb-2 block">Công việc</label><InputText v-model="editForm.cong_viec" class="w-full" /></div>
                  <div class="col-12 md:col-6"><label class="font-medium mb-2 block">Sức khỏe</label><InputText v-model="editForm.suc_khoe" class="w-full" /></div>
                  <div class="col-12 md:col-6"><label class="font-medium mb-2 block">Kỹ năng</label><InputText v-model="editForm.ky_nang" class="w-full" /></div>
                  <div class="col-12"><label class="font-medium mb-2 block">Ghi chú</label><Textarea v-model="editForm.ghi_chu" rows="3" class="w-full" /></div>
                </div>
                <div class="flex justify-end gap-3 mt-4">
                  <Button label="Hủy" severity="secondary" text @click="cancelEdit" />
                  <Button label="Lưu" icon="pi pi-check" :loading="saving" @click="saveEdit" />
                </div>
              </div>
            </div>
          </TabPanel>

          <!-- Tab Lịch sử chăm sóc -->
          <TabPanel :value="1">
            <div class="mt-4">
              <!-- Toolbar: filter hình thức + lọc sự kiện -->
              <div class="flex justify-between items-center mb-4 flex-wrap gap-3">
                <div class="flex gap-3 flex-wrap items-center">
                  <Select
                    v-model="selectedEventId"
                    :options="[{ label: '📋 Tất cả chăm sóc', id: '' }, ...events]"
                    optionLabel="ten_su_kien"
                    optionValue="id"
                    :placeholder="'📋 Tất cả chăm sóc'"
                    class="w-56"
                  >
                    <template #option="slotProps">
                      <span v-if="!slotProps.option.id" class="text-muted-color">📋 Tất cả chăm sóc</span>
                      <span v-else>🗓 {{ slotProps.option.ten_su_kien }}</span>
                    </template>
                    <template #value="slotProps">
                      <span v-if="!slotProps.value">📋 Tất cả chăm sóc</span>
                      <span v-else>🗓 {{ selectedEventName }}</span>
                    </template>
                  </Select>
                  <Select v-model="careFilter" :options="[{ label: 'Tất cả hình thức', value: '' }, ...hinhThucOptions]"
                    optionLabel="label" optionValue="value" class="w-44" />
                </div>
                <Button label="📝 Ghi chú" icon="pi pi-plus" @click="openCareDialog()" />
              </div>

              <!-- Banner kết quả check-in (khi lọc theo sự kiện) -->
              <div v-if="selectedEventId" class="mb-4">
                <div v-if="selectedEventAttendee"
                  class="flex items-center gap-3 p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700">
                  <i class="pi pi-check-circle text-green-500 text-xl"></i>
                  <div>
                    <div class="font-semibold text-green-700 dark:text-green-300">✅ Đã check-in tại sự kiện</div>
                    <div class="text-sm text-green-600 dark:text-green-400">
                      Thời gian: {{ formatDateTime(selectedEventAttendee.checked_in_at) }}
                    </div>
                  </div>
                </div>
                <div v-else
                  class="flex items-center gap-3 p-3 rounded-lg bg-surface-100 dark:bg-surface-800 border">
                  <i class="pi pi-times-circle text-muted-color text-xl"></i>
                  <div class="text-muted-color">Chưa check-in tại sự kiện này</div>
                </div>
              </div>

              <!-- Timeline care notes -->
              <div v-if="careLoading" class="flex justify-center py-4"><ProgressSpinner /></div>
              <div v-else-if="careNotes.length === 0" class="card text-center py-8">
                <i class="pi pi-comments text-4xl mb-3 block text-muted-color"></i>
                <p class="text-lg text-muted-color">
                  {{ selectedEventId ? `Chưa có ghi chú chăm sóc cho sự kiện này` : 'Chưa có ghi chú chăm sóc nào' }}
                </p>
                <Button label="Tạo ghi chú đầu tiên" icon="pi pi-plus" class="mt-3" @click="openCareDialog()" />
              </div>
              <div v-else class="flex flex-col gap-3">
                <div v-for="note in careNotes" :key="note.id" class="card">
                  <div class="flex justify-between items-start">
                    <div class="flex items-center gap-3 mb-2 flex-wrap">
                      <span class="text-lg">{{ hinhThucLabel[note.hinh_thuc] || note.hinh_thuc }}</span>
                      <span class="text-muted-color text-sm">{{ formatDateTime(note.thoi_gian) }}</span>
                      <!-- Badge tên sự kiện (khi xem tất cả) -->
                      <Tag v-if="note.ten_su_kien && !selectedEventId" :value="'🗓 ' + note.ten_su_kien" severity="info" />
                      <!-- Badge trạng thái tham dự -->
                      <Tag v-if="note.trang_thai_sk" :value="trangThaiSkLabel[note.trang_thai_sk]"
                        :severity="trangThaiSkSeverity[note.trang_thai_sk]" />
                    </div>
                    <Button icon="pi pi-times" text rounded severity="danger" size="small" @click="deleteCareNote(note)" />
                  </div>
                  <div class="text-sm text-muted-color mb-2">
                    Người chăm sóc: <span class="font-medium">{{ note.created_by_name || '—' }}</span>
                  </div>
                  <div class="whitespace-pre-wrap mb-2">{{ note.noi_dung }}</div>
                  <div class="flex items-center gap-4 flex-wrap">
                    <span v-if="note.phan_hoi" class="text-sm">
                      Phản hồi: <span class="font-medium">{{ phanHoiLabel[note.phan_hoi] || note.phan_hoi }}</span>
                    </span>
                    <span v-if="note.follow_up" class="text-sm text-orange-500">
                      <i class="pi pi-clock mr-1"></i>
                      Follow-up: {{ note.follow_up_date ? new Date(note.follow_up_date).toLocaleDateString('vi-VN') : 'Chưa đặt ngày' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </TabPanel>

          <!-- Tab Hoạt động -->
          <TabPanel :value="2">
            <div class="mt-4">
              <div v-if="activitiesLoading" class="flex justify-center py-4"><ProgressSpinner /></div>
              <div v-else-if="activities.length === 0" class="card text-center py-8">
                <i class="pi pi-calendar text-4xl mb-3 block text-muted-color"></i>
                <p class="text-lg text-muted-color">Chưa check-in sự kiện nào</p>
              </div>
              <div v-else class="flex flex-col gap-3">
                <div v-for="(act, idx) in activities" :key="idx" class="card">
                  <div class="flex items-center gap-3 mb-2">
                    <span class="text-lg">{{ loaiHinhEventLabel[act.loai_hinh] || '📋' }}</span>
                    <span class="font-semibold">{{ act.ten_su_kien }}</span>
                  </div>
                  <div class="flex items-center gap-4 text-sm text-muted-color flex-wrap">
                    <span><i class="pi pi-clock mr-1"></i>{{ formatDateTime(act.thoi_gian_bat_dau) }}</span>
                    <span v-if="act.dia_diem"><i class="pi pi-map-marker mr-1"></i>{{ act.dia_diem }}</span>
                    <span><i class="pi pi-user mr-1"></i>Check-in bởi: {{ act.checked_in_by_name }}</span>
                  </div>
                </div>
              </div>
            </div>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>

    <!-- Dialog Ghi chú chăm sóc -->
    <Dialog v-model:visible="showCareDialog" header="📝 Ghi chú chăm sóc" modal :style="{ width: '520px' }">
      <div class="flex flex-col gap-4 pt-2">
        <div class="flex flex-col gap-2">
          <label class="font-medium">Hình thức <span class="text-red-500">*</span></label>
          <Select v-model="careForm.hinh_thuc" :options="hinhThucOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>

        <!-- Gắn sự kiện (tùy chọn) -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Gắn với sự kiện <span class="text-muted-color text-sm">(không bắt buộc)</span></label>
          <Select
            v-model="careForm.event_id"
            :options="[{ id: null, ten_su_kien: 'Không — Chăm sóc thường' }, ...events]"
            optionLabel="ten_su_kien"
            optionValue="id"
            class="w-full"
            showClear
          />
        </div>

        <!-- Trạng thái tham dự (chỉ hiện khi chọn sự kiện) -->
        <div v-if="careForm.event_id" class="flex flex-col gap-2">
          <label class="font-medium">Trạng thái tham dự <span class="text-red-500">*</span></label>
          <Select v-model="careForm.trang_thai_sk" :options="trangThaiSkOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-medium">Nội dung <span class="text-red-500">*</span></label>
          <Textarea v-model="careForm.noi_dung" rows="4" class="w-full" placeholder="Ghi nội dung cuộc trao đổi..." />
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-medium">Phản hồi của thành viên</label>
          <Select v-model="careForm.phan_hoi" :options="phanHoiOptions" optionLabel="label" optionValue="value"
            class="w-full" showClear placeholder="Chọn phản hồi (không bắt buộc)" />
        </div>

        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <Checkbox v-model="careForm.follow_up" :binary="true" inputId="follow_up" />
            <label for="follow_up">Cần follow-up</label>
          </div>
          <DatePicker v-if="careForm.follow_up" v-model="careForm.follow_up_date" dateFormat="dd/mm/yy"
            showIcon placeholder="Ngày follow-up" class="flex-1" />
        </div>
      </div>
      <template #footer>
        <Button label="Hủy" severity="secondary" text @click="showCareDialog = false" />
        <Button label="Lưu ghi chú" icon="pi pi-check" :loading="careSaving" @click="saveCareNote" />
      </template>
    </Dialog>

    <Toast />
  </div>
</template>
