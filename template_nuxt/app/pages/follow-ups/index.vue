<script setup lang="ts">
const { apiFetch } = useApi()
const toast = useToast()

const followUps = ref<any[]>([])
const loading = ref(true)

const hinhThucLabel: Record<string, string> = {
  call: '📞 Gọi điện', message: '💬 Nhắn tin', visit: '🏠 Thăm trực tiếp',
  gift: '🎁 Gửi quà', other: '📋 Khác'
}

const phanHoiLabel: Record<string, string> = {
  happy: '😊 Vui vẻ', normal: '😐 Bình thường',
  need_help: '😟 Cần hỗ trợ', no_contact: '📵 Không liên lạc'
}

const loadFollowUps = async () => {
  loading.value = true
  try {
    const data = await apiFetch('/api/follow-ups')
    followUps.value = data.data
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Không tải được', life: 3000 })
  }
  loading.value = false
}

const isOverdue = (date: string) => {
  if (!date) return false
  return new Date(date) < new Date()
}

const isToday = (date: string) => {
  if (!date) return false
  const d = new Date(date)
  const today = new Date()
  return d.toDateString() === today.toDateString()
}

const formatDate = (dt: string) => {
  if (!dt) return 'Chưa đặt ngày'
  return new Date(dt).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatDateTime = (dt: string) => {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleDateString('vi-VN') + ' ' + d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
}

const overdueCount = computed(() => followUps.value.filter((f: any) => f.follow_up_date && isOverdue(f.follow_up_date)).length)
const todayCount = computed(() => followUps.value.filter((f: any) => f.follow_up_date && isToday(f.follow_up_date)).length)

onMounted(loadFollowUps)
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg md:text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">Follow-up</h2>
    </div>

    <!-- Summary inline on mobile -->
    <div class="flex gap-2 mb-3 flex-wrap" v-if="followUps.length">
      <Tag severity="info" class="text-sm">
        <i class="pi pi-list mr-1"></i> {{ followUps.length }} tổng
      </Tag>
      <Tag v-if="overdueCount" severity="danger" class="text-sm">
        🔴 {{ overdueCount }} quá hạn
      </Tag>
      <Tag v-if="todayCount" severity="warn" class="text-sm">
        🟠 {{ todayCount }} hôm nay
      </Tag>
    </div>

    <!-- List -->
    <div v-if="loading" class="flex justify-center py-8"><ProgressSpinner /></div>
    <div v-else-if="followUps.length === 0" class="card text-center py-8">
      <i class="pi pi-check-circle text-4xl mb-3 block text-green-500"></i>
      <p class="text-lg text-muted-color">Không có follow-up nào cần xử lý! 🎉</p>
    </div>
    <div v-else class="flex flex-col gap-3">
      <div v-for="item in followUps" :key="item.id"
        class="card"
        :style="item.follow_up_date && isOverdue(item.follow_up_date) ? 'border-left: 4px solid var(--red-500)' :
                item.follow_up_date && isToday(item.follow_up_date) ? 'border-left: 4px solid var(--orange-500)' : ''">
        <div class="flex justify-between items-start flex-wrap gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <NuxtLink :to="`/members/${item.member_id}`" class="font-semibold text-lg text-primary hover:underline">
                {{ item.ho_ten }}
              </NuxtLink>
              <span v-if="item.phap_danh" class="text-muted-color">({{ item.phap_danh }})</span>
              <Tag :value="item.group_name" severity="secondary" />
            </div>
            <div class="flex items-center gap-4 mb-2 text-sm">
              <span>{{ hinhThucLabel[item.hinh_thuc] || item.hinh_thuc }}</span>
              <span v-if="item.phan_hoi">{{ phanHoiLabel[item.phan_hoi] || item.phan_hoi }}</span>
              <span class="text-muted-color">{{ formatDateTime(item.thoi_gian) }}</span>
              <span class="text-muted-color">bởi {{ item.created_by_name }}</span>
            </div>
            <p class="m-0 text-sm line-clamp-2">{{ item.noi_dung }}</p>
          </div>
          <div class="text-right flex flex-col items-end gap-2">
            <Tag v-if="!item.follow_up_date" value="⏰ Chưa đặt ngày" severity="warn" />
            <Tag v-else-if="isOverdue(item.follow_up_date)" :value="`🔴 Quá hạn: ${formatDate(item.follow_up_date)}`" severity="danger" />
            <Tag v-else-if="isToday(item.follow_up_date)" value="🟠 Hôm nay" severity="warn" />
            <Tag v-else :value="`📅 ${formatDate(item.follow_up_date)}`" severity="info" />
            <div class="flex gap-1">
              <NuxtLink :to="`/members/${item.member_id}`">
                <Button icon="pi pi-eye" text rounded size="small" severity="info" v-tooltip="'Xem thành viên'" />
              </NuxtLink>
              <a v-if="item.phone" :href="`tel:${item.phone}`">
                <Button icon="pi pi-phone" text rounded size="small" severity="success" v-tooltip="'Gọi điện'" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Toast />
  </div>
</template>
