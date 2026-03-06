<script setup>
const { apiFetch } = useApi()
const toast = useToast()
const router = useRouter()

// ── DATA ─────────────────────────────────────────────────────────────────────
const members = ref([])
const groups = ref([])
const events = ref([])
const loading = ref(false)
const totalRecords = ref(0)

// Featured (CSHN mode)
const featured = ref([])
const featuredLoading = ref(false)

// Pagination
const page = ref(1)
const limit = ref(50)
const first = ref(0)

// ── MODE: Hybrid dropdown (CSHN + events) ─────────────────────────────────────
// selectedMode: '' = CSHN, hoặc event.id
const CSHN_VALUE = '__cshn__'
const selectedMode = ref(CSHN_VALUE)

const isCshnMode = computed(() => selectedMode.value === CSHN_VALUE || selectedMode.value === '')
const isEventMode = computed(() => !isCshnMode.value)
const selectedEvent = computed(() => events.value.find(e => e.id === selectedMode.value) || null)

// Options cho dropdown
const modeOptions = computed(() => [
  { id: CSHN_VALUE, label: '♡ Chăm sóc hàng ngày', isCshn: true },
  ...events.value.map(e => ({ id: e.id, label: `🗓 ${e.ten_su_kien}`, isCshn: false }))
])

const selectedModeLabel = computed(() => {
  if (isCshnMode.value) return '♡ Chăm sóc hàng ngày'
  return selectedEvent.value?.ten_su_kien || 'Chọn mode...'
})

// ── FILTERS ───────────────────────────────────────────────────────────────────
const search = ref('')
const showFilter = ref(false)
const selectedGroup = ref(null)
const selectedStatus = ref(null)

// CSHN filter
const notContactedSince = ref('') // '' | 'never' | '1m' | '3m' | '6m'

// Event filter
const selectedSkFilter = ref('') // '' | 'chua_lien_he' | 'chua_lien_lac' | ...

const activeFilterCount = computed(() => {
  let c = 0
  if (selectedGroup.value) c++
  if (selectedStatus.value) c++
  if (isCshnMode.value && notContactedSince.value) c++
  if (isEventMode.value && selectedSkFilter.value) c++
  return c
})

// ── STATS ─────────────────────────────────────────────────────────────────────
// Được tính từ members data (nếu đủ nhỏ) hoặc API riêng
// Hiện tại tính từ phía server response
const routineStats = ref({ never: 0, over3m: 0, over1m: 0, thisMonth: 0 })
const eventStats = computed(() => {
  if (!isEventMode.value || !members.value.length) return null
  const all = members.value
  return {
    chua_lien_he: all.filter(m => !m.event_trang_thai_sk).length,
    chua_lien_lac: all.filter(m => m.event_trang_thai_sk === 'chua_lien_lac').length,
    se_tham_gia: all.filter(m => m.event_trang_thai_sk === 'se_tham_gia').length,
    khong_tham_gia: all.filter(m => m.event_trang_thai_sk === 'khong_tham_gia').length,
    da_tham_gia: all.filter(m => m.event_trang_thai_sk === 'da_tham_gia').length,
  }
})

// ── LABELS / MAPS ─────────────────────────────────────────────────────────────
const statusOptions = [
  { label: 'Hoạt động', value: 'active' },
  { label: 'Tạm nghỉ', value: 'paused' },
  { label: 'Đã rời', value: 'left' }
]
const statusSeverity = { active: 'success', paused: 'warn', left: 'danger' }
const statusLabel = { active: 'Hoạt động', paused: 'Tạm nghỉ', left: 'Đã rời' }

const skLabel = {
  chua_lien_lac: '📵 Chưa liên lạc',
  se_tham_gia: '✅ Sẽ đến',
  khong_tham_gia: '❌ Không đến',
  da_tham_gia: '🎯 Đã đến'
}
const skSeverity = {
  chua_lien_lac: 'secondary',
  se_tham_gia: 'success',
  khong_tham_gia: 'danger',
  da_tham_gia: 'info'
}

const phanHoiEmoji = {
  happy: '🥰',
  normal: '😊',
  need_help: '😟',
  no_contact: '📵'
}

// ── LOAD ──────────────────────────────────────────────────────────────────────
const loadGroups = async () => {
  try {
    const data = await apiFetch('/api/groups')
    groups.value = data.data || []
  } catch {}
}

const loadEvents = async () => {
  try {
    const data = await apiFetch('/api/events')
    events.value = (data.data || []).filter(e => e.trang_thai !== 'completed')
  } catch {}
}

const loadFeatured = async () => {
  if (!isCshnMode.value) return
  featuredLoading.value = true
  try {
    const data = await apiFetch('/api/members/featured')
    featured.value = data.data || []
  } catch {
    featured.value = []
  }
  featuredLoading.value = false
}

const loadRoutineStats = async () => {
  // Tải stats đơn giản bằng cách query 4 nhóm
  if (!isCshnMode.value) return
  try {
    const [neverRes, over3mRes, over1mRes] = await Promise.all([
      apiFetch('/api/members?not_contacted_since=never&limit=1'),
      apiFetch('/api/members?not_contacted_since=3m&limit=1'),
      apiFetch('/api/members?not_contacted_since=1m&limit=1'),
    ])
    routineStats.value = {
      never: neverRes.meta?.total || 0,
      over3m: over3mRes.meta?.total || 0,
      over1m: over1mRes.meta?.total || 0,
      thisMonth: 0 // TODO
    }
  } catch {}
}

const loadMembers = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('search', search.value)
    if (selectedGroup.value) params.set('group_id', selectedGroup.value)
    if (selectedStatus.value) params.set('trang_thai', selectedStatus.value)
    if (isEventMode.value) {
      params.set('event_id', selectedMode.value)
      if (selectedSkFilter.value) params.set('trang_thai_sk', selectedSkFilter.value)
    }
    if (isCshnMode.value && notContactedSince.value) {
      params.set('not_contacted_since', notContactedSince.value)
    }
    params.set('page', String(page.value))
    params.set('limit', String(limit.value))

    const data = await apiFetch(`/api/members?${params}`)
    members.value = data.data || []
    totalRecords.value = data.meta?.total || 0
  } catch {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: 'Không tải được danh sách', life: 3000 })
  }
  loading.value = false
}

const onModeChange = async () => {
  // Reset filters khi chuyển mode
  notContactedSince.value = ''
  selectedSkFilter.value = ''
  selectedGroup.value = null
  selectedStatus.value = null
  page.value = 1
  first.value = 0
  showFilter.value = false

  await loadMembers()
  if (isCshnMode.value) {
    loadFeatured()
    loadRoutineStats()
  }
}

// Stat chip click → set filter + reload
const applyStatFilter = (filter) => {
  if (isCshnMode.value) {
    notContactedSince.value = notContactedSince.value === filter ? '' : filter
  } else {
    selectedSkFilter.value = selectedSkFilter.value === filter ? '' : filter
  }
  page.value = 1; first.value = 0
  loadMembers()
}

// ── CARE DIALOG ───────────────────────────────────────────────────────────────
const showCareDialog = ref(false)
const careTarget = ref(null)

// Detail Dialog
const showDetailDialog = ref(false)
const detailMemberId = ref(null)

const openCare = (member) => {
  careTarget.value = member
  showCareDialog.value = true
}

const onCareSaved = () => {
  loadMembers()
  if (isCshnMode.value) {
    loadFeatured()
    loadRoutineStats()
  }
}

const openDetail = (member) => {
  detailMemberId.value = member.id
  showDetailDialog.value = true
}

const onDetailCare = (member) => {
  showDetailDialog.value = false
  openCare(member)
}

// ── TIME UTIL ─────────────────────────────────────────────────────────────────
const timeAgo = (dateStr) => {
  if (!dateStr) return null
  let normalized = dateStr
  if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('T')) {
    normalized = dateStr.replace(' ', 'T') + 'Z'
  }
  const seconds = Math.floor((new Date().getTime() - new Date(normalized).getTime()) / 1000)
  if (seconds < 60) return 'vừa xong'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes} phút`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} giờ`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}n`
  const months = Math.floor(days / 30)
  if (months < 12) return `${months}th`
  return `${Math.floor(months / 12)}năm`
}

const formatPhoneForZalo = (phone) => phone?.startsWith('0') ? '84' + phone.slice(1) : phone
const copyPhone = async (phone, e) => {
  e.stopPropagation()
  try {
    await navigator.clipboard.writeText(phone)
    toast.add({ severity: 'success', summary: 'Đã copy', detail: phone, life: 1500 })
  } catch {}
}

// ── PAGINATION ────────────────────────────────────────────────────────────────
const onPageChange = (event) => {
  page.value = event.page + 1
  first.value = event.first
  limit.value = event.rows
  loadMembers()
}

// ── SEARCH debounce ───────────────────────────────────────────────────────────
let searchTimeout
const onSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { page.value = 1; first.value = 0; loadMembers() }, 400)
}

// ── INIT ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([loadGroups(), loadEvents()])
  await loadMembers()
  loadFeatured()
  loadRoutineStats()
})

watch([selectedGroup, selectedStatus], () => {
  page.value = 1; first.value = 0; loadMembers()
})
</script>

<template>
  <div class="flex flex-col gap-2">

    <!-- ── ROW 1: Dropdown Mode + Filter Icon ────────────────────────── -->
    <div class="flex gap-2 items-center">
      <!-- Dropdown Hybrid: CSHN + Events -->
      <Select
        v-model="selectedMode"
        :options="modeOptions"
        option-label="label"
        option-value="id"
        class="flex-1 min-w-0"
        @change="onModeChange"
        :pt="{
          label: { class: isCshnMode ? 'text-primary font-semibold' : '' }
        }"
      >
        <template #value>
          <span :class="isCshnMode ? 'text-primary font-semibold' : ''">
            <span v-if="isCshnMode">♡ Chăm sóc hàng ngày</span>
            <span v-else class="truncate">🗓 {{ selectedEvent?.ten_su_kien }}</span>
          </span>
        </template>
        <template #option="{ option }">
          <div :class="option.isCshn ? 'font-semibold text-primary py-0.5' : ''">
            {{ option.label }}
          </div>
          <div v-if="option.isCshn" class="border-b border-surface-200 dark:border-surface-700 mt-1.5 mb-0.5 -mx-3"></div>
        </template>
      </Select>

      <!-- Icon Filter -->
      <Button
        :icon="showFilter ? 'pi pi-filter-slash' : 'pi pi-filter'"
        :severity="activeFilterCount ? 'warn' : 'secondary'"
        :badge="activeFilterCount ? String(activeFilterCount) : undefined"
        :outlined="!activeFilterCount"
        rounded
        @click="showFilter = !showFilter"
      />
    </div>

    <!-- ── ROW 2: Search ──────────────────────────────────────────────── -->
    <IconField>
      <InputIcon class="pi pi-search" />
      <InputText
        v-model="search"
        placeholder="Tìm tên, SĐT, pháp danh..."
        class="w-full"
        @input="onSearch"
      />
    </IconField>

    <!-- ── STATS ROW ──────────────────────────────────────────────────── -->
    <!-- CSHN Stats -->
    <div v-if="isCshnMode" class="flex gap-1.5 overflow-x-auto scrollbar-none">
      <button
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all border"
        :class="notContactedSince === 'never'
          ? 'bg-orange-500 text-white border-orange-500'
          : 'bg-surface-100 dark:bg-surface-800 border-surface-200 dark:border-surface-700 text-muted-color'"
        @click="applyStatFilter('never')"
      >
        Chưa bao giờ<span class="ml-1 font-bold">{{ routineStats.never }}</span>
      </button>
      <button
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all border"
        :class="notContactedSince === '3m'
          ? 'bg-amber-500 text-white border-amber-500'
          : 'bg-surface-100 dark:bg-surface-800 border-surface-200 dark:border-surface-700 text-muted-color'"
        @click="applyStatFilter('3m')"
      >
        &gt;3 tháng<span class="ml-1 font-bold">{{ routineStats.over3m }}</span>
      </button>
      <button
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all border"
        :class="notContactedSince === '1m'
          ? 'bg-blue-500 text-white border-blue-500'
          : 'bg-surface-100 dark:bg-surface-800 border-surface-200 dark:border-surface-700 text-muted-color'"
        @click="applyStatFilter('1m')"
      >
        &gt;1 tháng<span class="ml-1 font-bold">{{ routineStats.over1m }}</span>
      </button>
    </div>

    <!-- Event Stats -->
    <div v-if="isEventMode && eventStats" class="flex gap-1.5 overflow-x-auto scrollbar-none">
      <button
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all border"
        :class="selectedSkFilter === 'chua_lien_he'
          ? 'bg-surface-500 text-white border-surface-500'
          : 'bg-surface-100 dark:bg-surface-800 border-surface-200 dark:border-surface-700 text-muted-color'"
        @click="applyStatFilter('chua_lien_he')"
      >— Chưa LH<span class="ml-1 font-bold">{{ eventStats.chua_lien_he }}</span></button>
      <button
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all border"
        :class="selectedSkFilter === 'chua_lien_lac'
          ? 'bg-orange-500 text-white border-orange-500'
          : 'bg-surface-100 dark:bg-surface-800 border-surface-200 dark:border-surface-700 text-muted-color'"
        @click="applyStatFilter('chua_lien_lac')"
      >📵 K liên lạc<span class="ml-1 font-bold">{{ eventStats.chua_lien_lac }}</span></button>
      <button
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all border"
        :class="selectedSkFilter === 'se_tham_gia'
          ? 'bg-green-500 text-white border-green-500'
          : 'bg-surface-100 dark:bg-surface-800 border-surface-200 dark:border-surface-700 text-muted-color'"
        @click="applyStatFilter('se_tham_gia')"
      >✅ Sẽ đến<span class="ml-1 font-bold">{{ eventStats.se_tham_gia }}</span></button>
      <button
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all border"
        :class="selectedSkFilter === 'khong_tham_gia'
          ? 'bg-red-500 text-white border-red-500'
          : 'bg-surface-100 dark:bg-surface-800 border-surface-200 dark:border-surface-700 text-muted-color'"
        @click="applyStatFilter('khong_tham_gia')"
      >❌ K đến<span class="ml-1 font-bold">{{ eventStats.khong_tham_gia }}</span></button>
    </div>

    <!-- ── FEATURED CARD (CSHN mode only) ────────────────────────────── -->
    <MembersMemberFeaturedCard
      v-if="isCshnMode"
      :members="featured"
      :loading="featuredLoading"
      @care="openCare"
      @refresh="loadFeatured"
    />

    <!-- ── FILTER PANEL (slide down) ─────────────────────────────────── -->
    <Transition name="slide-down">
      <div v-show="showFilter" class="card !p-3 flex flex-wrap gap-2">
        <Select
          v-model="selectedGroup"
          :options="[{ ten_nhom: 'Tất cả nhóm', id: null }, ...groups]"
          option-label="ten_nhom"
          option-value="id"
          class="flex-1 min-w-36"
          placeholder="Tất cả nhóm"
          show-clear
        />
        <Select
          v-model="selectedStatus"
          :options="statusOptions"
          option-label="label"
          option-value="value"
          class="flex-1 min-w-32"
          placeholder="Trạng thái"
          show-clear
        />
      </div>
    </Transition>

    <!-- ── MEMBER LIST ────────────────────────────────────────────────── -->
    <!-- Loading -->
    <div v-if="loading" class="flex flex-col gap-2">
      <div v-for="i in 5" :key="i" class="card !p-3 h-20 animate-pulse bg-surface-100 dark:bg-surface-800" />
    </div>

    <!-- Empty state -->
    <div v-else-if="members.length === 0" class="card text-center py-10 flex flex-col items-center gap-3">
      <div class="w-14 h-14 rounded-full bg-surface-100 dark:bg-surface-800 flex items-center justify-center">
        <i class="pi pi-users text-2xl text-muted-color"></i>
      </div>
      <div>
        <p class="text-muted-color text-sm">Không tìm thấy thành viên nào</p>
        <p v-if="activeFilterCount" class="text-xs text-muted-color mt-1">Thử xóa bộ lọc để xem thêm</p>
      </div>
      <NuxtLink v-if="!search && !activeFilterCount" to="/members/create">
        <Button label="+ Thêm thành viên" icon="pi pi-user-plus" size="small" />
      </NuxtLink>
    </div>

    <!-- Cards -->
    <div v-else class="flex flex-col gap-2">
      <div
        v-for="m in members"
        :key="m.id"
        class="card !p-3 cursor-pointer hover:bg-surface-50 dark:hover:bg-surface-800/70 transition-colors"
        @click="openDetail(m)"
      >
        <!-- ── Dòng 1: Tên - Pháp danh | Thời gian ────────────────── -->
        <div class="flex items-center justify-between gap-2">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="font-semibold text-sm leading-tight">{{ m.ho_ten }}</span>
              <span v-if="m.phap_danh" class="text-xs text-muted-color">· {{ m.phap_danh }}</span>
              <Tag v-if="m.trang_thai !== 'active'"
                :value="statusLabel[m.trang_thai]"
                :severity="statusSeverity[m.trang_thai]"
                class="!text-[0.6rem] !py-0 !px-1.5" />
            </div>
          </div>
          <div class="flex items-center gap-1 flex-shrink-0">
            <span v-if="isCshnMode && m.last_contact_date"
              class="text-[0.65rem] text-muted-color whitespace-nowrap">
              {{ timeAgo(m.last_contact_date) }} trước
            </span>
            <span v-else-if="isCshnMode && !m.last_contact_date"
              class="text-[0.65rem] text-orange-500 font-medium whitespace-nowrap">Chưa LH</span>
            <span v-else-if="isEventMode && m.event_thoi_gian_lien_he"
              class="text-[0.65rem] text-muted-color whitespace-nowrap">
              {{ timeAgo(m.event_thoi_gian_lien_he) }}
            </span>
          </div>
        </div>

        <!-- ── Dòng 2: SĐT + badge | icons ──────────────────────────── -->
        <div class="flex items-center justify-between gap-2 mt-0.5">
          <div class="flex items-center gap-2 min-w-0">
            <span v-if="m.phone" class="text-xs text-muted-color">{{ m.phone }}</span>
            <span v-else class="text-xs text-orange-400 italic">Chưa có SĐT</span>
            <Tag v-if="isEventMode && m.event_trang_thai_sk"
              :value="skLabel[m.event_trang_thai_sk]"
              :severity="skSeverity[m.event_trang_thai_sk]"
              class="!text-[0.6rem] !py-0 !px-1.5" />
            <span v-else-if="isEventMode" class="text-[0.65rem] text-muted-color italic">— Chưa LH</span>
            <span v-else-if="isCshnMode && m.recent_activities?.[0]?.phan_hoi" class="text-sm leading-none">
              {{ phanHoiEmoji[m.recent_activities[0].phan_hoi] }}
            </span>
          </div>
          <div class="flex items-center gap-0 flex-shrink-0">
            <a v-if="m.phone" :href="`tel:${m.phone}`" @click.stop>
              <Button icon="pi pi-phone" text rounded severity="success" class="!w-14 !h-14 !text-lg" />
            </a>
            <Button v-else icon="pi pi-phone" text rounded severity="secondary" class="!w-14 !h-14 !text-lg opacity-40"
              @click.stop="toast.add({ severity: 'info', summary: 'Không có SĐT', detail: `${m.ho_ten} chưa có số điện thoại`, life: 2500 })" />
            <a v-if="m.phone" :href="`https://zalo.me/${formatPhoneForZalo(m.phone)}`" target="_blank" @click.stop>
              <Button text rounded class="!w-14 !h-14 !text-blue-600 !font-bold">
                <template #icon><span class="text-sm font-bold">Zalo</span></template>
              </Button>
            </a>
            <Button v-else text rounded class="!w-14 !h-14 !font-bold opacity-40"
              @click.stop="toast.add({ severity: 'info', summary: 'Không có SĐT', detail: `${m.ho_ten} chưa có số điện thoại`, life: 2500 })">
              <template #icon><span class="text-sm font-bold text-muted-color">Zalo</span></template>
            </Button>
            <Button v-if="m.phone" icon="pi pi-copy" text rounded severity="secondary"
              class="!w-14 !h-14 !text-lg" @click.stop="copyPhone(m.phone, $event)" />
            <Button icon="pi pi-comment"
              :severity="isEventMode ? 'warn' : 'secondary'"
              text rounded class="!w-14 !h-14 !text-lg"
              @click.stop="openCare(m)" />
          </div>
        </div>

        <!-- ── Ghi chú chăm sóc gần nhất (tối đa 3) ─────────────── -->
        <div
          v-if="m.recent_activities?.length"
          class="mt-2 pt-2 border-t border-surface-100 dark:border-surface-700 flex flex-col gap-1"
        >
          <div
            v-for="(act, i) in m.recent_activities"
            :key="i"
            class="flex items-start gap-1.5 text-xs text-muted-color"
          >
            <i :class="act.type === 'attendance' ? 'pi pi-calendar text-primary' : 'pi pi-comment text-surface-400'"
              class="mt-0.5 shrink-0 text-[0.6rem]"></i>
            <span class="min-w-0 leading-relaxed">
              <!-- Prefix tên sự kiện cho care note gắn event (CSHN mode hiện cả 2 loại) -->
              <span v-if="act.event_name && act.type !== 'attendance'"
                class="font-medium text-primary/70 mr-1">[{{ act.event_name }}]</span>
              <span v-if="act.type === 'attendance'" class="italic">Tham gia: {{ act.noi_dung }}</span>
              <span v-else>{{ act.noi_dung }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <Paginator
      v-if="totalRecords > limit"
      :rows="limit"
      :totalRecords="totalRecords"
      :first="first"
      :rowsPerPageOptions="[20, 50, 100]"
      @page="onPageChange"
      class="mt-1"
      template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
    />
    <div v-if="members.length" class="text-xs text-muted-color text-center">
      {{ members.length }} / {{ totalRecords }} thành viên
    </div>

    <!-- Care Dialog -->
    <MembersMemberCareDialog
      v-model:visible="showCareDialog"
      :member="careTarget"
      :is-event-mode="isEventMode"
      :event-name="selectedEvent?.ten_su_kien"
      :event-id="isEventMode ? selectedMode : null"
      @saved="onCareSaved"
    />

    <!-- Detail Dialog -->
    <MembersMemberDetailDialog
      v-model:visible="showDetailDialog"
      :member-id="detailMemberId"
      @care="onDetailCare"
      @updated="onCareSaved"
    />

    <Toast />
  </div>
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

.scrollbar-none {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
</style>
