<script setup lang="ts">
const route = useRoute()
const { apiFetch } = useApi()
const { user } = useAuth()
const toast = useToast()

const eventData = ref<any>(null)
const attendees = ref<any[]>([])
const careStats = ref<any>(null)
const careMembers = ref<any[]>([])
const loading = ref(true)
const activeTab = ref(0)

const showCheckinDialog = ref(false)
const memberSearch = ref('')
const memberResults = ref<any[]>([])
const searching = ref(false)
const checkinLoading = ref(false)

const loaiHinhLabel: Record<string, string> = {
  tung_kinh: '🙏 Tụng kinh', thien_nguyen: '💝 Thiện nguyện',
  khoa_tu: '🧘 Khóa tu', le_hoi: '🎉 Lễ hội', khac: '📋 Khác'
}
const statusLabel: Record<string, string> = {
  planned: '📋 Lên kế hoạch', ongoing: '▶️ Đang diễn ra',
  completed: '✅ Đã kết thúc', cancelled: '❌ Hủy'
}
const statusSeverity: Record<string, string> = {
  planned: 'info', ongoing: 'warn', completed: 'success', cancelled: 'danger'
}
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

const loadEvent = async () => {
  loading.value = true
  try {
    const data = await apiFetch(`/api/events/${route.params.id}`)
    const detail = data.data
    eventData.value = detail
    attendees.value = detail.attendees || []
    careStats.value = detail.care_stats || null
    careMembers.value = detail.care_members || []
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Không tải được', life: 3000 })
  }
  loading.value = false
}

const searchMembers = async () => {
  if (!memberSearch.value || memberSearch.value.length < 2) { memberResults.value = []; return }
  searching.value = true
  try {
    const data = await apiFetch(`/api/members?search=${encodeURIComponent(memberSearch.value)}&limit=10`)
    const attendedIds = new Set(attendees.value.map((a: any) => a.member_id))
    memberResults.value = data.data.map((m: any) => ({ ...m, already: attendedIds.has(m.id) }))
  } catch { memberResults.value = [] }
  searching.value = false
}

const checkinMember = async (memberId: string) => {
  checkinLoading.value = true
  try {
    await apiFetch('/api/attendance', { method: 'POST', body: { event_id: route.params.id, member_id: memberId } })
    toast.add({ severity: 'success', summary: 'Điểm danh thành công', life: 2000 })
    loadEvent()
    searchMembers()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message, life: 3000 })
  }
  checkinLoading.value = false
}

const removeAttendance = async (attendanceId: string) => {
  if (!confirm('Hủy điểm danh?')) return
  try {
    await apiFetch(`/api/attendance/${attendanceId}`, { method: 'DELETE' })
    toast.add({ severity: 'success', summary: 'Đã hủy', life: 2000 })
    loadEvent()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message, life: 3000 })
  }
}

const formatDate = (d: string) => {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }
  catch { return d }
}

// Tỉ lệ chăm sóc
const carePercent = computed(() => {
  if (!careStats.value || !careStats.value.tong_lien_he) return 0
  const total = (careStats.value.se_tham_gia || 0) + (careStats.value.khong_tham_gia || 0) +
    (careStats.value.da_tham_gia || 0) + (careStats.value.chua_lien_lac || 0)
  return total
})

let searchTimeout: any = null
watch(memberSearch, () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(searchMembers, 300) })
onMounted(loadEvent)
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8"><ProgressSpinner /></div>

    <template v-else-if="eventData">
      <!-- Header -->
      <div class="flex justify-between items-start mb-4">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <Button icon="pi pi-arrow-left" text rounded @click="$router.push('/events')" />
            <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-0">{{ eventData.ten_su_kien }}</h2>
          </div>
          <div class="flex items-center gap-3 ml-12">
            <Tag :value="loaiHinhLabel[eventData.loai_hinh]" severity="secondary" />
            <Tag :value="statusLabel[eventData.trang_thai]" :severity="statusSeverity[eventData.trang_thai]" />
          </div>
        </div>
        <Button label="Điểm danh" icon="pi pi-check-square" @click="showCheckinDialog = true"
          :disabled="eventData.trang_thai === 'cancelled'" />
      </div>

      <!-- Thông tin sự kiện -->
      <div class="card mb-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><div class="text-muted-color text-sm mb-1">Thời gian bắt đầu</div><div class="font-medium">{{ formatDate(eventData.thoi_gian_bat_dau) }}</div></div>
          <div><div class="text-muted-color text-sm mb-1">Thời gian kết thúc</div><div class="font-medium">{{ eventData.thoi_gian_ket_thuc ? formatDate(eventData.thoi_gian_ket_thuc) : '—' }}</div></div>
          <div><div class="text-muted-color text-sm mb-1">Địa điểm</div><div class="font-medium">{{ eventData.dia_diem || '—' }}</div></div>
        </div>
        <div v-if="eventData.mo_ta" class="mt-4 pt-4 border-t border-surface-200 dark:border-surface-700">
          <div class="text-muted-color text-sm mb-1">Mô tả</div>
          <div>{{ eventData.mo_ta }}</div>
        </div>
      </div>

      <!-- Tabs: Điểm danh | Chăm sóc -->
      <Tabs v-model:value="activeTab">
        <TabList>
          <Tab :value="0">
            <i class="pi pi-check-square mr-2"></i>Điểm danh
            <Badge :value="attendees.length" severity="success" class="ml-2" />
          </Tab>
          <Tab :value="1">
            <i class="pi pi-phone mr-2"></i>Chăm sóc
            <Badge v-if="careStats?.tong_lien_he" :value="careStats.tong_lien_he" severity="info" class="ml-2" />
          </Tab>
        </TabList>

        <TabPanels>
          <!-- Tab Điểm danh -->
          <TabPanel :value="0">
            <div class="card mt-4">
              <div class="flex justify-between items-center mb-3">
                <h3 class="text-lg font-semibold">Đã điểm danh <Badge :value="attendees.length" severity="info" class="ml-2" /></h3>
              </div>
              <DataTable :value="attendees" stripedRows>
                <template #empty>Chưa có ai điểm danh</template>
                <Column field="ho_ten" header="Họ tên">
                  <template #body="{ data }">
                    <NuxtLink :to="`/members/${data.member_id}`" class="font-semibold text-primary hover:underline">
                      {{ data.ho_ten }}
                    </NuxtLink>
                    <span v-if="data.phap_danh" class="text-sm text-muted-color ml-2">({{ data.phap_danh }})</span>
                  </template>
                </Column>
                <Column field="group_name" header="Nhóm" />
                <Column field="phone" header="SĐT" />
                <Column field="checked_in_at" header="Thời gian">
                  <template #body="{ data }">{{ formatDate(data.checked_in_at) }}</template>
                </Column>
                <Column field="checked_in_by_name" header="Người điểm danh" />
                <Column header="" style="width: 60px">
                  <template #body="{ data }">
                    <Button icon="pi pi-times" text rounded severity="danger" size="small" @click="removeAttendance(data.id)" />
                  </template>
                </Column>
              </DataTable>
            </div>
          </TabPanel>

          <!-- Tab Chăm sóc -->
          <TabPanel :value="1">
            <div class="mt-4">
              <!-- Thống kê cards -->
              <div v-if="careStats" class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
                <div class="card text-center p-4 border-l-4 border-orange-400">
                  <div class="text-3xl font-bold text-orange-500">{{ careStats.chua_lien_lac || 0 }}</div>
                  <div class="text-sm text-muted-color mt-1">📵 Chưa liên lạc</div>
                </div>
                <div class="card text-center p-4 border-l-4 border-green-400">
                  <div class="text-3xl font-bold text-green-500">{{ careStats.se_tham_gia || 0 }}</div>
                  <div class="text-sm text-muted-color mt-1">✅ Sẽ tham gia</div>
                </div>
                <div class="card text-center p-4 border-l-4 border-red-400">
                  <div class="text-3xl font-bold text-red-500">{{ careStats.khong_tham_gia || 0 }}</div>
                  <div class="text-sm text-muted-color mt-1">❌ Không tham gia</div>
                </div>
                <div class="card text-center p-4 border-l-4 border-blue-400">
                  <div class="text-3xl font-bold text-blue-500">{{ careStats.da_tham_gia || 0 }}</div>
                  <div class="text-sm text-muted-color mt-1">🎯 Đã tham gia</div>
                </div>
                <div class="card text-center p-4 bg-primary/5 border-l-4 border-primary">
                  <div class="text-3xl font-bold text-primary">{{ attendees.length }}</div>
                  <div class="text-sm text-muted-color mt-1">🏁 Check-in thực tế</div>
                </div>
              </div>

              <!-- So sánh tổng -->
              <div v-if="careStats" class="card mb-4 p-4 bg-surface-50 dark:bg-surface-800">
                <div class="flex items-center gap-6 flex-wrap text-sm">
                  <span>📞 Đã liên hệ: <strong>{{ careStats.tong_lien_he }}</strong> người</span>
                  <span>→</span>
                  <span>✅ Cam kết tham gia: <strong>{{ (careStats.se_tham_gia || 0) + (careStats.da_tham_gia || 0) }}</strong> người</span>
                  <span>→</span>
                  <span>🏁 Check-in thực tế: <strong>{{ attendees.length }}</strong> người</span>
                </div>
              </div>

              <!-- Danh sách thành viên đã được chăm sóc -->
              <div class="card">
                <h3 class="text-lg font-semibold mb-3">Danh sách đã liên hệ</h3>
                <DataTable :value="careMembers" stripedRows>
                  <template #empty>
                    <div class="text-center py-6 text-muted-color">
                      <i class="pi pi-phone text-3xl mb-2 block"></i>
                      Chưa có ai được chăm sóc cho sự kiện này.<br>
                      Mở trang thành viên → chọn sự kiện → ghi chú chăm sóc.
                    </div>
                  </template>
                  <Column field="ho_ten" header="Họ tên">
                    <template #body="{ data }">
                      <NuxtLink :to="`/members/${data.member_id}`" class="font-semibold text-primary hover:underline">
                        {{ data.ho_ten }}
                      </NuxtLink>
                      <span v-if="data.phap_danh" class="text-sm text-muted-color ml-2">({{ data.phap_danh }})</span>
                    </template>
                  </Column>
                  <Column field="group_name" header="Nhóm" />
                  <Column field="phone" header="SĐT" />
                  <Column field="trang_thai_sk" header="Trạng thái cam kết">
                    <template #body="{ data }">
                      <Tag v-if="data.trang_thai_sk"
                        :value="trangThaiSkLabel[data.trang_thai_sk]"
                        :severity="trangThaiSkSeverity[data.trang_thai_sk]" />
                      <span v-else class="text-muted-color">—</span>
                    </template>
                  </Column>
                  <Column field="da_checkin" header="Check-in">
                    <template #body="{ data }">
                      <Tag v-if="data.da_checkin" value="✅ Đã check-in" severity="success" />
                      <span v-else class="text-muted-color text-sm">Chưa</span>
                    </template>
                  </Column>
                  <Column field="ghi_chu_moi_nhat" header="Ghi chú mới nhất">
                    <template #body="{ data }">
                      <span class="text-sm truncate block max-w-48" :title="data.ghi_chu_moi_nhat">
                        {{ data.ghi_chu_moi_nhat || '—' }}
                      </span>
                    </template>
                  </Column>
                  <Column field="thoi_gian_lien_he" header="Lần liên hệ cuối">
                    <template #body="{ data }">
                      <span class="text-sm">{{ formatDate(data.thoi_gian_lien_he) }}</span>
                    </template>
                  </Column>
                </DataTable>
              </div>
            </div>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </template>

    <!-- Dialog điểm danh -->
    <Dialog v-model:visible="showCheckinDialog" header="Điểm danh thành viên" modal :style="{ width: '520px' }">
      <div class="flex flex-col gap-4 pt-2">
        <div class="flex flex-col gap-2">
          <label class="font-medium">Tìm thành viên (theo tên/SĐT)</label>
          <InputText v-model="memberSearch" class="w-full" placeholder="Nhập ít nhất 2 ký tự..." autofocus />
        </div>
        <div v-if="searching" class="flex justify-center py-4"><ProgressSpinner style="width: 30px; height: 30px" /></div>
        <div v-else-if="memberResults.length" class="flex flex-col gap-2 max-h-80 overflow-y-auto">
          <div v-for="m in memberResults" :key="m.id"
            class="flex items-center justify-between p-3 rounded-border border border-surface-200 dark:border-surface-700"
            :class="{ 'bg-green-50 dark:bg-green-900/20': m.already }">
            <div>
              <div class="font-medium">{{ m.ho_ten }} <span v-if="m.phap_danh" class="text-muted-color">({{ m.phap_danh }})</span></div>
              <div class="text-sm text-muted-color">{{ m.phone }} • {{ m.group_name }}</div>
            </div>
            <div>
              <Tag v-if="m.already" value="✅ Đã điểm danh" severity="success" />
              <Button v-else label="Điểm danh" icon="pi pi-check" size="small" :loading="checkinLoading"
                @click="checkinMember(m.id)" />
            </div>
          </div>
        </div>
        <div v-else-if="memberSearch.length >= 2" class="text-center text-muted-color py-4">
          Không tìm thấy thành viên
        </div>
      </div>
    </Dialog>

    <Toast />
  </div>
</template>
