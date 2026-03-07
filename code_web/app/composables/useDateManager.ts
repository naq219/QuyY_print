import type { LunarResult } from '~/composables/useLunarConverter'

/**
 * Composable quản lý ngày quy y, chuyển đổi âm lịch, Phật lịch
 */
export function useDateManager(config: Ref<any>) {
    const toast = useToast()
    const { convertDate } = useLunarConverter()
    const { updateDateFields, clearDateFields } = useConfigManager()

    // State
    const selectedDate = ref<Date | null>(null)
    const lunarInfo = ref<LunarResult | null>(null)
    const highlightDate = ref(false)

    // Computed
    const lunarDisplayText = computed(() => {
        if (!lunarInfo.value) return ''
        const li = lunarInfo.value
        return `${li.lunar_day}/${li.lunar_month} ${li.lunar_year_name}`
    })

    // Functions
    function formatDateISO(d: Date): string {
        const y = d.getFullYear()
        const m = String(d.getMonth() + 1).padStart(2, '0')
        const dd = String(d.getDate()).padStart(2, '0')
        return `${y}-${m}-${dd}`
    }

    function onDateChange() {
        if (!selectedDate.value) {
            lunarInfo.value = null
            clearDateFields()
            return
        }
        try {
            const dateStr = formatDateISO(selectedDate.value)
            const info = convertDate(dateStr)
            lunarInfo.value = info
            updateDateFields(info)
            toast.add({ severity: 'success', summary: 'Đã chọn ngày', detail: `Âm lịch: ${info.lunar_day}/${info.lunar_month} ${info.lunar_year_name} - PL ${info.buddhist_year}`, life: 3000 })
        } catch {
            toast.add({ severity: 'error', summary: 'Lỗi', detail: 'Không thể chuyển đổi ngày', life: 3000 })
        }
    }

    function clearDate() {
        selectedDate.value = null
        lunarInfo.value = null
        clearDateFields()
    }

    function onLunarTextChange(text: string) {
        const parts = text.trim().split(/[\s/]+/)
        if (parts.length >= 2) {
            const day = parts[0]!
            const month = parts[1]!
            const yearName = parts.slice(2).join(' ')
            if (config.value.custom_fields.ngay_am) config.value.custom_fields.ngay_am.value = day
            if (config.value.custom_fields.thang_am) config.value.custom_fields.thang_am.value = month
            if (yearName && config.value.custom_fields.nam_am) config.value.custom_fields.nam_am.value = yearName
            if (lunarInfo.value) {
                lunarInfo.value = { ...lunarInfo.value, lunar_day: parseInt(day) || 0, lunar_month: parseInt(month) || 0, lunar_year_name: yearName || lunarInfo.value.lunar_year_name }
            }
            toast.add({ severity: 'success', summary: 'Đã sửa âm lịch', detail: text, life: 1500 })
        }
    }

    function onBuddhistYearChange(text: string) {
        const val = text.trim()
        if (config.value.custom_fields.phat_lich) {
            config.value.custom_fields.phat_lich.value = val
        }
        if (lunarInfo.value) {
            lunarInfo.value = { ...lunarInfo.value, buddhist_year: parseInt(val) || 0 }
        }
        toast.add({ severity: 'success', summary: 'Đã sửa Phật lịch', detail: val, life: 1500 })
    }

    function highlightDatePicker() {
        toast.add({ severity: 'warn', summary: 'Chưa chọn ngày', detail: 'Vui lòng chọn Ngày Quy Y trước', life: 3000 })
        highlightDate.value = true
        setTimeout(() => { highlightDate.value = false }, 3000)
    }

    return {
        selectedDate,
        lunarInfo,
        highlightDate,
        lunarDisplayText,
        onDateChange,
        clearDate,
        onLunarTextChange,
        onBuddhistYearChange,
        highlightDatePicker
    }
}
