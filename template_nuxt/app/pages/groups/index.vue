<script setup>
const { apiFetch } = useApi()
const toast = useToast()

const groups = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editMode = ref(false)
const form = ref({ id: '', ten_nhom: '', mo_ta: '' })
const saving = ref(false)

const loadGroups = async () => {
  loading.value = true
  try {
    const data = await apiFetch('/api/groups')
    groups.value = data.data
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: 'Không tải được danh sách nhóm', life: 3000 })
  }
  loading.value = false
}

const openCreate = () => {
  form.value = { id: '', ten_nhom: '', mo_ta: '' }
  editMode.value = false
  showDialog.value = true
}

const openEdit = (group) => {
  form.value = { id: group.id, ten_nhom: group.ten_nhom, mo_ta: group.mo_ta || '' }
  editMode.value = true
  showDialog.value = true
}

const saveGroup = async () => {
  if (!form.value.ten_nhom) {
    toast.add({ severity: 'warn', summary: 'Thiếu thông tin', detail: 'Vui lòng nhập tên nhóm', life: 3000 })
    return
  }
  saving.value = true
  try {
    if (editMode.value) {
      await apiFetch(`/api/groups/${form.value.id}`, { method: 'PUT', body: form.value })
      toast.add({ severity: 'success', summary: 'Thành công', detail: 'Cập nhật nhóm thành công', life: 3000 })
    } else {
      await apiFetch('/api/groups', { method: 'POST', body: form.value })
      toast.add({ severity: 'success', summary: 'Thành công', detail: 'Tạo nhóm thành công', life: 3000 })
    }
    showDialog.value = false
    loadGroups()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Thao tác thất bại', life: 3000 })
  }
  saving.value = false
}

const deleteGroup = async (group) => {
  if (!confirm(`Xóa nhóm "${group.ten_nhom}"?`)) return
  try {
    await apiFetch(`/api/groups/${group.id}`, { method: 'DELETE' })
    toast.add({ severity: 'success', summary: 'Thành công', detail: 'Xóa nhóm thành công', life: 3000 })
    loadGroups()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Xóa thất bại', life: 3000 })
  }
}

onMounted(loadGroups)
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg md:text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">Nhóm</h2>
      <Button icon="pi pi-plus" class="md:hidden" rounded size="small" @click="openCreate" />
      <Button label="Thêm nhóm" icon="pi pi-plus" class="hidden md:inline-flex" @click="openCreate" />
    </div>

    <div class="card">
      <DataTable :value="groups" :loading="loading" stripedRows responsiveLayout="scroll"
        emptyMessage="Chưa có nhóm nào. Hãy tạo nhóm đầu tiên.">
        <Column field="ten_nhom" header="Tên nhóm" sortable />
        <Column field="mo_ta" header="Mô tả" class="hidden md:table-cell" />
        <Column field="member_count" header="TV" sortable style="width: 70px">
          <template #body="{ data }">
            <Tag :value="data.member_count || 0" severity="info" />
          </template>
        </Column>
        <Column field="created_at" header="Ngày tạo" sortable style="width: 120px" class="hidden lg:table-cell">
          <template #body="{ data }">
            {{ data.created_at ? new Date(data.created_at).toLocaleDateString('vi-VN') : '' }}
          </template>
        </Column>
        <Column header="" style="width: 90px">
          <template #body="{ data }">
            <Button icon="pi pi-pencil" text rounded severity="info" size="small" @click="openEdit(data)" />
            <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="deleteGroup(data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Dialog tạo/sửa nhóm -->
    <Dialog v-model:visible="showDialog" :header="editMode ? 'Sửa nhóm' : 'Thêm nhóm mới'" modal
      :style="{ width: '450px' }">
      <div class="flex flex-col gap-4 pt-2">
        <div class="flex flex-col gap-2">
          <label for="ten_nhom" class="font-medium">Tên nhóm <span class="text-red-500">*</span></label>
          <InputText id="ten_nhom" v-model="form.ten_nhom" placeholder="VD: Đạo tràng Quận 1" />
        </div>
        <div class="flex flex-col gap-2">
          <label for="mo_ta" class="font-medium">Mô tả</label>
          <Textarea id="mo_ta" v-model="form.mo_ta" rows="3" placeholder="Mô tả ngắn về nhóm" />
        </div>
      </div>
      <template #footer>
        <Button label="Hủy" severity="secondary" text @click="showDialog = false" />
        <Button :label="editMode ? 'Cập nhật' : 'Tạo nhóm'" :loading="saving" @click="saveGroup" />
      </template>
    </Dialog>

    <Toast />
  </div>
</template>
