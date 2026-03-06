<script setup>
import * as XLSX from 'xlsx'

const { apiFetch } = useApi()
const toast = useToast()
const { user } = useAuth()

const isManager = computed(() => user.value?.role === 'admin' || user.value?.role === 'manager')

const members = ref([])
const loading = ref(false)
const selectedMembers = ref([])
const search = ref('')

const loadMembers = async () => {
  loading.value = true
  try {
    const data = await apiFetch(`/api/members?limit=3000${search.value ? '&search='+encodeURIComponent(search.value) : ''}`) 
    members.value = data.data || []
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi tải danh bạ', life: 3000 })
  }
  loading.value = false
}

// Xử lý Search debounce
let searchTimeout
const onSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { loadMembers() }, 400)
}

const exportExcel = (dataToExport, fileName) => {
  const ws = XLSX.utils.json_to_sheet(dataToExport.map(m => ({
    'ID': m.id,
    'Họ Tên': m.ho_ten,
    'SĐT': m.phone,
    'Pháp danh': m.phap_danh || '',
    'Giới tính': m.gioi_tinh === 'nam' ? 'Nam' : 'Nữ',
    'Ngày sinh': m.ngay_sinh || '',
    'Ngày gia nhập': m.ngay_gia_nhap || '',
    'Trạng thái': m.trang_thai,
    'Ghi chú': m.ghi_chu || ''
  })))
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Danh_Ba')
  XLSX.writeFile(wb, fileName)
}

const saving = ref(false)

const deleteSelected = async () => {
  if (!selectedMembers.value.length) return
  const ids = selectedMembers.value.map(m => m.id)
  
  if (confirm(`Bạn có chắc chắn muốn xoá ${ids.length} người đã chọn? Hành động này sẽ xoá luôn cả các lịch sử chăm sóc liên quan.`)) {
    saving.value = true
    if (ids.length > 10) {
      toast.add({ severity: 'info', summary: 'Đang tải file backup trước khi xoá...', life: 2500 })
      exportExcel(selectedMembers.value, `Backup_Xoa_${ids.length}_Nguoi_${new Date().toISOString().slice(0,10)}.xlsx`)
    }
    
    try {
      await apiFetch('/api/members/bulk-delete', {
        method: 'POST',
        body: { ids }
      })
      toast.add({ severity: 'success', summary: `Đã xoá ${ids.length} người`, life: 2000 })
      selectedMembers.value = []
      loadMembers()
    } catch (e) {
      toast.add({ severity: 'error', summary: 'Lỗi xoá dữ liệu', detail: e?.data?.message, life: 3000 })
    }
    saving.value = false
  }
}

const deleteAll = async () => {
  if (confirm('NGUY HIỂM: Bạn có chắc chắn muốn XÓA TOÀN BỘ danh bạ trong đạo tràng? Hành động này không thể hoàn tác!')) {
    const confirmText = prompt('Vui lòng gõ chữ XOA (viết hoa) để xác nhận:')
    if (confirmText === 'XOA') {
      saving.value = true
      
      if (members.value.length > 0) {
        toast.add({ severity: 'info', summary: 'Đang tải file backup toàn bộ...', life: 2500 })
        exportExcel(members.value, `Backup_Xoa_Toan_Bo_${members.value.length}_Nguoi_${new Date().toISOString().slice(0,10)}.xlsx`)
      }

      try {
        await apiFetch('/api/members/delete-all', {
          method: 'POST',
          body: { confirm_text: 'XOA' }
        })
        toast.add({ severity: 'success', summary: `Đã xoá toàn bộ danh bạ`, life: 2000 })
        selectedMembers.value = []
        loadMembers()
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message, life: 3000 })
      }
      saving.value = false
    } else {
      toast.add({ severity: 'warn', summary: 'Hủy thao tác xoá vì chữ xác nhận không chính xác.', life: 3000 })
    }
  }
}

onMounted(() => {
  loadMembers()
})
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <h2 class="text-xl font-bold flex items-center gap-2">
        <i class="pi pi-address-book text-primary"></i> Danh Bạ
      </h2>
      
      <div v-if="isManager" class="flex gap-2 flex-wrap">
        <Button 
          v-if="selectedMembers.length > 0"
          :label="`Xóa ${selectedMembers.length} dòng`" 
          icon="pi pi-trash" 
          severity="danger" 
          :loading="saving"
          @click="deleteSelected"
          size="small"
        />
        <Button 
          label="Xóa tất cả" 
          icon="pi pi-ban" 
          severity="danger" 
          outlined
          :loading="saving"
          @click="deleteAll"
          size="small"
        />
      </div>
      <div v-else class="text-xs text-red-500 font-medium">
        Chính thức xoá chỉ dành cho Admin / Manager
      </div>
    </div>

    <!-- Toolbar: Search -->
    <IconField>
      <InputIcon class="pi pi-search" />
      <InputText
        v-model="search"
        placeholder="Tìm tên, SĐT, pháp danh..."
        class="w-full md:w-80"
        @input="onSearch"
      />
    </IconField>
    
    <!-- Table -->
    <DataTable 
      v-model:selection="selectedMembers" 
      :value="members" 
      dataKey="id"
      :loading="loading"
      responsiveLayout="scroll"
      size="small"
      scrollable
      scrollHeight="70vh"
      class="border rounded-md shadow-sm overflow-hidden"
    >
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
      <Column field="ho_ten" header="Họ Tên" sortable>
        <template #body="slotProps">
          <span class="font-medium text-primary-600 dark:text-primary-400">{{ slotProps.data.ho_ten }}</span>
        </template>
      </Column>
      <Column field="phone" header="SĐT">
        <template #body="slotProps">
          <span class="text-muted-color">{{ slotProps.data.phone }}</span>
        </template>
      </Column>
      <Column field="phap_danh" header="Pháp danh" class="hidden md:table-cell"></Column>
      <Column field="gioi_tinh" header="Giới tính" class="hidden sm:table-cell">
        <template #body="slotProps">
          <span v-if="slotProps.data.gioi_tinh === 'nam'">Nam</span>
          <span v-else-if="slotProps.data.gioi_tinh === 'nu'">Nữ</span>
          <span v-else>—</span>
        </template>
      </Column>
      <Column field="ghi_chu" header="Ghi chú" class="hidden lg:table-cell">
        <template #body="slotProps">
          <span class="text-xs text-muted-color line-clamp-1" :title="slotProps.data.ghi_chu">{{ slotProps.data.ghi_chu }}</span>
        </template>
      </Column>
      <template #empty>
        <div class="p-6 text-center text-muted-color">
          <i class="pi pi-inbox text-2xl mb-2"></i>
          <p>Không có dữ liệu.</p>
        </div>
      </template>
    </DataTable>

    <Toast />
  </div>
</template>
