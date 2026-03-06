<script setup>
/**
 * MemberCareDialog — Dialog ghi chú nhanh
 * Mode CSHN: hiện cảm nhận emoji + nội dung
 * Mode Event: hiện trạng thái tham dự + nội dung
 */
const props = defineProps({
  visible: { type: Boolean, default: false },
  member: { type: Object, default: null },
  isEventMode: { type: Boolean, default: false },
  eventName: { type: String, default: '' },
  eventId: { type: String, default: null }
})

const emit = defineEmits(['update:visible', 'saved'])
const { apiFetch } = useApi()
const toast = useToast()

const saving = ref(false)
const form = ref({
  noi_dung: '',
  phan_hoi: null,
  trang_thai_sk: null,
  follow_up: false,
  follow_up_date: null
})

// Reset form khi mở dialog
watch(() => props.visible, (val) => {
  if (val) {
    form.value = {
      noi_dung: '',
      phan_hoi: null,
      trang_thai_sk: props.isEventMode ? 'chua_lien_lac' : null,
      follow_up: false,
      follow_up_date: null
    }
  }
})

// ── Cảm nhận (CSHN mode) ────────────────────────────────────
const phanHoiOptions = [
  { value: 'happy',      label: '🥰', desc: 'Tinh tấn' },
  { value: 'normal',     label: '😊', desc: 'Bình thường' },
  { value: 'need_help',  label: '😟', desc: 'Cần hỗ trợ' },
  { value: 'no_contact', label: '📵', desc: 'K bắt máy' },
]

// ── Trạng thái sự kiện (Event mode) ─────────────────────────
const trangThaiSkOptions = [
  { value: 'se_tham_gia',     label: '✅', desc: 'Sẽ đến' },
  { value: 'khong_tham_gia',  label: '❌', desc: 'Không đến' },
  { value: 'chua_lien_lac',   label: '📵', desc: 'K bắt máy' },
  { value: 'da_tham_gia',     label: '🎯', desc: 'Đã đến' },
]

// Quick text
const quickTexts = computed(() =>
  props.isEventMode
    ? ['Đồng ý tham gia', 'Không nghe máy', 'Không thể đi', 'Sẽ hỏi lại']
    : ['Khoẻ, tinh tấn tu học', 'Đang bận, gọi lại sau', 'Đang ốm', 'Không nghe máy', 'Số sai']
)

const insertQuick = (text) => {
  form.value.noi_dung = form.value.noi_dung
    ? form.value.noi_dung + ', ' + text
    : text
}

const formatPhoneForZalo = (phone) => phone?.startsWith('0') ? '84' + phone.slice(1) : phone

// ── Save ──────────────────────────────────────────────────────
const save = async () => {
  if (!form.value.noi_dung.trim()) {
    toast.add({ severity: 'warn', summary: 'Thiếu nội dung', detail: 'Vui lòng ghi vài chữ', life: 2500 })
    return
  }
  saving.value = true
  try {
    await apiFetch('/api/care-notes', {
      method: 'POST',
      body: {
        member_id: props.member.id,
        hinh_thuc: 'call',
        noi_dung: form.value.noi_dung,
        phan_hoi: props.isEventMode ? null : form.value.phan_hoi,
        follow_up: form.value.follow_up,
        follow_up_date: form.value.follow_up_date instanceof Date
          ? form.value.follow_up_date.toISOString().split('T')[0]
          : form.value.follow_up_date,
        event_id: props.isEventMode ? props.eventId : null,
        trang_thai_sk: props.isEventMode ? form.value.trang_thai_sk : null
      }
    })
    toast.add({ severity: 'success', summary: 'Đã lưu', detail: props.member.ho_ten, life: 2000 })
    emit('update:visible', false)
    emit('saved')
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: e?.data?.message || 'Lưu thất bại', life: 3000 })
  }
  saving.value = false
}
</script>

<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    modal
    :style="{ width: '95vw', maxWidth: '460px' }"
    :pt="{ header: { class: 'pb-2' } }"
  >
    <template #header>
      <div class="flex items-center gap-2 min-w-0 flex-1">
        <i class="pi pi-comment text-primary text-sm flex-shrink-0"></i>
        <div class="min-w-0">
          <p class="font-semibold text-sm leading-tight truncate">{{ member?.ho_ten }}</p>
          <!-- Phone + actions inline -->
          <div v-if="member?.phone" class="flex items-center gap-2 mt-0.5">
            <span class="text-xs text-muted-color">{{ member.phone }}</span>
            <a :href="`tel:${member.phone}`" @click.stop>
              <button class="text-green-600 hover:text-green-700 transition-colors">
                <i class="pi pi-phone text-xs"></i>
              </button>
            </a>
            <a :href="`https://zalo.me/${formatPhoneForZalo(member?.phone)}`" target="_blank" @click.stop>
              <button class="text-blue-600 hover:text-blue-700 text-xs font-bold transition-colors">Z</button>
            </a>
          </div>
          <div v-else class="mt-0.5">
            <span class="text-xs text-orange-400 italic">Chưa có SĐT</span>
          </div>
        </div>
      </div>
    </template>

    <div class="flex flex-col gap-3 pt-1">
      <!-- Badge Event (khi event mode) -->
      <div v-if="isEventMode && eventName" class="flex items-center gap-1.5 px-2 py-1.5 bg-primary/5 rounded-lg text-xs">
        <i class="pi pi-calendar text-primary text-xs"></i>
        <span class="text-primary font-medium truncate">{{ eventName }}</span>
      </div>

      <!-- Cảm nhận / Trạng thái dạng nút Emoji lớn -->
      <div>
        <label class="text-xs text-muted-color font-medium block mb-1.5">
          {{ isEventMode ? 'Trả lời:' : 'Cảm nhận:' }}
        </label>
        <div class="grid grid-cols-4 gap-1.5">
          <template v-if="!isEventMode">
            <button
              v-for="opt in phanHoiOptions" :key="opt.value"
              class="flex flex-col items-center gap-0.5 py-2 px-1 rounded-xl border-2 transition-all text-center"
              :class="form.phan_hoi === opt.value
                ? 'border-primary bg-primary/10'
                : 'border-surface-200 dark:border-surface-700 hover:border-surface-300'"
              @click="form.phan_hoi = opt.value"
            >
              <span class="text-xl leading-none">{{ opt.label }}</span>
              <span class="text-[0.6rem] text-muted-color leading-tight">{{ opt.desc }}</span>
            </button>
          </template>
          <template v-else>
            <button
              v-for="opt in trangThaiSkOptions" :key="opt.value"
              class="flex flex-col items-center gap-0.5 py-2 px-1 rounded-xl border-2 transition-all text-center"
              :class="form.trang_thai_sk === opt.value
                ? 'border-primary bg-primary/10'
                : 'border-surface-200 dark:border-surface-700 hover:border-surface-300'"
              @click="form.trang_thai_sk = opt.value"
            >
              <span class="text-xl leading-none">{{ opt.label }}</span>
              <span class="text-[0.6rem] text-muted-color leading-tight">{{ opt.desc }}</span>
            </button>
          </template>
        </div>
      </div>

      <!-- Quick text chips -->
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="qt in quickTexts" :key="qt"
          class="text-xs px-2.5 py-1 rounded-full border border-surface-200 dark:border-surface-700 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors text-muted-color"
          @click="insertQuick(qt)"
        >{{ qt }}</button>
      </div>

      <!-- Nội dung -->
      <Textarea
        v-model="form.noi_dung"
        :rows="3"
        placeholder="Ghi vài chữ về cuộc hỏi thăm..."
        class="w-full text-sm"
        :pt="{ root: { class: 'resize-none' } }"
      />

      <!-- Follow-up -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <Checkbox v-model="form.follow_up" :binary="true" inputId="fu_check" />
          <label for="fu_check" class="text-sm cursor-pointer">Nhắc gọi lại</label>
        </div>
        <DatePicker
          v-if="form.follow_up"
          v-model="form.follow_up_date"
          dateFormat="dd/mm/yy"
          showIcon
          placeholder="Ngày"
          class="flex-1 text-sm"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex gap-2 justify-end">
        <Button label="Hủy" severity="secondary" text size="small" @click="$emit('update:visible', false)" />
        <Button label="Lưu ghi chú" icon="pi pi-check" size="small" :loading="saving" @click="save" />
      </div>
    </template>
  </Dialog>
</template>
