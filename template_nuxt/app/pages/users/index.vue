<script setup lang="ts">
const { apiFetch } = useApi()
const { user } = useAuth()
const toast = useToast()

// Chỉ admin mới vào được trang này
if (user.value?.role !== 'admin') {
  navigateTo('/')
}

const users = ref<any[]>([])
const groups = ref<any[]>([])
const loading = ref(true)
const showDialog = ref(false)
const editMode = ref(false)
const saving = ref(false)

// Khi tạo user: nếu username đã tồn tại ở org khác → dùng pass cũ
const existingOrgNotice = ref('')

const roleOptions = [
  { label: '👑 Admin', value: 'admin' },
  { label: '📊 Quản lý cấp cao', value: 'manager' },
  { label: '👤 Trưởng nhóm', value: 'leader' }
]

const roleLabel: Record<string, string> = {
  admin: '👑 Admin',
  manager: '📊 Quản lý',
  leader: '👤 Trưởng nhóm'
}

const roleSeverity: Record<string, string> = {
  admin: 'danger',
  manager: 'warn',
  leader: 'info'
}

const form = ref({
  id: '',
  username: '',
  password: '',
  email: '',
  phone: '',
  ho_ten: '',
  role: 'leader' as string,
  group_id: null as string | null,
  support_group_ids: [] as string[]
})

const loadData = async () => {
  loading.value = true
  try {
    const [userData, groupData] = await Promise.all([
      apiFetch('/api/users'),
      apiFetch('/api/groups')
    ])
    users.value = userData.data
    groups.value = groupData.data
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Không tải được dữ liệu', life: 3000 })
  }
  loading.value = false
}

const openCreate = () => {
  form.value = { id: '', username: '', password: '', email: '', phone: '', ho_ten: '', role: 'leader', group_id: null, support_group_ids: [] }
  existingOrgNotice.value = ''
  editMode.value = false
  showDialog.value = true
}

const openEdit = (u: any) => {
  form.value = {
    id: u.id,
    username: u.username || u.email || '',
    password: '',
    email: u.email || '',
    phone: u.phone || '',
    ho_ten: u.ho_ten,
    role: u.role,
    group_id: u.group_id,
    support_group_ids: u.support_group_ids || []
  }
  existingOrgNotice.value = ''
  editMode.value = true
  showDialog.value = true
}

const saveUser = async () => {
  if (!form.value.username || !form.value.ho_ten || !form.value.role) {
    toast.add({ severity: 'warn', summary: 'Thiếu thông tin', detail: 'Vui lòng điền tài khoản, họ tên, vai trò', life: 3000 })
    return
  }
  if (form.value.role === 'leader' && !form.value.group_id) {
    toast.add({ severity: 'warn', summary: 'Thiếu thông tin', detail: 'Trưởng nhóm phải được gán nhóm chính', life: 3000 })
    return
  }

  saving.value = true
  existingOrgNotice.value = ''
  try {
    const body: any = {
      username: form.value.username,
      email: form.value.email || undefined,
      phone: form.value.phone || undefined,
      ho_ten: form.value.ho_ten,
      role: form.value.role,
      group_id: form.value.role === 'leader' ? form.value.group_id : null,
      support_group_ids: form.value.role === 'leader' ? form.value.support_group_ids : []
    }
    if (form.value.password) body.password = form.value.password

    if (editMode.value) {
      await apiFetch(`/api/users/${form.value.id}`, { method: 'PUT', body })
      toast.add({ severity: 'success', summary: 'Thành công', detail: 'Cập nhật thành công', life: 3000 })
      showDialog.value = false
    } else {
      const res = await apiFetch('/api/users', { method: 'POST', body })
      if (res.used_existing_password && res.existing_org_name) {
        existingOrgNotice.value = res.message
        toast.add({
          severity: 'info',
          summary: 'Lưu ý',
          detail: res.message,
          life: 6000
        })
      } else {
        toast.add({ severity: 'success', summary: 'Thành công', detail: 'Tạo tài khoản thành công', life: 3000 })
      }
      showDialog.value = false
    }
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Thao tác thất bại', life: 3000 })
  }
  saving.value = false
}

const deleteUser = async (u: any) => {
  if (!confirm(`Xóa tài khoản "${u.ho_ten}" (@${u.username})?`)) return
  try {
    await apiFetch(`/api/users/${u.id}`, { method: 'DELETE' })
    toast.add({ severity: 'success', summary: 'Đã xóa', detail: 'Xóa tài khoản thành công', life: 3000 })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Xóa thất bại', life: 3000 })
  }
}

onMounted(loadData)
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg md:text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">Tài khoản</h2>
      <Button icon="pi pi-plus" class="md:hidden" rounded size="small" @click="openCreate" />
      <Button label="Thêm tài khoản" icon="pi pi-plus" class="hidden md:inline-flex" @click="openCreate" />
    </div>

    <div class="card">
      <DataTable :value="users" :loading="loading" stripedRows>
        <template #empty>Chưa có tài khoản nào</template>
        <Column field="ho_ten" header="Họ tên" sortable>
          <template #body="{ data }">
            <div class="font-semibold">{{ data.ho_ten }}</div>
            <div class="text-xs text-muted-color">@{{ data.username }}</div>
          </template>
        </Column>
        <Column field="phone" header="SĐT" class="hidden md:table-cell">
          <template #body="{ data }">
            <span v-if="data.phone">{{ data.phone }}</span>
            <span v-else class="text-muted-color">—</span>
          </template>
        </Column>
        <Column field="email" header="Email" class="hidden lg:table-cell">
          <template #body="{ data }">
            <span v-if="data.email" class="text-xs">{{ data.email }}</span>
            <span v-else class="text-muted-color text-xs">—</span>
          </template>
        </Column>
        <Column field="role" header="Vai trò" sortable>
          <template #body="{ data }">
            <Tag :value="roleLabel[data.role] || data.role" :severity="roleSeverity[data.role]" />
          </template>
        </Column>
        <Column field="group_name" header="Nhóm chính">
          <template #body="{ data }">
            <span v-if="data.group_name">{{ data.group_name }}</span>
            <span v-else class="text-muted-color">—</span>
          </template>
        </Column>
        <Column field="support_group_ids" header="Hỗ trợ chéo" class="hidden md:table-cell">
          <template #body="{ data }">
            <span v-if="data.support_group_ids?.length">{{ data.support_group_ids.length }} nhóm</span>
            <span v-else class="text-muted-color">—</span>
          </template>
        </Column>
        <Column header="Thao tác" style="width: 100px">
          <template #body="{ data }">
            <div class="flex gap-1">
              <Button icon="pi pi-pencil" text rounded severity="info" size="small" @click="openEdit(data)" />
              <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="deleteUser(data)"
                :disabled="data.id === user?.id" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Dialog tạo/sửa -->
    <Dialog v-model:visible="showDialog" :header="editMode ? 'Sửa tài khoản' : 'Tạo tài khoản mới'" modal :style="{ width: '520px' }">
      <div class="flex flex-col gap-4 pt-2">
        <!-- Tài khoản (username) -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Tài khoản <span class="text-red-500">*</span></label>
          <InputText v-model="form.username" class="w-full" placeholder="vd: nguyenvana" :disabled="editMode" />
          <span v-if="!editMode" class="text-xs text-muted-color">Dùng để đăng nhập. Nếu đã có ở đạo tràng khác sẽ dùng mật khẩu hiện có.</span>
        </div>

        <!-- Mật khẩu -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">
            {{ editMode ? 'Mật khẩu mới (bỏ trống = giữ nguyên)' : 'Mật khẩu' }}
            <span v-if="!editMode" class="text-muted-color text-sm">(bỏ trống nếu đã có ở đạo tràng khác)</span>
          </label>
          <InputText v-model="form.password" class="w-full" type="password"
            :placeholder="editMode ? 'Bỏ trống nếu không đổi' : 'Nhập mật khẩu'" />
        </div>

        <!-- Họ tên -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Họ và tên <span class="text-red-500">*</span></label>
          <InputText v-model="form.ho_ten" class="w-full" />
        </div>

        <!-- SĐT + Email cùng hàng -->
        <div class="grid grid-cols-2 gap-3">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Số điện thoại</label>
            <InputText v-model="form.phone" class="w-full" placeholder="0901..." />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Email</label>
            <InputText v-model="form.email" class="w-full" type="email" placeholder="tùy chọn" />
          </div>
        </div>

        <!-- Vai trò -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Vai trò <span class="text-red-500">*</span></label>
          <Select v-model="form.role" :options="roleOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>

        <!-- Nhóm chính -->
        <div v-if="form.role === 'leader'" class="flex flex-col gap-2">
          <label class="font-medium">Nhóm chính <span class="text-red-500">*</span></label>
          <Select v-model="form.group_id" :options="groups" optionLabel="ten_nhom" optionValue="id"
            class="w-full" placeholder="Chọn nhóm phụ trách" />
        </div>

        <!-- Nhóm hỗ trợ chéo -->
        <div v-if="form.role === 'leader'" class="flex flex-col gap-2">
          <label class="font-medium">Nhóm hỗ trợ chéo</label>
          <MultiSelect v-model="form.support_group_ids" :options="groups.filter(g => g.id !== form.group_id)"
            optionLabel="ten_nhom" optionValue="id" class="w-full" placeholder="Chọn nhóm hỗ trợ (không bắt buộc)"
            display="chip" />
        </div>

        <div v-if="form.role === 'leader'" class="p-3 rounded-border bg-blue-50 dark:bg-blue-900/20 text-sm">
          <i class="pi pi-info-circle mr-2"></i>
          Trưởng nhóm chỉ xem/chăm sóc thành viên trong nhóm chính + nhóm hỗ trợ chéo.
        </div>
      </div>
      <template #footer>
        <Button label="Hủy" severity="secondary" text @click="showDialog = false" />
        <Button :label="editMode ? 'Cập nhật' : 'Tạo mới'" icon="pi pi-check" :loading="saving" @click="saveUser" />
      </template>
    </Dialog>

    <Toast />
  </div>
</template>
