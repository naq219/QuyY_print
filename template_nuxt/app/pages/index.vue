<script setup>
const { apiFetch } = useApi()
const toast = useToast()
const router = useRouter()

const stats = ref({})
const followUpList = ref([])
const neverContacted = ref([])
const needHelpList = ref([])
const recentNotes = ref([])
const upcomingBirthdays = ref([])
const eventSpotlight = ref(null)
const featured = ref([])
const loading = ref(true)

const phanHoiEmoji = { happy: '🥰', normal: '😊', need_help: '😟', no_contact: '📵' }
const hinhThucEmoji = { call: '📞', message: '💬', visit: '🏠', gift: '🎁', other: '📋' }

const formatPhoneForZalo = (phone) => phone?.startsWith('0') ? '84' + phone.slice(1) : phone

const timeAgo = (dateStr) => {
  if (!dateStr) return ''
  let normalized = dateStr
  if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('T')) {
    normalized = dateStr.replace(' ', 'T') + 'Z'
  }
  const seconds = Math.floor((new Date().getTime() - new Date(normalized).getTime()) / 1000)
  if (seconds < 60) return 'vừa xong'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}ph`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}n`
  const months = Math.floor(days / 30)
  return `${months}th`
}

const coverageColor = computed(() => {
  const p = stats.value.coveragePercent || 0
  if (p >= 70) return 'text-green-600'
  if (p >= 40) return 'text-orange-500'
  return 'text-red-500'
})

const coverageBg = computed(() => {
  const p = stats.value.coveragePercent || 0
  if (p >= 70) return 'bg-green-500'
  if (p >= 40) return 'bg-orange-500'
  return 'bg-red-500'
})

// Care dialog
const showCareDialog = ref(false)
const careTarget = ref(null)
const openCare = (member) => {
  careTarget.value = member
  showCareDialog.value = true
}
const onCareSaved = () => { loadDashboard(); loadFeatured() }

const loadDashboard = async () => {
  loading.value = true
  try {
    const data = await apiFetch('/api/stats')
    const d = data.data
    stats.value = d.stats || {}
    followUpList.value = d.followUpList || []
    neverContacted.value = d.neverContacted || []
    needHelpList.value = d.needHelpList || []
    recentNotes.value = d.recentNotes || []
    upcomingBirthdays.value = d.upcomingBirthdays || []
    eventSpotlight.value = d.eventSpotlight || null
  } catch (e) {
    console.error('Dashboard error:', e)
  }
  loading.value = false
}

const loadFeatured = async () => {
  try {
    const data = await apiFetch('/api/members/featured')
    featured.value = data.data || []
  } catch { featured.value = [] }
}

onMounted(async () => {
  await loadDashboard()
  loadFeatured()
})
</script>

<template>
  <div class="flex flex-col gap-3">

    <!-- ── HEADER: Tổng quan + Link chăm sóc ──────────── -->
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold m-0">Tổng quan</h2>
      <NuxtLink to="/members">
        <Button label="Chăm sóc" icon="pi pi-heart" size="small" severity="help" outlined />
      </NuxtLink>
    </div>

    <!-- ── LOADING ────────────────────────────────────── -->
    <div v-if="loading" class="grid grid-cols-2 gap-2">
      <div v-for="i in 4" :key="i" class="card !p-3 h-20 animate-pulse bg-surface-100 dark:bg-surface-800" />
    </div>

    <template v-else>
      <!-- ═══ STATS CARDS (2x2 trên mobile) ═══ -->
      <div class="grid grid-cols-2 gap-2">
        <!-- Card 1: Thành viên -->
        <NuxtLink to="/members" class="card !p-3 no-underline text-color hover:bg-surface-50 dark:hover:bg-surface-800/70 transition-colors cursor-pointer">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-400/10 flex items-center justify-center flex-shrink-0">
              <i class="pi pi-users text-blue-500 text-sm"></i>
            </div>
            <span class="text-2xl font-bold">{{ stats.totalMembers }}</span>
          </div>
          <div class="text-xs text-muted-color">Thành viên</div>
          <div v-if="stats.newThisMonth" class="text-[0.65rem] text-green-600 font-medium mt-0.5">+{{ stats.newThisMonth }} mới</div>
        </NuxtLink>

        <!-- Card 2: Độ phủ chăm sóc -->
        <NuxtLink to="/members" class="card !p-3 no-underline text-color hover:bg-surface-50 dark:hover:bg-surface-800/70 transition-colors cursor-pointer">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-400/10 flex items-center justify-center flex-shrink-0">
              <i class="pi pi-heart text-green-500 text-sm"></i>
            </div>
            <span class="text-2xl font-bold" :class="coverageColor">{{ stats.coveragePercent }}%</span>
          </div>
          <div class="text-xs text-muted-color">Độ phủ CS</div>
          <div class="w-full bg-surface-200 dark:bg-surface-700 rounded-full h-1.5 mt-1">
            <div class="h-1.5 rounded-full transition-all" :class="coverageBg" :style="{ width: Math.min(stats.coveragePercent, 100) + '%' }"></div>
          </div>
          <div class="text-[0.6rem] text-muted-color mt-0.5">{{ stats.contactedCount }}/{{ stats.activeCount }} đã LH</div>
        </NuxtLink>

        <!-- Card 3: Follow-up hôm nay -->
        <div class="card !p-3 cursor-pointer hover:bg-surface-50 dark:hover:bg-surface-800/70 transition-colors"
             @click="followUpList.length ? null : null">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-400/10 flex items-center justify-center flex-shrink-0">
              <i class="pi pi-clock text-orange-500 text-sm"></i>
            </div>
            <span class="text-2xl font-bold" :class="stats.followUpToday > 0 ? 'text-orange-600' : 'text-muted-color'">{{ stats.followUpToday }}</span>
          </div>
          <div class="text-xs text-muted-color">Follow-up</div>
          <div v-if="stats.followUpToday > 0" class="text-[0.65rem] text-orange-600 font-medium mt-0.5">Cần gọi lại</div>
          <div v-else class="text-[0.65rem] text-green-600 mt-0.5">✓ Không có</div>
        </div>

        <!-- Card 4: Cần hỗ trợ -->
        <div class="card !p-3 cursor-pointer hover:bg-surface-50 dark:hover:bg-surface-800/70 transition-colors">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-8 h-8 rounded-lg" :class="stats.needHelpCount > 0 ? 'bg-red-100 dark:bg-red-400/10' : 'bg-surface-100 dark:bg-surface-800'">
              <div class="w-full h-full flex items-center justify-center">
                <span class="text-sm">😟</span>
              </div>
            </div>
            <span class="text-2xl font-bold" :class="stats.needHelpCount > 0 ? 'text-red-600' : 'text-muted-color'">{{ stats.needHelpCount }}</span>
          </div>
          <div class="text-xs text-muted-color">Cần hỗ trợ</div>
          <div v-if="stats.needHelpCount > 0" class="text-[0.65rem] text-red-500 font-medium mt-0.5">Cần quan tâm!</div>
          <div v-else class="text-[0.65rem] text-green-600 mt-0.5">✓ Tốt</div>
        </div>
      </div>

      <!-- ═══ VIỆC CẦN LÀM HÔM NAY ═══ -->
      <div v-if="followUpList.length > 0 || featured.length > 0" class="card !p-3">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-semibold m-0"><i class="pi pi-list-check mr-1 text-primary"></i>Việc cần làm</h3>
          <NuxtLink to="/members"><Button label="Chăm sóc" text size="small" /></NuxtLink>
        </div>

        <!-- Follow-up quá hạn -->
        <div v-if="followUpList.length" class="flex flex-col gap-1.5 mb-2">
          <div class="text-[0.65rem] text-orange-500 font-medium uppercase tracking-wide">⏰ Cần gọi lại</div>
          <div v-for="f in followUpList" :key="f.id"
            class="flex items-center gap-2 p-2 rounded-lg bg-orange-50 dark:bg-orange-900/10">
            <div class="min-w-0 flex-1">
              <div class="text-sm font-medium truncate">{{ f.ho_ten }}</div>
              <div class="text-[0.6rem] text-muted-color truncate">{{ f.noi_dung }}</div>
            </div>
            <div class="flex gap-0.5 flex-shrink-0">
              <a v-if="f.phone" :href="`tel:${f.phone}`" @click.stop>
                <Button icon="pi pi-phone" text rounded severity="success" size="small" class="!w-8 !h-8" />
              </a>
              <Button icon="pi pi-comment" text rounded severity="warn" size="small" class="!w-8 !h-8"
                @click="openCare(f)" />
            </div>
          </div>
        </div>

        <!-- Gợi ý hỏi thăm -->
        <div v-if="featured.length" class="flex flex-col gap-1.5">
          <div class="text-[0.65rem] text-primary font-medium uppercase tracking-wide">💡 Gợi ý hỏi thăm hôm nay</div>
          <div v-for="f in featured" :key="f.id"
            class="flex items-center gap-2 p-2 rounded-lg bg-primary/5">
            <div class="min-w-0 flex-1">
              <div class="text-sm font-medium truncate">{{ f.ho_ten }}</div>
              <div v-if="f.phone" class="text-[0.6rem] text-muted-color">{{ f.phone }}</div>
              <div v-else class="text-[0.6rem] text-orange-400 italic">Chưa có SĐT</div>
            </div>
            <div class="flex gap-0.5 flex-shrink-0">
              <a v-if="f.phone" :href="`tel:${f.phone}`" @click.stop>
                <Button icon="pi pi-phone" text rounded severity="success" size="small" class="!w-8 !h-8" />
              </a>
              <a v-if="f.phone" :href="`https://zalo.me/${formatPhoneForZalo(f.phone)}`" target="_blank" @click.stop>
                <Button text rounded size="small" class="!w-8 !h-8 !text-blue-600">
                  <template #icon><span class="text-[0.55rem] font-bold">Zalo</span></template>
                </Button>
              </a>
              <Button icon="pi pi-comment" text rounded severity="warn" size="small" class="!w-8 !h-8"
                @click="openCare(f)" />
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ CẢNH BÁO MẤT KẾT NỐI ═══ -->
      <div v-if="neverContacted.length > 0" class="card !p-3">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-semibold m-0"><i class="pi pi-exclamation-triangle mr-1 text-orange-500"></i>Chưa liên hệ</h3>
          <NuxtLink to="/members"><Button label="Xem tất cả" text size="small" /></NuxtLink>
        </div>
        <div class="flex flex-col gap-1">
          <div v-for="m in neverContacted" :key="m.id"
            class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-surface-50 dark:hover:bg-surface-800/50">
            <div class="min-w-0 flex-1">
              <span class="text-sm font-medium">{{ m.ho_ten }}</span>
              <span v-if="m.group_name" class="text-[0.6rem] text-muted-color ml-1">· {{ m.group_name }}</span>
            </div>
            <Tag v-if="m.alert_type === 'never'" value="Chưa từng LH" severity="danger" class="!text-[0.55rem] !py-0 !px-1.5" />
            <Tag v-else :value="timeAgo(m.last_contact) + ' trước'" severity="warn" class="!text-[0.55rem] !py-0 !px-1.5" />
            <Button icon="pi pi-comment" text rounded severity="secondary" size="small" class="!w-7 !h-7"
              @click="openCare(m)" />
          </div>
        </div>
      </div>

      <!-- ═══ SỰ KIỆN SPOTLIGHT ═══ -->
      <div v-if="eventSpotlight" class="card !p-3">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-semibold m-0">🗓 {{ eventSpotlight.ten_su_kien }}</h3>
          <NuxtLink to="/members"><Button label="Chăm sóc SK" text size="small" severity="info" /></NuxtLink>
        </div>
        <div class="text-xs text-muted-color mb-2">
          {{ new Date(eventSpotlight.thoi_gian_bat_dau).toLocaleDateString('vi-VN') }}
          <span v-if="eventSpotlight.dia_diem"> · {{ eventSpotlight.dia_diem }}</span>
        </div>
        <!-- Progress bar -->
        <div class="w-full bg-surface-200 dark:bg-surface-700 rounded-full h-2 mb-1.5">
          <div class="bg-primary h-2 rounded-full transition-all"
            :style="{ width: (eventSpotlight.total_members > 0 ? Math.round(eventSpotlight.contacted_count / eventSpotlight.total_members * 100) : 0) + '%' }">
          </div>
        </div>
        <div class="flex gap-3 text-[0.65rem] text-muted-color">
          <span>Đã LH: <b class="text-primary">{{ eventSpotlight.contacted_count }}</b></span>
          <span>Sẽ đến: <b class="text-green-600">{{ eventSpotlight.se_den }}</b></span>
          <span>K đến: <b class="text-red-500">{{ eventSpotlight.k_den }}</b></span>
        </div>
      </div>

      <!-- ═══ SINH NHẬT TUẦN NÀY ═══ -->
      <div v-if="upcomingBirthdays.length > 0" class="card !p-3">
        <h3 class="text-sm font-semibold m-0 mb-2">🎂 Sinh nhật tuần này</h3>
        <div class="flex flex-col gap-1.5">
          <div v-for="m in upcomingBirthdays" :key="m.id"
            class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-surface-50 dark:hover:bg-surface-800/50">
            <span class="text-lg flex-shrink-0">🎂</span>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-medium truncate">
                {{ m.ho_ten }}
                <span v-if="m.phap_danh" class="text-muted-color font-normal text-xs"> · {{ m.phap_danh }}</span>
              </div>
              <div class="text-[0.6rem] text-muted-color">
                {{ m.birthday_date }}
                <span v-if="m.group_name"> · {{ m.group_name }}</span>
              </div>
            </div>
            <Tag v-if="m.days_until === 0" value="🎉 Hôm nay!" severity="danger" class="!text-[0.6rem] !py-0 !px-1.5" />
            <Tag v-else-if="m.days_until === 1" value="Ngày mai" severity="warn" class="!text-[0.6rem] !py-0 !px-1.5" />
            <Tag v-else :value="`${m.days_until} ngày nữa`" severity="info" class="!text-[0.6rem] !py-0 !px-1.5" />
            <a v-if="m.phone" :href="`tel:${m.phone}`" @click.stop>
              <Button icon="pi pi-phone" text rounded severity="success" size="small" class="!w-7 !h-7" />
            </a>
          </div>
        </div>
      </div>

      <!-- ═══ HOẠT ĐỘNG GẦN ĐÂY ═══ -->
      <div v-if="recentNotes.length > 0" class="card !p-3">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-semibold m-0"><i class="pi pi-comments mr-1 text-muted-color"></i>Gần đây</h3>
          <NuxtLink to="/members"><Button label="Xem tất cả" text size="small" /></NuxtLink>
        </div>
        <div class="flex flex-col gap-1">
          <div v-for="note in recentNotes" :key="note.id"
            class="flex items-center gap-2 py-1 text-xs">
            <span class="flex-shrink-0">{{ hinhThucEmoji[note.hinh_thuc] || '📋' }}</span>
            <span class="font-medium truncate">{{ note.member_name }}</span>
            <span v-if="note.phan_hoi" class="flex-shrink-0">{{ phanHoiEmoji[note.phan_hoi] }}</span>
            <span class="text-muted-color truncate flex-1 min-w-0">{{ note.noi_dung }}</span>
            <span class="text-muted-color flex-shrink-0 whitespace-nowrap">{{ timeAgo(note.thoi_gian) }}</span>
          </div>
        </div>
      </div>

    </template>

    <!-- Care Dialog -->
    <MembersMemberCareDialog
      v-model:visible="showCareDialog"
      :member="careTarget"
      @saved="onCareSaved"
    />

    <Toast />
  </div>
</template>
