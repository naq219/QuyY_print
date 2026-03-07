import type { ProcessedRecord } from '~/composables/useDataProcessor'

/**
 * Composable quản lý Excel upload, danh sách bản ghi, nhập nhanh
 */
export function useExcelManager(clearDateFn: () => void) {
    const toast = useToast()
    const { readExcelFile, validateExcel, processAll, getDemoData } = useDataProcessor()

    // State
    const excelData = ref<Record<string, unknown>[]>([])
    const recordCount = ref(0)
    const excelFileName = ref('')
    const processedRecords = ref<ProcessedRecord[]>([])
    const currentRecordIndex = ref(0)
    const isUsingDemoData = ref(true)
    const showQuickEntry = ref(false)
    const quickForm = ref({
        ho_ten: '',
        phap_danh: '',
        sinh_nam: '',
        dia_chi: ''
    })

    // Computed
    const currentRecord = computed(() => {
        if (processedRecords.value.length === 0) return null
        return processedRecords.value[currentRecordIndex.value] || null
    })
    const totalRecords = computed(() => processedRecords.value.length)

    // Init demo data
    function initDemoData() {
        processedRecords.value = getDemoData()
        isUsingDemoData.value = true
    }

    // Excel Upload
    async function onExcelUpload(event: Event) {
        const input = event.target as HTMLInputElement
        const file = input?.files?.[0]
        if (!file) return

        try {
            const { count, data } = await readExcelFile(file)
            excelData.value = data
            recordCount.value = count
            excelFileName.value = file.name
            isUsingDemoData.value = false

            const warnings = validateExcel(data)
            if (warnings.has_warnings) {
                toast.add({ severity: 'warn', summary: 'Cảnh báo dữ liệu', detail: warnings.summary, life: 5000 })
            }

            const { dataList, errorCount } = processAll(data)
            processedRecords.value = dataList
            currentRecordIndex.value = 0

            // Xóa ngày quy y khi chọn Excel mới
            clearDateFn()

            toast.add({ severity: 'success', summary: 'Đã tải Excel', detail: `${count} bản ghi${errorCount > 0 ? ` (${errorCount} lỗi)` : ''}`, life: 3000 })
        } catch (err: unknown) {
            toast.add({ severity: 'error', summary: 'Lỗi đọc Excel', detail: String(err), life: 5000 })
        }
        input.value = ''
    }

    // Record navigation
    function prevRecord() {
        if (currentRecordIndex.value > 0) currentRecordIndex.value--
    }
    function nextRecord() {
        if (currentRecordIndex.value < totalRecords.value - 1) currentRecordIndex.value++
    }

    // Nhập nhanh
    function applyQuickEntry() {
        if (!quickForm.value.ho_ten.trim()) {
            toast.add({ severity: 'warn', summary: 'Thiếu thông tin', detail: 'Vui lòng nhập Họ và Tên', life: 3000 })
            return
        }
        const record: ProcessedRecord = {
            ho_ten: quickForm.value.ho_ten.trim(),
            phap_danh: quickForm.value.phap_danh.trim(),
            sinh_nam: quickForm.value.sinh_nam.trim(),
            dia_chi: quickForm.value.dia_chi.trim(),
            _has_error: false,
            _error_details: [],
            _row_index: 1
        }
        processedRecords.value = [record]
        currentRecordIndex.value = 0
        isUsingDemoData.value = false
        excelFileName.value = ''
        recordCount.value = 1
        toast.add({ severity: 'success', summary: 'Đã nhập', detail: `Dữ liệu: ${record.ho_ten}`, life: 2000 })
        showQuickEntry.value = false
    }

    function clearQuickForm() {
        quickForm.value = { ho_ten: '', phap_danh: '', sinh_nam: '', dia_chi: '' }
    }

    return {
        excelData,
        recordCount,
        excelFileName,
        processedRecords,
        currentRecordIndex,
        isUsingDemoData,
        showQuickEntry,
        quickForm,
        currentRecord,
        totalRecords,
        initDemoData,
        onExcelUpload,
        prevRecord,
        nextRecord,
        applyQuickEntry,
        clearQuickForm
    }
}
