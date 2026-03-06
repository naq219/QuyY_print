<script setup>
/**
 * ContactImportDialog — Import thành viên từ danh bạ điện thoại
 * - Contact Picker API (Android Chrome / Samsung Browser)
 * - Fallback rõ ràng cho iOS: hướng dẫn dùng Excel
 * - Normalize SĐT: giữ dấu +, loại ký tự lạ
 * - Đoán giới tính từ danh xưng trong tên
 * - Lọc trùng SĐT trong batch ngay trên frontend
 */

const props = defineProps({
  visible: { type: Boolean, default: false },
  groups: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:visible', 'import'])

const { apiFetch } = useApi()
const toast = useToast()

// ── State ─────────────────────────────────────────────────────────────────────
const contacts = ref([])
const importing = ref(false)
const importResult = ref(null)
const selectedGroupId = ref(null)
const picking = ref(false)

// Manual entry fallback
const showManual = ref(false)
const manualName = ref('')
const manualPhone = ref('')

// ── Platform detection ────────────────────────────────────────────────────────
const isContactPickerSupported = computed(() =>
  typeof window !== 'undefined' && 'contacts' in navigator && 'ContactsManager' in window
)

const isIOS = computed(() => {
  if (typeof window === 'undefined') return false
  const ua = navigator.userAgent || ''
  return /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
})

// ── Normalize phone ────────────────────────────────────────────────────────────
// Giữ dấu + ở đầu (mã quốc gia), loại bỏ mọi ký tự không phải số
const normalizePhone = (raw) => {
  if (!raw) return ''
  let p = String(raw).trim()
  // Giữ dấu + ở đầu nếu có
  const hasPlus = p.startsWith('+')
  // Loại bỏ tất cả ký tự không phải số
  p = p.replace(/[^\d]/g, '')
  // Thêm lại dấu + nếu ban đầu có
  if (hasPlus && p.length > 0) p = '+' + p
  return p
}

// Lấy số điện thoại tốt nhất từ danh sách tel của 1 contact
const getBestPhone = (phones) => {
  if (!phones || phones.length === 0) return ''
  // Normalize tất cả
  const normalized = phones.map(normalizePhone).filter(p => p.length >= 9)
  if (normalized.length === 0) return normalizePhone(phones[0])
  // Ưu tiên số VN di động (bắt đầu 0 hoặc +84)
  const vnMobile = normalized.find(p =>
    /^(0[35789]\d{8}|\+84[35789]\d{8})$/.test(p)
  )
  if (vnMobile) return vnMobile
  // Ưu tiên số bắt đầu bằng 0 (local)
  const local = normalized.find(p => p.startsWith('0'))
  if (local) return local
  // Ưu tiên số có dấu + (quốc tế)
  const intl = normalized.find(p => p.startsWith('+'))
  if (intl) return intl
  return normalized[0]
}

// ── Đoán giới tính từ danh xưng trong tên ──────────────────────────────────────
const FEMALE_PREFIXES = ['chị', 'chi', 'chj', 'cô', 'co', 'dì', 'di', 'gì', 'gi', 'tỉ', 'tỷ', 'ty', 'mẹ', 'me', 'mự', 'mu', 'bà', 'ba', 'thím', 'thim', 'mợ', 'mo', 'má', 'ma']
const MALE_PREFIXES = ['anh', 'ông', 'ong', 'chú', 'chu', 'bác', 'bac', 'thầy', 'thay', 'qt', 'quý thầy', 'quy thay', 'sư', 'su', 'đại đức', 'dai duc', 'thượng tọa', 'thuong toa']

const guessGender = (name) => {
  if (!name) return 'khong_xac_dinh'
  // Lowercase và bỏ dấu để so sánh linh hoạt hơn
  const lower = name.toLowerCase().trim()

  // Kiểm tra prefix: so sánh từ đầu tiên (hoặc 2 từ đầu) với danh sách
  for (const prefix of MALE_PREFIXES) {
    // Kiểm tra: tên bắt đầu bằng prefix + khoảng trắng hoặc dấu chấm
    if (lower.startsWith(prefix + ' ') || lower.startsWith(prefix + '.') || lower === prefix) {
      return 'nam'
    }
  }
  for (const prefix of FEMALE_PREFIXES) {
    if (lower.startsWith(prefix + ' ') || lower.startsWith(prefix + '.') || lower === prefix) {
      return 'nu'
    }
  }

  return 'khong_xac_dinh'
}

// ── Contact Picker API ─────────────────────────────────────────────────────────
const openContactPicker = async () => {
  if (!isContactPickerSupported.value) {
    toast.add({
      severity: 'info',
      summary: 'Không hỗ trợ',
      detail: 'Trình duyệt chưa hỗ trợ. Vui lòng nhập tay hoặc dùng Excel.',
      life: 4000
    })
    showManual.value = true
    return
  }

  picking.value = true
  try {
    const selected = await navigator.contacts.select(
      ['name', 'tel'],
      { multiple: true }
    )

    if (!selected || selected.length === 0) {
      picking.value = false
      return
    }

    // Normalize và thêm vào danh sách
    // Lọc trùng SĐT ngay trong danh sách hiện có
    const existingPhones = new Set(contacts.value.map(c => c.phone))
    let added = 0
    let skippedDup = 0

    for (const contact of selected) {
      const name = (contact.name?.[0] || '').trim()
      const phone = getBestPhone(contact.tel || [])

      if (!name && !phone) continue

      // Lọc trùng trong batch
      if (phone && existingPhones.has(phone)) {
        skippedDup++
        continue
      }

      const gioi_tinh = guessGender(name)

      const item = {
        ho_ten: name,
        phone,
        gioi_tinh,
        _valid: !!(name && phone && phone.length >= 9),
        _error: !name ? 'Chưa có tên' : !phone ? 'Chưa có SĐT' : phone.length < 9 ? 'SĐT không hợp lệ' : '',
        _editing: false
      }

      contacts.value.push(item)
      if (phone) existingPhones.add(phone)
      added++
    }

    let msg = `${added} liên lạc từ danh bạ`
    if (skippedDup > 0) msg += ` (bỏ qua ${skippedDup} trùng SĐT)`
    if (added > 0 || skippedDup > 0) {
      toast.add({ severity: 'success', summary: 'Đã chọn', detail: msg, life: 3000 })
    }
  } catch (e) {
    if (e.name !== 'AbortError') {
      toast.add({ severity: 'error', summary: 'Lỗi', detail: 'Không thể mở danh bạ', life: 3000 })
    }
  }
  picking.value = false
}

// ── Manual entry ──────────────────────────────────────────────────────────────
const addManual = () => {
  const name = manualName.value.trim()
  const phone = normalizePhone(manualPhone.value)

  if (!name) {
    toast.add({ severity: 'warn', summary: 'Thiếu tên', detail: 'Vui lòng nhập họ tên', life: 2000 })
    return
  }
  if (!phone || phone.length < 9) {
    toast.add({ severity: 'warn', summary: 'SĐT không hợp lệ', detail: 'Vui lòng nhập số điện thoại hợp lệ', life: 2000 })
    return
  }

  // Lọc trùng
  if (contacts.value.some(c => c.phone === phone)) {
    toast.add({ severity: 'warn', summary: 'Trùng SĐT', detail: `${phone} đã có trong danh sách`, life: 2500 })
    return
  }

  contacts.value.push({
    ho_ten: name,
    phone,
    gioi_tinh: guessGender(name),
    _valid: true,
    _error: '',
    _editing: false
  })

  manualName.value = ''
  manualPhone.value = ''
}

// ── Edit inline ────────────────────────────────────────────────────────────────
const startEdit = (item) => { item._editing = true }

const finishEdit = (item) => {
  item._editing = false
  item.phone = normalizePhone(item.phone)
  item.gioi_tinh = guessGender(item.ho_ten)
  item._valid = !!(item.ho_ten && item.phone && item.phone.length >= 9)
  item._error = !item.ho_ten ? 'Chưa có tên' : !item.phone ? 'Chưa có SĐT' : item.phone.length < 9 ? 'SĐT không hợp lệ' : ''
}

const removeContact = (index) => {
  contacts.value.splice(index, 1)
}

// ── Giới tính display ─────────────────────────────────────────────────────────
const gioiTinhLabel = (gt) => {
  if (gt === 'nam') return '♂'
  if (gt === 'nu') return '♀'
  return '?'
}
const gioiTinhClass = (gt) => {
  if (gt === 'nam') return 'text-blue-500'
  if (gt === 'nu') return 'text-pink-500'
  return 'text-muted-color'
}

// ── Stats ─────────────────────────────────────────────────────────────────────
const validCount = computed(() => contacts.value.filter(c => c._valid).length)
const invalidCount = computed(() => contacts.value.filter(c => !c._valid).length)

// ── Submit import ──────────────────────────────────────────────────────────────
const submitImport = async () => {
  const validRows = contacts.value.filter(c => c._valid)
  if (validRows.length === 0) {
    toast.add({ severity: 'warn', summary: 'Không có dữ liệu', detail: 'Không có liên lạc hợp lệ để thêm', life: 3000 })
    return
  }

  importing.value = true
  try {
    const members = validRows.map(c => ({
      ho_ten: c.ho_ten.trim(),
      phone: c.phone,
      gioi_tinh: c.gioi_tinh || 'khong_xac_dinh',
      group_id: selectedGroupId.value || null
    }))

    const result = await apiFetch('/api/members/import', {
      method: 'POST',
      body: { members }
    })

    importResult.value = result.data

    if (result.data.imported > 0) {
      toast.add({
        severity: 'success',
        summary: 'Thêm thành công',
        detail: `Đã thêm ${result.data.imported}/${result.data.total} thành viên`,
        life: 5000
      })
    }

    if (result.data.failed > 0) {
      toast.add({
        severity: 'warn',
        summary: 'Một số liên lạc bị bỏ qua',
        detail: `${result.data.failed} liên lạc không thêm được (trùng hoặc lỗi)`,
        life: 5000
      })
    }

    emit('import', result.data)
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Thêm thất bại', life: 3000 })
  }
  importing.value = false
}

// ── Close / reset ──────────────────────────────────────────────────────────────
const close = () => {
  if (importing.value) return
  emit('update:visible', false)
}

const reset = () => {
  contacts.value = []
  importing.value = false
  importResult.value = null
  selectedGroupId.value = null
  showManual.value = false
  manualName.value = ''
  manualPhone.value = ''
}

watch(() => props.visible, (val) => {
  if (!val) reset()
})
</script>

<template>
  <Dialog
    :visible="visible"
    @update:visible="close"
    modal
    header="📱 Thêm từ danh bạ điện thoại"
    :style="{ width: '95vw', maxWidth: '600px' }"
    :closable="!importing"
  >
    <!-- ── Chưa có kết quả import ── -->
    <div v-if="!importResult">

      <!-- ═══ iOS Fallback: Hướng dẫn chuyển sang Excel ═══ -->
      <div
        v-if="isIOS"
        class="mb-4 p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800"
      >
        <div class="flex items-start gap-3">
          <div class="text-3xl">🍎</div>
          <div class="flex-1">
            <p class="font-semibold text-amber-800 dark:text-amber-200 mb-1">iPhone/iPad không hỗ trợ chọn danh bạ qua web</p>
            <p class="text-sm text-amber-700 dark:text-amber-400 mb-2">
              Do hạn chế của Apple, trình duyệt trên iOS không thể truy cập danh bạ.
              Bạn có thể dùng <strong>2 cách thay thế</strong>:
            </p>
            <ol class="text-sm text-amber-700 dark:text-amber-400 list-decimal list-inside space-y-1 mb-3">
              <li>Nhập tay từng người bằng form bên dưới</li>
              <li>Xuất danh bạ ra file Excel rồi dùng tính năng <strong>"Import Excel"</strong> ở trang thêm thành viên</li>
            </ol>
            <Button
              label="Nhập tay từng người"
              icon="pi pi-plus"
              size="small"
              severity="warn"
              @click="showManual = true"
            />
          </div>
        </div>
      </div>

      <!-- ═══ Nút chọn từ danh bạ (Android) ═══ -->
      <div v-else class="mb-4">
        <div
          v-if="isContactPickerSupported"
          class="flex flex-col items-center gap-3 p-5 rounded-xl border-2 border-dashed border-primary/40 bg-primary/5 mb-3"
        >
          <i class="pi pi-address-book text-4xl text-primary"></i>
          <div class="text-center">
            <p class="font-semibold text-surface-800 dark:text-surface-100">Chọn từ danh bạ</p>
            <p class="text-sm text-muted-color mt-0.5">Mở danh bạ để chọn nhiều người cùng lúc</p>
          </div>
          <Button
            label="Mở danh bạ"
            icon="pi pi-address-book"
            :loading="picking"
            @click="openContactPicker"
            size="large"
          />
        </div>

        <!-- Desktop / trình duyệt không hỗ trợ -->
        <div
          v-else
          class="flex items-start gap-3 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 mb-3"
        >
          <i class="pi pi-info-circle text-blue-500 mt-0.5"></i>
          <div class="flex-1 text-sm">
            <p class="font-medium text-blue-800 dark:text-blue-300">Mở trang này trên điện thoại Android</p>
            <p class="text-blue-700 dark:text-blue-400 mt-0.5">
              Chức năng chọn danh bạ yêu cầu <strong>Chrome trên Android</strong>.
              Trên máy tính, bạn có thể nhập tay hoặc dùng Import Excel.
            </p>
          </div>
        </div>
      </div>

      <!-- ═══ Nút nhập tay (hiện cho mọi nền tảng) ═══ -->
      <div v-if="!isIOS" class="flex gap-2 justify-center mb-3">
        <Button
          :label="showManual ? 'Ẩn nhập tay' : '+ Thêm thủ công'"
          :icon="showManual ? 'pi pi-chevron-up' : 'pi pi-plus'"
          severity="secondary"
          text
          size="small"
          @click="showManual = !showManual"
        />
      </div>

      <!-- ═══ Form nhập tay ═══ -->
      <Transition name="slide-down">
        <div v-show="showManual" class="mb-4 p-3 rounded-lg bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-600">
          <p class="text-sm font-medium mb-3 text-muted-color">Nhập liên lạc thủ công:</p>
          <div class="flex gap-2 flex-col sm:flex-row">
            <InputText
              v-model="manualName"
              placeholder="Họ và tên *"
              class="flex-1"
              @keydown.enter="addManual"
            />
            <InputText
              v-model="manualPhone"
              placeholder="Số điện thoại *"
              inputmode="tel"
              class="flex-1"
              @keydown.enter="addManual"
            />
            <Button
              icon="pi pi-plus"
              @click="addManual"
              :disabled="!manualName || !manualPhone"
            />
          </div>
        </div>
      </Transition>

      <!-- ═══ Danh sách đã chọn ═══ -->
      <div v-if="contacts.length > 0">
        <!-- Header stats -->
        <div class="flex items-center justify-between mb-3">
          <div class="flex gap-2 flex-wrap">
            <Tag :value="`${contacts.length} liên lạc`" severity="info" />
            <Tag :value="`${validCount} hợp lệ`" severity="success" />
            <Tag v-if="invalidCount" :value="`${invalidCount} lỗi`" severity="danger" />
          </div>
          <Button
            icon="pi pi-trash"
            label="Xóa hết"
            severity="danger"
            text
            size="small"
            @click="contacts = []"
          />
        </div>

        <!-- Chọn nhóm -->
        <div class="mb-3">
          <label class="text-sm font-medium mb-1.5 block">Nhóm (áp dụng cho tất cả):</label>
          <Select
            v-model="selectedGroupId"
            :options="groups"
            optionLabel="ten_nhom"
            optionValue="id"
            class="w-full"
            placeholder="Không phân nhóm"
            showClear
          />
        </div>

        <!-- Thêm từ danh bạ nếu muốn bổ sung -->
        <div v-if="isContactPickerSupported && !isIOS" class="mb-3 text-center">
          <Button
            label="+ Chọn thêm từ danh bạ"
            icon="pi pi-address-book"
            severity="secondary"
            text
            size="small"
            :loading="picking"
            @click="openContactPicker"
          />
        </div>

        <!-- Danh sách -->
        <div class="overflow-auto max-h-64 border border-surface-200 dark:border-surface-600 rounded-lg">
          <div
            v-for="(c, i) in contacts"
            :key="i"
            class="flex items-center gap-2 px-3 py-2 border-b border-surface-100 dark:border-surface-700 last:border-0"
            :class="c._valid ? '' : 'bg-red-50 dark:bg-red-900/10'"
          >
            <!-- Avatar chữ cái + giới tính -->
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 relative"
              :class="c._valid ? 'bg-primary/20 text-primary' : 'bg-red-100 dark:bg-red-900/30 text-red-500'"
            >
              {{ c.ho_ten?.[0]?.toUpperCase() || '?' }}
              <span
                class="absolute -bottom-0.5 -right-0.5 text-[0.55rem] leading-none"
                :class="gioiTinhClass(c.gioi_tinh)"
              >{{ gioiTinhLabel(c.gioi_tinh) }}</span>
            </div>

            <!-- Nội dung -->
            <div v-if="!c._editing" class="flex-1 min-w-0 cursor-pointer" @click="startEdit(c)">
              <p class="text-sm font-medium leading-tight truncate">{{ c.ho_ten || '(Chưa có tên)' }}</p>
              <p class="text-xs text-muted-color">{{ c.phone || '(Chưa có SĐT)' }}</p>
            </div>

            <!-- Edit inline -->
            <div v-else class="flex-1 flex gap-1.5">
              <InputText v-model="c.ho_ten" placeholder="Họ tên" class="flex-1 !text-sm !py-1" @keydown.enter="finishEdit(c)" @blur="finishEdit(c)" />
              <InputText v-model="c.phone" placeholder="SĐT" inputmode="tel" class="w-28 !text-sm !py-1" @keydown.enter="finishEdit(c)" @blur="finishEdit(c)" />
            </div>

            <!-- Status + actions -->
            <div class="flex items-center gap-0.5 shrink-0">
              <Tag v-if="c._valid" value="OK" severity="success" class="!text-xs !py-0 !px-1.5" />
              <Tag v-else :value="c._error || 'Lỗi'" severity="danger" class="!text-xs !py-0 !px-1.5" />
              <Button icon="pi pi-pencil" text rounded severity="secondary" size="small" class="!w-7 !h-7" @click="startEdit(c)" v-tooltip.left="'Sửa'" />
              <Button icon="pi pi-times" text rounded severity="danger" size="small" class="!w-7 !h-7" @click="removeContact(i)" v-tooltip.left="'Xóa'" />
            </div>
          </div>
        </div>

        <!-- Gợi ý -->
        <p v-if="invalidCount" class="text-xs text-muted-color mt-2">
          <i class="pi pi-info-circle mr-1"></i>
          Nhấn vào dòng lỗi để sửa thông tin, hoặc nhấn ✕ để xóa.
        </p>
      </div>

      <!-- Empty state -->
      <div v-else-if="!isIOS || showManual" class="text-center py-6 text-muted-color text-sm">
        <i class="pi pi-users text-3xl mb-2 block opacity-40"></i>
        Chưa có liên lạc nào được chọn
      </div>
    </div>

    <!-- ═══ Kết quả import ═══ -->
    <div v-else class="text-center py-6">
      <i class="pi pi-check-circle text-5xl text-green-500 mb-4 block"></i>
      <h3 class="text-xl font-bold mb-3">Hoàn tất!</h3>
      <div class="flex justify-center gap-6 mb-4">
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600">{{ importResult.imported }}</div>
          <div class="text-sm text-muted-color">Đã thêm</div>
        </div>
        <div v-if="importResult.failed" class="text-center">
          <div class="text-3xl font-bold text-orange-500">{{ importResult.failed }}</div>
          <div class="text-sm text-muted-color">Bỏ qua</div>
        </div>
      </div>

      <!-- Chi tiết lỗi / bỏ qua -->
      <div v-if="importResult.errors?.length" class="text-left mt-4 bg-orange-50 dark:bg-orange-900/10 rounded-lg p-3">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-400 mb-2">
          <i class="pi pi-info-circle mr-1"></i>Chi tiết bỏ qua:
        </p>
        <div class="overflow-auto max-h-40">
          <div v-for="err in importResult.errors" :key="err.row" class="text-xs mb-1 flex gap-1">
            <span class="font-medium text-surface-700 dark:text-surface-200 shrink-0">{{ err.ho_ten }}:</span>
            <span class="text-orange-600 dark:text-orange-400">{{ err.error }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ Footer ═══ -->
    <template #footer>
      <template v-if="!importResult">
        <Button label="Hủy" severity="secondary" text @click="close" :disabled="importing" />
        <Button
          :label="validCount > 0 ? `Thêm ${validCount} thành viên` : 'Thêm'"
          icon="pi pi-user-plus"
          :loading="importing"
          :disabled="validCount === 0"
          @click="submitImport"
        />
      </template>
      <template v-else>
        <Button label="Xong" icon="pi pi-check" @click="close" />
      </template>
    </template>
  </Dialog>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
  max-height: 200px;
}
.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
