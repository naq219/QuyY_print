<script setup>
const { apiFetch } = useApi()
const toast = useToast()

// Data
const groups = ref([])
const ungrouped = ref([])
const unassignedCount = ref(0)
const loading = ref(true)
const saving = ref(false)
const showAssignDialog = ref(false) // MỚI: Dialog phân bổ

// Selection (Phân bổ)
const selectedMembers = ref([])
const targetGroupIdTab0 = ref(null)

// Auto-assign
const autoAssigning = ref(false)

// Chuyển nhóm (Main Page Layout)
const sourceGroupId = ref(null)
const sourceMembers = ref([])
const selectedSource = ref([])
const targetGroupIdTab1 = ref(null)

// ── Computed ──
const totalActive = computed(() => {
  const inGroups = groups.value.reduce((sum, g) => sum + (Number(g.active_count) || 0), 0)
  return inGroups + ungrouped.value.length
})

// ── Load Data ──
const loadAll = async () => {
  loading.value = true
  try {
    const [gRes, mRes] = await Promise.all([
      apiFetch('/api/groups'),
      apiFetch('/api/members?group_id=none&trang_thai=active&limit=500')
    ])
    groups.value = gRes.data || []
    unassignedCount.value = gRes.unassigned_count || 0
    ungrouped.value = mRes.data || []
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

const loadSourceMembers = async () => {
  if (!sourceGroupId.value) {
    sourceMembers.value = []
    selectedSource.value = []
    return
  }
  try {
    const data = await apiFetch(`/api/members?group_id=${sourceGroupId.value}&trang_thai=active&limit=500`)
    sourceMembers.value = data.data || []
    selectedSource.value = []
  } catch (e) {
    console.error(e)
  }
}

// ── Manual Assign (In Dialog) ──
const doManualAssign = async () => {
  const ids = selectedMembers.value.map(m => m.id)
  if (!ids.length || !targetGroupIdTab0.value) return

  saving.value = true
  try {
    await apiFetch('/api/members/bulk-group', {
      method: 'POST',
      body: { member_ids: ids, group_id: targetGroupIdTab0.value }
    })
    toast.add({ severity: 'success', summary: `Đã phân bổ ${ids.length} người`, life: 2500 })
    selectedMembers.value = []
    targetGroupIdTab0.value = null
    await loadAll()
    if (ungrouped.value.length === 0) {
      showAssignDialog.value = false // Tự đóng dialog nếu hết người
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message, life: 3000 })
  }
  saving.value = false
}

// ── Auto Assign ──
const doAutoAssign = async () => {
  if (!ungrouped.value.length || !groups.value.length) return
  
  autoAssigning.value = true
  try {
    // Tính toán phân bổ: thêm người vào nhóm ít nhất trước
    const groupCounts = groups.value.map(g => ({
      id: g.id,
      count: Number(g.active_count) || 0
    }))
    
    const assignments = {} // { group_id: [member_ids] }
    
    for (const member of ungrouped.value) {
      // Tìm nhóm có ít người nhất
      groupCounts.sort((a, b) => a.count - b.count)
      const target = groupCounts[0]
      
      if (!assignments[target.id]) assignments[target.id] = []
      assignments[target.id].push(member.id)
      target.count++ // Cập nhật count ảo để phân bổ đều
    }
    
    // Gọi API cho từng nhóm
    let totalAssigned = 0
    for (const [groupId, memberIds] of Object.entries(assignments)) {
      await apiFetch('/api/members/bulk-group', {
        method: 'POST',
        body: { member_ids: memberIds, group_id: groupId }
      })
      totalAssigned += memberIds.length
    }
    
    toast.add({ severity: 'success', summary: `Tự động phân bổ ${totalAssigned} người vào ${Object.keys(assignments).length} nhóm`, life: 3000 })
    await loadAll()
    showAssignDialog.value = false
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi phân bổ tự động', detail: e?.data?.message, life: 3000 })
  }
  autoAssigning.value = false
}

// ── Transfer ──
const doTransfer = async () => {
  const ids = selectedSource.value.map(m => m.id)
  if (!ids.length || !targetGroupIdTab1.value) return

  saving.value = true
  try {
    await apiFetch('/api/members/bulk-group', {
      method: 'POST',
      body: { member_ids: ids, group_id: targetGroupIdTab1.value }
    })
    toast.add({ severity: 'success', summary: `Đã chuyển ${ids.length} người`, life: 2500 })
    selectedSource.value = []
    targetGroupIdTab1.value = null
    await Promise.all([loadAll(), loadSourceMembers()])
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message, life: 3000 })
  }
  saving.value = false
}

watch(sourceGroupId, loadSourceMembers)

onMounted(loadAll)
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12"><ProgressSpinner /></div>

    <template v-else>
      <!-- ═══ Tổng quan nhóm ═══ -->
      <div class="card">
        <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
          <h3 class="text-lg font-bold m-0">
            <i class="pi pi-sitemap mr-2 text-primary"></i>Tổng quan nhóm
          </h3>
          <span class="text-sm text-muted-color">
            Tổng: <strong>{{ totalActive }}</strong> thành viên đang hoạt động
          </span>
        </div>

        <div class="flex flex-wrap gap-2 items-center">
          <!-- Chip chưa phân bổ -->
          <div
            v-if="ungrouped.length > 0"
            class="flex items-center gap-3 px-1 py-1 pr-3 rounded-full border-2 border-orange-400 bg-orange-50 dark:bg-orange-900/10 text-orange-700 dark:text-orange-300 text-sm font-medium mr-2"
          >
            <div class="flex items-center gap-2 pl-2">
              <span>Chưa phân bổ</span>
              <Badge :value="ungrouped.length" severity="warn" size="small" />
            </div>
            <!-- MỚI: Nút bấm Phân bổ ngay nằm trong chip (hoặc bên cạnh) -->
            <Button
              label="Phân bổ ngay"
              icon="pi pi-arrow-right"
              severity="warn"
              size="small"
              class="!text-xs h-7 !py-0 ml-1"
              @click="showAssignDialog = true"
            />
          </div>

          <!-- Chip "đều" khi không có chưa phân bổ -->
          <!-- Đã ẩn hiển thị chip này nếu không cần thiết nữa theo yêu cầu: "hoàn tất phân bổ rồi không hiển thị nữa" -->
          <template v-else></template>

          <div v-if="ungrouped.length > 0" class="h-6 w-px bg-surface-300 dark:bg-surface-600 hidden md:block mr-1"></div>

          <!-- Chip từng nhóm -->
          <div
            v-for="g in groups" :key="g.id"
            class="flex items-center gap-2 px-3 py-1.5 rounded-full border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 transition-colors cursor-default text-sm"
          >
            <span class="font-medium truncate max-w-[150px]" :title="g.ten_nhom">{{ g.ten_nhom }}</span>
            <Badge :value="g.active_count || 0" severity="info" size="small" />
          </div>
        </div>
      </div>

      <!-- ═══ Chuyển nhóm (Main page layout) ═══ -->
      <div class="card !p-0 overflow-hidden">
        <!-- TabHeader giả để giữ UI quen thuộc hoặc gỡ bỏ đi thay bằng title bình thường -->
        <div class="bg-surface-50 dark:bg-surface-800 border-b border-surface-200 dark:border-surface-700 p-4">
          <h3 class="font-bold text-lg m-0 flex items-center">
            <i class="pi pi-arrow-right-arrow-left mr-2"></i>Chuyển thành viên giữa các nhóm
          </h3>
          <p class="text-sm text-muted-color mt-1">Chọn nhóm nguồn, tick chọn thành viên và chuyển sang nhóm mới.</p>
        </div>

        <div class="p-4 bg-surface-0 dark:bg-surface-900">
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <!-- Left: Source List -->
            <div class="lg:col-span-8 flex flex-col gap-3">
              <div class="flex items-center gap-3">
                <span class="text-sm font-medium whitespace-nowrap">Từ nhóm:</span>
                <Select
                  v-model="sourceGroupId"
                  :options="groups"
                  optionLabel="ten_nhom"
                  optionValue="id"
                  placeholder="-- Chọn nhóm nguồn --"
                  class="min-w-[200px]"
                >
                  <template #option="{ option }">
                    <div class="flex justify-between w-full">
                      <span>{{ option.ten_nhom }}</span>
                      <span class="text-muted-color text-xs ml-2">({{ option.active_count || 0 }})</span>
                    </div>
                  </template>
                </Select>
              </div>

              <DataTable
                v-model:selection="selectedSource"
                :value="sourceMembers"
                dataKey="id"
                size="small"
                scrollable scrollHeight="60vh"
                class="border border-surface-200 dark:border-surface-700 rounded-lg overflow-hidden block"
              >
                <template #empty>
                  <div class="p-6 text-center text-muted-color text-sm">
                    <span v-if="!sourceGroupId">Vui lòng chọn nhóm nguồn ở trên</span>
                    <span v-else>Nhóm này không có thành viên hoạt động nào.</span>
                  </div>
                </template>
                <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                <Column field="ho_ten" header="Họ tên" class="font-medium">
                  <template #body="{ data }">
                    {{ data.ho_ten }}
                    <span v-if="data.phap_danh" class="text-xs text-muted-color font-normal ml-1">- {{ data.phap_danh }}</span>
                  </template>
                </Column>
                <Column field="phone" header="SĐT" class="text-sm text-muted-color"></Column>
              </DataTable>
            </div>

            <!-- Right: Form -->
            <div class="lg:col-span-4">
              <div class="p-4 rounded-xl border border-primary/30 bg-primary/5 dark:bg-primary/10 sticky top-4">
                <h4 class="font-bold mb-1">Chuyển sang nhóm mới</h4>
                <p class="text-sm mb-4">
                  Đã chọn: <strong class="text-primary">{{ selectedSource.length }}</strong> người
                </p>

                <div class="flex flex-col gap-2 mb-4">
                  <label class="text-sm font-medium">Nhóm đích</label>
                  <Select
                    v-model="targetGroupIdTab1"
                    :options="groups.filter(g => g.id !== sourceGroupId)"
                    optionLabel="ten_nhom"
                    optionValue="id"
                    placeholder="Chọn nhóm đích..."
                    class="w-full"
                  >
                    <template #option="{ option }">
                      <div class="flex justify-between w-full">
                        <span>{{ option.ten_nhom }}</span>
                        <span class="text-muted-color text-xs ml-2">({{ option.active_count || 0 }})</span>
                      </div>
                    </template>
                  </Select>
                </div>

                <Button
                  label="Chuyển nhóm"
                  icon="pi pi-arrow-right-arrow-left"
                  class="w-full"
                  :disabled="!selectedSource.length || !targetGroupIdTab1"
                  :loading="saving"
                  @click="doTransfer"
                />
                <p class="text-[0.7rem] text-center text-orange-600 dark:text-orange-400 mt-3 font-medium">
                  Lưu ý: Lịch sử chăm sóc vẫn được giữ nguyên.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══ DIALOG: Phân bổ người chưa có nhóm ═══ -->
    <Dialog 
      v-model:visible="showAssignDialog" 
      header="Phân bổ thành viên chưa có nhóm" 
      modal 
      :style="{ width: '800px', maxWidth: '95vw' }"
      class="p-fluid"
    >
      <div v-if="ungrouped.length === 0" class="text-center py-6">
        <i class="pi pi-check-circle text-4xl text-green-500 mb-3 block"></i>
        <p class="text-lg text-muted-color">Tuyệt vời! Tất cả thành viên đã được phân nhóm.</p>
        <Button label="Đóng" class="mt-4" @click="showAssignDialog = false" />
      </div>

      <div v-else class="flex flex-col gap-4">
        <!-- Thanh công cụ auto-assign -->
        <div class="flex justify-between items-center p-3 rounded-lg bg-orange-50 dark:bg-orange-900/10 border border-orange-200 dark:border-orange-800">
          <div>
            <div class="font-medium text-orange-700 dark:text-orange-400">
              Có <strong class="text-xl">{{ ungrouped.length }}</strong> người chờ phân bổ
            </div>
            <div class="text-xs text-orange-600 dark:text-orange-500 mt-1">Ưu tiên tự động phân bổ đều để đỡ tốn thời gian</div>
          </div>
          <Button
            label="Tự động chia đều"
            icon="pi pi-bolt"
            severity="warn"
            :loading="autoAssigning"
            @click="doAutoAssign"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
          <!-- Bảng danh sách (chiếm 7 cột trên tablet/desktop) -->
          <div class="md:col-span-7 border border-surface-200 dark:border-surface-700 rounded-lg overflow-hidden">
            <DataTable
              v-model:selection="selectedMembers"
              :value="ungrouped"
              dataKey="id"
              size="small"
              scrollable scrollHeight="40vh"
              class="block"
            >
              <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
              <Column field="ho_ten" header="Họ tên">
                <template #body="{ data }">
                  <span class="font-medium">{{ data.ho_ten }}</span>
                  <span v-if="data.phap_danh" class="text-xs text-muted-color ml-1">- {{ data.phap_danh }}</span>
                </template>
              </Column>
              <Column field="phone" header="SĐT" class="text-sm text-muted-color hidden sm:table-cell"></Column>
            </DataTable>
          </div>

          <!-- Form gán thủ công -->
          <div class="md:col-span-5 p-4 rounded-xl border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 flex flex-col justify-center">
            <h4 class="font-bold mb-2">Gán thủ công</h4>
            <div class="text-sm mb-4 text-muted-color">
              Tick chọn <strong class="text-primary">{{ selectedMembers.length }}</strong> người ở bảng bên cạnh, sau đó chọn nhóm để gán.
            </div>
            
            <div class="flex flex-col gap-2 mb-4">
              <label class="text-sm font-medium">Nhóm đích</label>
              <Select
                v-model="targetGroupIdTab0"
                :options="groups"
                optionLabel="ten_nhom"
                optionValue="id"
                placeholder="-- Chọn nhóm --"
                class="w-full"
              >
                <template #option="{ option }">
                  <div class="flex justify-between w-full">
                    <span>{{ option.ten_nhom }}</span>
                    <span class="text-muted-color text-xs ml-2">({{ option.active_count || 0 }})</span>
                  </div>
                </template>
              </Select>
            </div>
            
            <Button
              label="Gán vào nhóm"
              icon="pi pi-check"
              class="w-full"
              :disabled="!selectedMembers.length || !targetGroupIdTab0"
              :loading="saving"
              @click="doManualAssign"
            />
          </div>
        </div>
      </div>
    </Dialog>

    <Toast />
  </div>
</template>
