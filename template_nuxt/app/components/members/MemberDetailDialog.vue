<script setup>
/**
 * MemberDetailDialog — Hiển thị chi tiết thành viên trong dialog
 * Thay vì chuyển trang, show dialog ngay tại list
 */
const props = defineProps({
  visible: { type: Boolean, default: false },
  memberId: { type: String, default: null }
})

const emit = defineEmits(['update:visible', 'care', 'updated'])
const { apiFetch } = useApi()
const toast = useToast()

const member = ref(null)
const loading = ref(false)
const careNotes = ref([])
const careLoading = ref(false)
const activeTab = ref('info') // 'info' | 'care'

// Edit mode
const editMode = ref(false)
const editForm = ref({})
const groups = ref([])
const saving = ref(false)

// === Labels ===
const statusSeverity = { active: 'success', paused: 'warn', left: 'danger' }
const statusLabel = { active: 'Hoạt động', paused: 'Tạm nghỉ', left: 'Đã rời' }
const gioiTinhOptions = [{ label: 'Nam', value: 'nam' }, { label: 'Nữ', value: 'nu' }, { label: 'Chưa xác định', value: 'khong_xac_dinh' }]
const statusOptions = [
  { label: 'Đang hoạt động', value: 'active' },
  { label: 'Tạm nghỉ', value: 'paused' },
  { label: 'Đã rời nhóm', value: 'left' }
]
const hinhThucLabel = {
  call: '📞', message: '💬', visit: '🏠', gift: '🎁', other: '📋'
}
const phanHoiLabel = {
  happy: '🥰', normal: '😊', need_help: '😟', no_contact: '📵'
}
const trangThaiSkLabel = {
  chua_lien_lac: '📵 Chưa LH',
  se_tham_gia: '✅ Sẽ đến',
  khong_tham_gia: '❌ Không đến',
  da_tham_gia: '🎯 Đã đến'
}
const trangThaiSkSeverity = {
  chua_lien_lac: 'secondary',
  se_tham_gia: 'success',
  khong_tham_gia: 'danger',
  da_tham_gia: 'info'
}

const formatPhoneForZalo = (phone) => phone?.startsWith('0') ? '84' + phone.slice(1) : phone

const formatDateTime = (dt) => {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleDateString('vi-VN') + ' ' + d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
}

// === Load ===
const loadMember = async () => {
  if (!props.memberId) return
  loading.value = true
  try {
    const data = await apiFetch(`/api/members/${props.memberId}`)
    member.value = data.data
  } catch {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: 'Không tải được thông tin', life: 3000 })
  }
  loading.value = false
}

const loadCareNotes = async () => {
  if (!props.memberId) return
  careLoading.value = true
  try {
    const data = await apiFetch(`/api/care-notes?member_id=${props.memberId}`)
    careNotes.value = data.data || []
  } catch {}
  careLoading.value = false
}

const loadGroups = async () => {
  try { groups.value = (await apiFetch('/api/groups')).data } catch {}
}

// === Edit ===
const startEdit = () => {
  editForm.value = { ...member.value }
  editMode.value = true
  loadGroups()
}

const saveEdit = async () => {
  saving.value = true
  try {
    await apiFetch(`/api/members/${props.memberId}`, { method: 'PUT', body: editForm.value })
    toast.add({ severity: 'success', summary: 'Đã lưu', detail: 'Cập nhật thành công', life: 2000 })
    editMode.value = false
    loadMember()
    emit('updated')
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Cập nhật thất bại', life: 3000 })
  }
  saving.value = false
}

const deleteCareNote = async (note) => {
  if (!confirm('Xóa ghi chú này?')) return
  try {
    await apiFetch(`/api/care-notes/${note.id}`, { method: 'DELETE' })
    toast.add({ severity: 'success', summary: 'Đã xóa', life: 2000 })
    loadCareNotes()
    emit('updated')
  } catch {}
}

const deleteMember = async () => {
  if (!confirm(`Xóa "${member.value?.ho_ten}"?`)) return
  try {
    await apiFetch(`/api/members/${props.memberId}`, { method: 'DELETE' })
    emit('update:visible', false)
    emit('updated')
  } catch {}
}

// Watch visible → load data
watch(() => props.visible, (val) => {
  if (val && props.memberId) {
    activeTab.value = 'info'
    editMode.value = false
    member.value = null
    careNotes.value = []
    loadMember()
    loadCareNotes()
  }
})

const openCare = () => {
  if (member.value) emit('care', member.value)
}
</script>

<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    modal
    :style="{ width: '95vw', maxWidth: '520px' }"
    :pt="{ content: { class: '!px-3 !py-0' }, header: { class: 'pb-1' } }"
    class="member-detail-dialog"
  >
    <template #header>
      <div class="flex items-center gap-2 min-w-0 flex-1">
        <i class="pi pi-user text-primary text-sm flex-shrink-0"></i>
        <span class="font-semibold text-sm truncate">Chi tiết thành viên</span>
      </div>
    </template>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-10">
      <ProgressSpinner style="width: 40px; height: 40px" />
    </div>

    <div v-else-if="member" class="flex flex-col gap-3 pb-3">
      <!-- ── HEADER: Tên + Trạng thái + Actions ──────────────── -->
      <div class="flex items-start gap-3 pt-2">
        <div class="w-11 h-11 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
          <i class="pi pi-user text-primary text-lg"></i>
        </div>
        <div class="min-w-0 flex-1">
          <p class="font-bold text-base leading-tight">{{ member.ho_ten }}</p>
          <p v-if="member.phap_danh" class="text-xs text-muted-color">PD: {{ member.phap_danh }}</p>
          <div class="flex items-center gap-1.5 mt-1 flex-wrap">
            <Tag v-if="member.group_name" :value="member.group_name" severity="info" class="!text-[0.6rem] !py-0 !px-1.5" />
            <Tag :value="statusLabel[member.trang_thai]" :severity="statusSeverity[member.trang_thai]" class="!text-[0.6rem] !py-0 !px-1.5" />
          </div>
        </div>
        <!-- Action buttons -->
        <div class="flex gap-0.5 flex-shrink-0">
          <Button icon="pi pi-pencil" text rounded severity="info" size="small" class="!w-9 !h-9" @click="startEdit" title="Sửa" />
          <Button icon="pi pi-comment" text rounded severity="warn" size="small" class="!w-9 !h-9" @click="openCare" title="Ghi chú CS" />
          <Button icon="pi pi-trash" text rounded severity="danger" size="small" class="!w-9 !h-9" @click="deleteMember" title="Xóa" />
        </div>
      </div>

      <!-- ── CONTACT: SĐT + Gọi / Zalo ──────────────────────── -->
      <div v-if="member.phone" class="flex items-center gap-3 px-2 py-2 bg-surface-50 dark:bg-surface-800 rounded-lg">
        <span class="text-sm font-medium flex-1">{{ member.phone }}</span>
        <a :href="`tel:${member.phone}`" @click.stop>
          <Button icon="pi pi-phone" text rounded severity="success" size="small" class="!w-10 !h-10" />
        </a>
        <a :href="`https://zalo.me/${formatPhoneForZalo(member.phone)}`" target="_blank" @click.stop>
          <Button text rounded size="small" class="!w-10 !h-10 !text-blue-600 !font-bold">
            <template #icon><span class="text-[0.6rem] font-bold">Zalo</span></template>
          </Button>
        </a>
      </div>
      <div v-else class="flex items-center gap-3 px-2 py-2 bg-orange-50 dark:bg-orange-900/10 rounded-lg">
        <span class="text-sm text-orange-500 italic flex-1"><i class="pi pi-exclamation-circle mr-1"></i>Chưa có số điện thoại</span>
      </div>

      <!-- ── TABS: Info / Lịch sử CS ─────────────────────────── -->
      <div class="flex border-b border-surface-200 dark:border-surface-700">
        <button
          class="flex-1 py-2 text-xs font-medium text-center transition-colors border-b-2"
          :class="activeTab === 'info' ? 'border-primary text-primary' : 'border-transparent text-muted-color hover:text-surface-700'"
          @click="activeTab = 'info'"
        >
          <i class="pi pi-id-card mr-1"></i>Thông tin
        </button>
        <button
          class="flex-1 py-2 text-xs font-medium text-center transition-colors border-b-2"
          :class="activeTab === 'care' ? 'border-primary text-primary' : 'border-transparent text-muted-color hover:text-surface-700'"
          @click="activeTab = 'care'"
        >
          <i class="pi pi-comments mr-1"></i>Lịch sử CS
          <span v-if="careNotes.length" class="ml-1 px-1.5 py-0.5 rounded-full bg-primary/10 text-primary text-[0.6rem]">{{ careNotes.length }}</span>
        </button>
      </div>

      <!-- ── TAB: Thông tin ───────────────────────────────────── -->
      <div v-if="activeTab === 'info' && !editMode" class="flex flex-col gap-2">
        <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
          <div class="text-muted-color">Giới tính</div>
          <div class="font-medium text-right">{{ member.gioi_tinh === 'nam' ? 'Nam' : member.gioi_tinh === 'nu' ? 'Nữ' : 'Chưa xác định' }}</div>

          <div class="text-muted-color">Năm sinh</div>
          <div class="font-medium text-right">{{ member.ngay_sinh || '—' }}</div>

          <div v-if="member.phone2" class="text-muted-color">SĐT phụ</div>
          <div v-if="member.phone2" class="font-medium text-right">{{ member.phone2 }}</div>

          <div class="text-muted-color">Tỉnh/TP</div>
          <div class="font-medium text-right">{{ member.tinh_tp || '—' }}</div>

          <div v-if="member.xa_phuong" class="text-muted-color">Xã/Phường</div>
          <div v-if="member.xa_phuong" class="font-medium text-right">{{ member.xa_phuong }}</div>

          <div v-if="member.dia_chi" class="text-muted-color">Địa chỉ</div>
          <div v-if="member.dia_chi" class="font-medium text-right">{{ member.dia_chi }}</div>

          <div class="text-muted-color">Gia nhập</div>
          <div class="font-medium text-right">{{ member.ngay_gia_nhap ? new Date(member.ngay_gia_nhap).toLocaleDateString('vi-VN') : '—' }}</div>

          <div v-if="member.cong_viec" class="text-muted-color">Công việc</div>
          <div v-if="member.cong_viec" class="font-medium text-right">{{ member.cong_viec }}</div>

          <div v-if="member.suc_khoe" class="text-muted-color">Sức khỏe</div>
          <div v-if="member.suc_khoe" class="font-medium text-right">{{ member.suc_khoe }}</div>

          <div v-if="member.nguoi_gioi_thieu" class="text-muted-color">Người giới thiệu</div>
          <div v-if="member.nguoi_gioi_thieu" class="font-medium text-right">{{ member.nguoi_gioi_thieu }}</div>
        </div>
        <div v-if="member.ghi_chu" class="mt-1 p-2 bg-surface-50 dark:bg-surface-800 rounded-lg">
          <div class="text-xs text-muted-color mb-1">Ghi chú</div>
          <div class="text-sm whitespace-pre-wrap">{{ member.ghi_chu }}</div>
        </div>
      </div>

      <!-- ── TAB: Edit info ───────────────────────────────────── -->
      <div v-if="activeTab === 'info' && editMode" class="flex flex-col gap-2">
        <div class="grid grid-cols-2 gap-2">
          <div class="col-span-2"><label class="text-xs font-medium mb-1 block">Họ tên *</label><InputText v-model="editForm.ho_ten" class="w-full" size="small" /></div>
          <div><label class="text-xs font-medium mb-1 block">Pháp danh</label><InputText v-model="editForm.phap_danh" class="w-full" size="small" /></div>
          <div><label class="text-xs font-medium mb-1 block">Giới tính</label><Select v-model="editForm.gioi_tinh" :options="gioiTinhOptions" optionLabel="label" optionValue="value" class="w-full" size="small" /></div>
          <div><label class="text-xs font-medium mb-1 block">Năm sinh</label><InputText v-model="editForm.ngay_sinh" class="w-full" size="small" /></div>
          <div><label class="text-xs font-medium mb-1 block">Nhóm</label><Select v-model="editForm.group_id" :options="groups" optionLabel="ten_nhom" optionValue="id" class="w-full" size="small" /></div>
          <div><label class="text-xs font-medium mb-1 block">SĐT</label><InputText v-model="editForm.phone" class="w-full" size="small" /></div>
          <div><label class="text-xs font-medium mb-1 block">Trạng thái</label><Select v-model="editForm.trang_thai" :options="statusOptions" optionLabel="label" optionValue="value" class="w-full" size="small" /></div>
          <div><label class="text-xs font-medium mb-1 block">Tỉnh/TP</label><InputText v-model="editForm.tinh_tp" class="w-full" size="small" /></div>
          <div><label class="text-xs font-medium mb-1 block">Xã/Phường</label><InputText v-model="editForm.xa_phuong" class="w-full" size="small" /></div>
          <div class="col-span-2"><label class="text-xs font-medium mb-1 block">Địa chỉ</label><InputText v-model="editForm.dia_chi" class="w-full" size="small" /></div>
          <div class="col-span-2"><label class="text-xs font-medium mb-1 block">Ghi chú</label><Textarea v-model="editForm.ghi_chu" rows="2" class="w-full" /></div>
        </div>
        <div class="flex justify-end gap-2 pt-1">
          <Button label="Hủy" severity="secondary" text size="small" @click="editMode = false" />
          <Button label="Lưu" icon="pi pi-check" size="small" :loading="saving" @click="saveEdit" />
        </div>
      </div>

      <!-- ── TAB: Lịch sử chăm sóc ───────────────────────────── -->
      <div v-if="activeTab === 'care'" class="flex flex-col gap-2" style="max-height: 50vh; overflow-y: auto">
        <div v-if="careLoading" class="flex justify-center py-6">
          <ProgressSpinner style="width: 30px; height: 30px" />
        </div>
        <div v-else-if="careNotes.length === 0" class="text-center py-6 text-muted-color text-sm">
          <i class="pi pi-comments text-2xl block mb-2"></i>
          Chưa có ghi chú chăm sóc
        </div>
        <div
          v-else
          v-for="note in careNotes" :key="note.id"
          class="p-2.5 rounded-lg border border-surface-100 dark:border-surface-700 text-sm"
        >
          <div class="flex items-center justify-between gap-2 mb-1">
            <div class="flex items-center gap-1.5 flex-wrap min-w-0">
              <span>{{ hinhThucLabel[note.hinh_thuc] || '📋' }}</span>
              <span class="text-[0.65rem] text-muted-color">{{ formatDateTime(note.thoi_gian) }}</span>
              <Tag v-if="note.ten_su_kien"
                :value="'🗓 ' + note.ten_su_kien"
                severity="info" class="!text-[0.55rem] !py-0 !px-1" />
              <Tag v-if="note.trang_thai_sk"
                :value="trangThaiSkLabel[note.trang_thai_sk]"
                :severity="trangThaiSkSeverity[note.trang_thai_sk]"
                class="!text-[0.55rem] !py-0 !px-1" />
              <span v-if="note.phan_hoi" class="text-sm">{{ phanHoiLabel[note.phan_hoi] }}</span>
            </div>
            <Button icon="pi pi-times" text rounded severity="danger" size="small"
              class="!w-6 !h-6" @click="deleteCareNote(note)" />
          </div>
          <div class="text-sm leading-relaxed">{{ note.noi_dung }}</div>
          <div v-if="note.follow_up" class="text-xs text-orange-500 mt-1">
            <i class="pi pi-clock mr-0.5"></i>
            Follow-up: {{ note.follow_up_date ? new Date(note.follow_up_date).toLocaleDateString('vi-VN') : 'Chưa đặt ngày' }}
          </div>
          <div v-if="note.created_by_name" class="text-[0.6rem] text-muted-color mt-1">
            bởi {{ note.created_by_name }}
          </div>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<style scoped>
.member-detail-dialog :deep(.p-dialog-content) {
  max-height: 75vh;
  overflow-y: auto;
}
</style>
