<script setup>
import * as XLSX from 'xlsx'

const { apiFetch } = useApi()
const toast = useToast()
const router = useRouter()

const groups = ref([])
const saving = ref(false)
const showMore = ref(false)

const defaultForm = () => ({
  ho_ten: '', phone: '', phap_danh: '', gioi_tinh: 'khong_xac_dinh',
  ngay_sinh_text: '',
  group_id: null, ghi_chu: '',
  phone2: '', zalo_fb: '',
  tinh_tp: '', xa_phuong: '', dia_chi: '',
  cong_viec: '', suc_khoe: '', ky_nang: '',
  nguoi_gioi_thieu: ''
})

const form = ref({ ...defaultForm() })

// === Import Excel ===
const showImportDialog = ref(false)
const importData = ref([])
const importing = ref(false)
const importResult = ref(null)
const fileInput = ref(null)

// === Import từ Danh bạ ===
const showContactDialog = ref(false)

const onContactImport = (result) => {
  if (result?.imported > 0) {
    // Navigate sang danh sách sau khi import xong
    setTimeout(() => router.push('/members'), 1500)
  }
}

const loadGroups = async () => {
  try {
    const data = await apiFetch('/api/groups')
    groups.value = data.data
  } catch {}
}

// === Xử lý ngày sinh text ===
// Chấp nhận: "1990", "02/1990", "01/02/1990", "1/2/1990"
// Auto-pad: 1/2/1990 → 01/02/1990
// Chỉ năm: 1990 → giữ nguyên "1990"
const formatDateInput = () => {
  let val = form.value.ngay_sinh_text.trim()
  if (!val) return
  val = val.replace(/[-\.]/g, '/')
  const parts = val.split('/')
  if (parts.length === 3) {
    // dd/mm/yyyy
    const dd = parts[0].padStart(2, '0')
    const mm = parts[1].padStart(2, '0')
    const yyyy = parts[2].length === 2 ? '19' + parts[2] : parts[2]
    form.value.ngay_sinh_text = `${dd}/${mm}/${yyyy}`
  } else if (parts.length === 2) {
    // mm/yyyy
    const mm = parts[0].padStart(2, '0')
    const yyyy = parts[1].length === 2 ? '19' + parts[1] : parts[1]
    form.value.ngay_sinh_text = `${mm}/${yyyy}`
  }
  // Nếu chỉ 4 số → giữ nguyên (năm sinh)
}

// Validate: trả về text chuẩn hóa hoặc null
const parseNgaySinh = (text) => {
  if (!text) return null
  text = String(text).trim().replace(/[-\.]/g, '/')
  const parts = text.split('/')

  if (parts.length === 1) {
    // Chỉ năm: "1990"
    const yyyy = parseInt(parts[0])
    if (isNaN(yyyy) || yyyy < 1900 || yyyy > 2030) return null
    return String(yyyy)
  }
  if (parts.length === 2) {
    // mm/yyyy
    const mm = parseInt(parts[0])
    const yyyy = parseInt(parts[1].length === 2 ? '19' + parts[1] : parts[1])
    if (isNaN(mm) || isNaN(yyyy)) return null
    if (mm < 1 || mm > 12 || yyyy < 1900 || yyyy > 2030) return null
    return `${String(mm).padStart(2, '0')}/${yyyy}`
  }
  if (parts.length === 3) {
    // dd/mm/yyyy
    const dd = parseInt(parts[0])
    const mm = parseInt(parts[1])
    const yyyy = parseInt(parts[2].length === 2 ? '19' + parts[2] : parts[2])
    if (isNaN(dd) || isNaN(mm) || isNaN(yyyy)) return null
    if (dd < 1 || dd > 31 || mm < 1 || mm > 12 || yyyy < 1900 || yyyy > 2030) return null
    return `${String(dd).padStart(2, '0')}/${String(mm).padStart(2, '0')}/${yyyy}`
  }
  return null
}

const normalizePhone = (phone) => {
  if (!phone) return ''
  let p = String(phone).replace(/[\s\-\.]/g, '')
  if (p.startsWith('84') && p.length > 9) p = '0' + p.slice(2)
  return p
}

const saveMember = async () => {
  if (!form.value.ho_ten) {
    toast.add({ severity: 'warn', summary: 'Thiếu thông tin', detail: 'Vui lòng nhập họ tên', life: 3000 })
    return
  }



  formatDateInput()
  const ngay_sinh = parseNgaySinh(form.value.ngay_sinh_text)
  if (form.value.ngay_sinh_text && !ngay_sinh) {
    toast.add({ severity: 'warn', summary: 'Sai định dạng', detail: 'Nhập ngày sinh: 1990 hoặc 01/02/1990', life: 4000 })
    return
  }

  saving.value = true
  try {
    const payload = {
      ho_ten: form.value.ho_ten, phone: form.value.phone,
      phap_danh: form.value.phap_danh || null, gioi_tinh: form.value.gioi_tinh,
      ngay_sinh: ngay_sinh || null,
      group_id: form.value.group_id || null, ghi_chu: form.value.ghi_chu || null,
      phone2: form.value.phone2 || null, zalo_fb: form.value.zalo_fb || null,
      tinh_tp: form.value.tinh_tp || null, xa_phuong: form.value.xa_phuong || null,
      dia_chi: form.value.dia_chi || null, cong_viec: form.value.cong_viec || null,
      suc_khoe: form.value.suc_khoe || null, ky_nang: form.value.ky_nang || null,
      nguoi_gioi_thieu: form.value.nguoi_gioi_thieu || null
    }
    await apiFetch('/api/members', { method: 'POST', body: payload })
    toast.add({ severity: 'success', summary: 'Thành công', detail: `Đã thêm ${form.value.ho_ten}. Bạn có thể tiếp tục thêm người mới.`, life: 4000 })
    // Reset form để tạo tiếp
    const keepGroup = form.value.group_id
    form.value = { ...defaultForm(), group_id: keepGroup }
    showMore.value = false
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Thêm thất bại', life: 3000 })
  }
  saving.value = false
}

// === Excel Import ===
const downloadTemplate = () => {
  // File mẫu nằm sẵn trong public/
  window.open('/mau_import_thanh_vien.xlsx', '_blank')
}

const onFileSelect = (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (ev) => {
    try {
      const data = new Uint8Array(ev.target.result)
      // raw: true → đọc tất cả cells dạng text, không parse date
      const wb = XLSX.read(data, { type: 'array', raw: true })
      const ws = wb.Sheets[wb.SheetNames[0]]
      const rows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '', raw: true })

      if (rows.length < 2) {
        toast.add({ severity: 'warn', summary: 'File trống', detail: 'File không có dữ liệu', life: 3000 })
        return
      }

      const parsed = []
      for (let i = 1; i < rows.length; i++) {
        const row = rows[i]
        if (!row[0] && !row[1]) continue

        const phone = normalizePhone(row[1])
        const ngaySinhRaw = String(row[2] || '').trim()
        const ngay_sinh = parseNgaySinh(ngaySinhRaw)
        const gioiTinh = String(row[4] || '').toLowerCase()

        parsed.push({
          ho_ten: String(row[0] || '').trim(),
          phone,
          ngay_sinh,
          ngay_sinh_display: ngay_sinh || ngaySinhRaw,
          phap_danh: String(row[3] || '').trim() || null,
          gioi_tinh: gioiTinh.includes('n') && gioiTinh.includes('ữ') ? 'nu' : 'nam',
          phone2: normalizePhone(row[5]) || null,
          dia_chi: String(row[6] || '').trim() || null,
          ghi_chu: String(row[7] || '').trim() || null,
          _valid: !!(row[0] && phone),
          _error: !row[0] ? 'Thiếu họ tên' : !phone ? 'Thiếu SĐT' : ''
        })
      }

      importData.value = parsed
      showImportDialog.value = true
      importResult.value = null
    } catch {
      toast.add({ severity: 'error', summary: 'Lỗi', detail: 'Không đọc được file Excel', life: 3000 })
    }
  }
  reader.readAsArrayBuffer(file)
  e.target.value = ''
}

const validCount = computed(() => importData.value.filter(r => r._valid).length)
const invalidCount = computed(() => importData.value.filter(r => !r._valid).length)

const removeImportRow = (index) => {
  importData.value.splice(index, 1)
}

const submitImport = async () => {
  const validRows = importData.value.filter(r => r._valid)
  if (validRows.length === 0) {
    toast.add({ severity: 'warn', summary: 'Không có dữ liệu hợp lệ', detail: 'Vui lòng kiểm tra lại file', life: 3000 })
    return
  }

  importing.value = true
  try {
    const members = validRows.map(r => ({
      ho_ten: r.ho_ten, phone: r.phone, ngay_sinh: r.ngay_sinh || null,
      phap_danh: r.phap_danh, gioi_tinh: r.gioi_tinh,
      phone2: r.phone2, dia_chi: r.dia_chi, ghi_chu: r.ghi_chu,
      group_id: form.value.group_id || null
    }))

    const result = await apiFetch('/api/members/import', {
      method: 'POST',
      body: { members }
    })

    importResult.value = result.data
    if (result.data.imported > 0) {
      toast.add({
        severity: 'success', summary: 'Import thành công',
        detail: `Đã thêm ${result.data.imported}/${result.data.total} thành viên`,
        life: 5000
      })
    }
    if (result.data.failed > 0) {
      toast.add({
        severity: 'warn', summary: 'Một số dòng lỗi',
        detail: `${result.data.failed} dòng không import được`,
        life: 5000
      })
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Import thất bại', life: 3000 })
  }
  importing.value = false
}

const finishImport = () => {
  showImportDialog.value = false
  importData.value = []
  importResult.value = null
  router.push('/members')
}

onMounted(loadGroups)
</script>

<template>
  <div>
    <div class="flex items-center gap-3 mb-4">
      <NuxtLink to="/members">
        <Button icon="pi pi-arrow-left" text rounded />
      </NuxtLink>
      <h2 class="text-xl md:text-2xl font-bold text-surface-900 dark:text-surface-0 flex-1">Thêm thành viên</h2>
    </div>

    <!-- Nhập hàng loạt — compact -->
    <div class="flex flex-wrap gap-2 mb-4">
      <Button
        label="Từ danh bạ"
        icon="pi pi-address-book"
        size="small"
        severity="help"
        outlined
        @click="showContactDialog = true"
      />
      <Button
        label="Từ Excel"
        icon="pi pi-file-excel"
        size="small"
        severity="success"
        outlined
        @click="fileInput?.click()"
      />
      <a href="/mau_import_thanh_vien.xlsx" download class="ml-auto">
        <Button label="Tải mẫu" icon="pi pi-download" size="small" severity="info" text />
      </a>
      <input ref="fileInput" type="file" accept=".xlsx,.xls,.csv" class="hidden" @change="onFileSelect" />
    </div>

    <form @submit.prevent="saveMember">
      <div class="card mb-4">
        <div class="flex flex-col gap-4">
          <div>
            <label class="font-medium mb-2 block">Họ và tên <span class="text-red-500">*</span></label>
            <InputText v-model="form.ho_ten" class="w-full" placeholder="Nguyễn Văn A" />
          </div>
          <div>
            <label class="font-medium mb-2 block">Số điện thoại</label>
            <InputText v-model="form.phone" class="w-full" placeholder="0912 345 678 (không bắt buộc)" inputmode="tel" />
          </div>
          <div>
            <label class="font-medium mb-2 block">Pháp danh</label>
            <InputText v-model="form.phap_danh" class="w-full" placeholder="Có thể chưa có" />
          </div>
          <div>
            <label class="font-medium mb-2 block">Giới tính</label>
            <div class="flex items-center gap-5">
              <div class="flex items-center gap-2">
                <RadioButton v-model="form.gioi_tinh" inputId="gt_nam" value="nam" />
                <label for="gt_nam" class="cursor-pointer">Nam</label>
              </div>
              <div class="flex items-center gap-2">
                <RadioButton v-model="form.gioi_tinh" inputId="gt_nu" value="nu" />
                <label for="gt_nu" class="cursor-pointer">Nữ</label>
              </div>
              <div class="flex items-center gap-2">
                <RadioButton v-model="form.gioi_tinh" inputId="gt_kxd" value="khong_xac_dinh" />
                <label for="gt_kxd" class="cursor-pointer text-muted-color">Chưa xác định</label>
              </div>
            </div>
          </div>
          <div>
            <label class="font-medium mb-2 block">Năm sinh</label>
            <InputText v-model="form.ngay_sinh_text" class="w-full" placeholder="1990 hoặc 01/02/1990"
              @blur="formatDateInput" />
            <small class="text-muted-color mt-1 block">Nhập năm (1990) hoặc đầy đủ ngày/tháng/năm. VD: 1/2/1990 → 01/02/1990</small>
          </div>
          <div>
            <label class="font-medium mb-2 block">Nhóm</label>
            <Select v-model="form.group_id" :options="groups" optionLabel="ten_nhom" optionValue="id"
              class="w-full" placeholder="Chọn nhóm (không bắt buộc)" showClear />
          </div>
          <div>
            <label class="font-medium mb-2 block">Ghi chú cá nhân</label>
            <Textarea v-model="form.ghi_chu" rows="2" class="w-full" placeholder="Ghi chú đặc điểm riêng..." />
          </div>
        </div>
      </div>

      <div class="mb-4">
        <Button type="button" :label="showMore ? 'Ẩn thông tin thêm' : 'Thêm thông tin khác'"
          :icon="showMore ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
          severity="secondary" text class="!px-0" @click="showMore = !showMore" />
      </div>

      <div v-show="showMore" class="card mb-4">
        <div class="font-semibold text-lg mb-4">
          <i class="pi pi-info-circle mr-2"></i>Thông tin bổ sung
        </div>
        <div class="flex flex-col gap-4">
          <div class="grid">
            <div class="col-12 md:col-6">
              <label class="font-medium mb-2 block">SĐT phụ</label>
              <InputText v-model="form.phone2" class="w-full" inputmode="tel" />
            </div>
            <div class="col-12 md:col-6">
              <label class="font-medium mb-2 block">Zalo / Facebook</label>
              <InputText v-model="form.zalo_fb" class="w-full" placeholder="ID Zalo hoặc link FB" />
            </div>
          </div>
          <div class="grid">
            <div class="col-12 md:col-4">
              <label class="font-medium mb-2 block">Tỉnh / Thành phố</label>
              <InputText v-model="form.tinh_tp" class="w-full" />
            </div>
            <div class="col-12 md:col-4">
              <label class="font-medium mb-2 block">Xã / Phường</label>
              <InputText v-model="form.xa_phuong" class="w-full" />
            </div>
            <div class="col-12 md:col-4">
              <label class="font-medium mb-2 block">Địa chỉ chi tiết</label>
              <InputText v-model="form.dia_chi" class="w-full" placeholder="Số nhà, đường..." />
            </div>
          </div>
          <div class="grid">
            <div class="col-12 md:col-4">
              <label class="font-medium mb-2 block">Công việc</label>
              <InputText v-model="form.cong_viec" class="w-full" />
            </div>
            <div class="col-12 md:col-4">
              <label class="font-medium mb-2 block">Sức khỏe</label>
              <InputText v-model="form.suc_khoe" class="w-full" placeholder="Bệnh mãn tính, cần hỗ trợ..." />
            </div>
            <div class="col-12 md:col-4">
              <label class="font-medium mb-2 block">Kỹ năng đặc biệt</label>
              <InputText v-model="form.ky_nang" class="w-full" placeholder="Nấu ăn, lái xe, y tế..." />
            </div>
          </div>
          <div>
            <label class="font-medium mb-2 block">Người giới thiệu</label>
            <InputText v-model="form.nguoi_gioi_thieu" class="w-full" />
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-3">
        <NuxtLink to="/members">
          <Button label="Hủy" severity="secondary" text />
        </NuxtLink>
        <Button type="submit" label="Lưu thành viên" icon="pi pi-check" :loading="saving" />
      </div>
    </form>

    <!-- ==================== DIALOG IMPORT EXCEL ==================== -->
    <Dialog v-model:visible="showImportDialog" modal header="📊 Import từ Excel"
      :style="{ width: '95vw', maxWidth: '800px' }" :closable="!importing">

      <div v-if="!importResult">
        <div class="flex items-center gap-3 mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <i class="pi pi-info-circle text-blue-500"></i>
          <span class="flex-1 text-sm">Cột "Năm sinh" nhập text: 1990 hoặc 01/02/1990. <b>Không format date trong Excel.</b></span>
          <Button label="Tải file mẫu" icon="pi pi-download" size="small" severity="info" outlined
            @click="downloadTemplate" />
        </div>

        <div class="mb-4">
          <label class="font-medium mb-2 block text-sm">Nhóm áp dụng cho tất cả (không bắt buộc):</label>
          <Select v-model="form.group_id" :options="groups" optionLabel="ten_nhom" optionValue="id"
            class="w-full" placeholder="Chọn nhóm..." showClear />
        </div>

        <div class="flex gap-3 mb-3">
          <Tag :value="`${importData.length} dòng`" severity="info" />
          <Tag :value="`${validCount} hợp lệ`" severity="success" />
          <Tag v-if="invalidCount" :value="`${invalidCount} lỗi`" severity="danger" />
        </div>

        <div class="overflow-auto max-h-96 border border-surface-200 dark:border-surface-600 rounded-lg">
          <table class="w-full text-sm">
            <thead class="sticky top-0 bg-surface-100 dark:bg-surface-700">
              <tr>
                <th class="text-left px-3 py-2">#</th>
                <th class="text-left px-3 py-2">Họ tên</th>
                <th class="text-left px-3 py-2">SĐT</th>
                <th class="text-left px-3 py-2">Năm sinh</th>
                <th class="text-left px-3 py-2">Pháp danh</th>
                <th class="text-left px-3 py-2">GT</th>
                <th class="text-left px-3 py-2">Trạng thái</th>
                <th class="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in importData" :key="i"
                :class="row._valid ? '' : 'bg-red-50 dark:bg-red-900/10'">
                <td class="px-3 py-2 text-muted-color">{{ i + 1 }}</td>
                <td class="px-3 py-2 font-medium">{{ row.ho_ten || '—' }}</td>
                <td class="px-3 py-2">{{ row.phone || '—' }}</td>
                <td class="px-3 py-2">{{ row.ngay_sinh_display || '—' }}</td>
                <td class="px-3 py-2">{{ row.phap_danh || '' }}</td>
                <td class="px-3 py-2">{{ row.gioi_tinh === 'nu' ? 'Nữ' : 'Nam' }}</td>
                <td class="px-3 py-2">
                  <Tag v-if="row._valid" value="OK" severity="success" class="!text-xs" />
                  <Tag v-else :value="row._error" severity="danger" class="!text-xs" />
                </td>
                <td class="px-3 py-2">
                  <Button icon="pi pi-times" text rounded severity="danger" size="small"
                    @click="removeImportRow(i)" v-tooltip.left="'Xóa dòng'" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="text-center py-6">
        <i class="pi pi-check-circle text-5xl text-green-500 mb-4 block"></i>
        <h3 class="text-xl font-bold mb-2">Import hoàn tất!</h3>
        <div class="flex justify-center gap-4 mb-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ importResult.imported }}</div>
            <div class="text-sm text-muted-color">Thành công</div>
          </div>
          <div v-if="importResult.failed" class="text-center">
            <div class="text-2xl font-bold text-red-600">{{ importResult.failed }}</div>
            <div class="text-sm text-muted-color">Thất bại</div>
          </div>
        </div>
        <div v-if="importResult.errors?.length" class="text-left mt-4">
          <div class="font-medium mb-2 text-red-600">
            <i class="pi pi-exclamation-triangle mr-1"></i>Chi tiết lỗi:
          </div>
          <div class="overflow-auto max-h-40 bg-red-50 dark:bg-red-900/10 rounded-lg p-3 text-sm">
            <div v-for="err in importResult.errors" :key="err.row" class="mb-1">
              <span class="font-medium">Dòng {{ err.row }}</span>
              <span v-if="err.ho_ten"> ({{ err.ho_ten }})</span>:
              <span class="text-red-600">{{ err.error }}</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <template v-if="!importResult">
          <Button label="Hủy" severity="secondary" text @click="showImportDialog = false" />
          <Button :label="`Import ${validCount} thành viên`" icon="pi pi-upload"
            :loading="importing" :disabled="validCount === 0" @click="submitImport" />
        </template>
        <template v-else>
          <Button label="Xong" icon="pi pi-check" @click="finishImport" />
        </template>
      </template>
    </Dialog>

    <!-- Dialog Import từ Danh bạ -->
    <MembersContactImportDialog
      v-model:visible="showContactDialog"
      :groups="groups"
      @import="onContactImport"
    />

    <Toast />
  </div>
</template>
