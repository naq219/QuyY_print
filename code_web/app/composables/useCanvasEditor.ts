import { convertUnicodeToVni } from '~/composables/useVniConverter'
import type { ProcessedRecord } from '~/composables/useDataProcessor'

// Canvas constants
const A4_WIDTH_MM = 297
const A4_HEIGHT_MM = 210

// Field labels dùng chung
export const fieldLabels: Record<string, string> = {
    phap_danh: 'Pháp danh', ho_ten: 'Họ tên', sinh_nam: 'Năm sinh', dia_chi: 'Địa chỉ',
    phat_lich: 'Phật lịch', ngay_duong: 'Ngày dương', thang_duong: 'Tháng dương',
    nam_duong: 'Năm dương', ngay_am: 'Ngày âm', thang_am: 'Tháng âm', nam_am: 'Năm âm'
}

export interface FieldInfo {
    label: string; value: string; x: number; y: number
    size: number; align: 'L' | 'C' | 'R'; isCustom: boolean
}

interface CanvasEditorDeps {
    config: Ref<any>
    currentRecord: ComputedRef<ProcessedRecord | null>
    currentRecordIndex: Ref<number>
}

/**
 * Composable quản lý canvas preview: vẽ, kéo thả, chọn, sửa inline
 */
export function useCanvasEditor(deps: CanvasEditorDeps) {
    const toast = useToast()
    const { config, currentRecord, currentRecordIndex } = deps

    // Canvas state
    const canvasRef = ref<HTMLCanvasElement | null>(null)
    const templateImage = ref<HTMLImageElement | null>(null)
    const templateLoaded = ref(false)
    const canvasScale = ref(2.5)
    const canvasWidth = computed(() => Math.round(A4_WIDTH_MM * canvasScale.value))
    const canvasHeight = computed(() => Math.round(A4_HEIGHT_MM * canvasScale.value))

    // Selection & Drag
    const selectedFields = ref<Set<string>>(new Set())
    const isDragging = ref(false)
    const dragStartPos = ref({ x: 0, y: 0 })
    const dragFieldStartPositions = ref<Record<string, { x: number; y: number }>>({})

    // Inline edit
    const inlineEditField = ref<string | null>(null)
    const inlineEditValue = ref('')
    const inlineEditPos = ref({ left: '0px', top: '0px', width: '200px', fontSize: '14px' })

    // Field value overrides (tạm, không vào config)
    const fieldOverrides = ref<Record<string, string>>({})

    // Xóa overrides khi chuyển record
    watch(currentRecordIndex, () => { fieldOverrides.value = {} })

    // Computed: tất cả fields (standard + custom)
    const allFields = computed(() => {
        const result: Record<string, FieldInfo> = {}
        for (const [key, pos] of Object.entries(config.value.field_positions)) {
            const rec = currentRecord.value
            let value = ''
            if (fieldOverrides.value[key] !== undefined) {
                value = fieldOverrides.value[key]
            } else if (rec) {
                if (key === 'phap_danh') value = rec.phap_danh
                else if (key === 'ho_ten') value = rec.ho_ten
                else if (key === 'sinh_nam') value = rec.sinh_nam
                else if (key === 'dia_chi') value = rec.dia_chi
            }
            result[key] = { label: fieldLabels[key] || key, value, x: (pos as any).x, y: (pos as any).y, size: (pos as any).size, align: (pos as any).align, isCustom: false }
        }
        for (const [key, cf] of Object.entries(config.value.custom_fields)) {
            result[key] = { label: fieldLabels[key] || key, value: (cf as any).value, x: (cf as any).x, y: (cf as any).y, size: (cf as any).size, align: (cf as any).align, isCustom: true }
        }
        return result
    })

    // ====== CANVAS DRAWING ======
    function drawCanvas() {
        const canvas = canvasRef.value
        if (!canvas) return
        const ctx = canvas.getContext('2d')
        if (!ctx) return
        ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

        if (templateImage.value && templateLoaded.value) {
            ctx.drawImage(templateImage.value, 0, 0, canvasWidth.value, canvasHeight.value)
        } else {
            ctx.fillStyle = '#f5f5f0'
            ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
        }

        const scale = canvasScale.value
        for (const [key, field] of Object.entries(allFields.value)) {
            if (!field.value) continue
            const x = field.x * scale
            const y = field.y * scale
            const displaySize = Math.round(field.size * scale * 0.35)
            let displayText = field.value
            if (config.value.use_vni_font) displayText = convertUnicodeToVni(displayText)

            const fontFamily = config.value.use_vni_font ? "'QuyY Font', serif" : "'Arial', sans-serif"
            ctx.font = `${displaySize}px ${fontFamily}`
            ctx.fillStyle = field.isCustom ? '#cc0000' : '#0000cc'

            const metrics = ctx.measureText(displayText)
            let drawX = x
            if (field.align === 'C') drawX = x - metrics.width / 2
            else if (field.align === 'R') drawX = x - metrics.width
            ctx.fillText(displayText, drawX, y)

            // Selection highlight
            if (selectedFields.value.has(key)) {
                const pad = 4
                const rectX = field.align === 'C' ? x - metrics.width / 2 - pad
                    : field.align === 'R' ? x - metrics.width - pad : drawX - pad
                ctx.strokeStyle = '#22c55e'
                ctx.lineWidth = 2
                ctx.setLineDash([4, 3])
                ctx.strokeRect(rectX, y - displaySize - pad, metrics.width + pad * 2, displaySize + pad * 2)
                ctx.setLineDash([])
            }
        }
    }

    // Watch để auto-redraw
    watch([() => config.value.field_positions, () => config.value.custom_fields, currentRecordIndex, () => config.value.use_vni_font, selectedFields, fieldOverrides], () => {
        nextTick(() => drawCanvas())
    }, { deep: true })

    // ====== HIT DETECTION ======
    function getFieldAtPos(px: number, py: number): string | null {
        const scale = canvasScale.value
        const canvas = canvasRef.value
        if (!canvas) return null
        const ctx = canvas.getContext('2d')
        if (!ctx) return null
        const pad = 6
        for (const [key, field] of Object.entries(allFields.value)) {
            if (!field.value) continue
            const fx = field.x * scale, fy = field.y * scale
            const displaySize = Math.round(field.size * scale * 0.35)
            let displayText = field.value
            if (config.value.use_vni_font) displayText = convertUnicodeToVni(displayText)
            const fontFamily = config.value.use_vni_font ? "'QuyY Font', serif" : "'Arial', sans-serif"
            ctx.font = `${displaySize}px ${fontFamily}`
            const textWidth = ctx.measureText(displayText).width
            let rectX = fx
            if (field.align === 'C') rectX = fx - textWidth / 2
            else if (field.align === 'R') rectX = fx - textWidth
            if (px >= rectX - pad && px <= rectX + textWidth + pad && py >= fy - displaySize - pad && py <= fy + pad) return key
        }
        return null
    }

    // ====== MOUSE EVENTS ======
    function onCanvasMouseDown(e: MouseEvent) {
        if (inlineEditField.value) return
        const canvas = canvasRef.value
        if (!canvas) return
        const rect = canvas.getBoundingClientRect()
        const x = (e.clientX - rect.left) * (canvas.width / rect.width)
        const y = (e.clientY - rect.top) * (canvas.height / rect.height)
        const clickedField = getFieldAtPos(x, y)
        if (clickedField) {
            if (e.ctrlKey || e.metaKey) {
                const newSet = new Set(selectedFields.value)
                if (newSet.has(clickedField)) newSet.delete(clickedField)
                else newSet.add(clickedField)
                selectedFields.value = newSet
            } else if (!selectedFields.value.has(clickedField)) {
                selectedFields.value = new Set([clickedField])
            }
            isDragging.value = true
            dragStartPos.value = { x, y }
            const starts: Record<string, { x: number; y: number }> = {}
            for (const key of selectedFields.value) {
                const f = allFields.value[key]
                if (f) starts[key] = { x: f.x, y: f.y }
            }
            dragFieldStartPositions.value = starts
        } else {
            selectedFields.value = new Set()
        }
    }

    function onCanvasMouseMove(e: MouseEvent) {
        if (!isDragging.value) return
        const canvas = canvasRef.value
        if (!canvas) return
        const rect = canvas.getBoundingClientRect()
        const x = (e.clientX - rect.left) * (canvas.width / rect.width)
        const y = (e.clientY - rect.top) * (canvas.height / rect.height)
        const scale = canvasScale.value
        const dx = (x - dragStartPos.value.x) / scale
        const dy = (y - dragStartPos.value.y) / scale
        for (const [key, start] of Object.entries(dragFieldStartPositions.value)) {
            const newX = Math.round((start.x + dx) * 10) / 10
            const newY = Math.round((start.y + dy) * 10) / 10
            if (config.value.field_positions[key]) {
                config.value.field_positions[key].x = newX
                config.value.field_positions[key].y = newY
            } else if (config.value.custom_fields[key]) {
                config.value.custom_fields[key].x = newX
                config.value.custom_fields[key].y = newY
            }
        }
    }

    function onCanvasMouseUp() { isDragging.value = false }

    // ====== KEYBOARD ======
    function onCanvasKeyDown(e: KeyboardEvent) {
        if (selectedFields.value.size === 0) return
        const step = 0.4
        let dx = 0, dy = 0
        if (e.key === 'ArrowLeft') dx = -step
        else if (e.key === 'ArrowRight') dx = step
        else if (e.key === 'ArrowUp') dy = -step
        else if (e.key === 'ArrowDown') dy = step
        else if (e.key === 'a' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault()
            selectedFields.value = new Set(Object.keys(allFields.value))
            return
        } else return
        e.preventDefault()
        for (const key of selectedFields.value) {
            if (config.value.field_positions[key]) {
                config.value.field_positions[key].x = Math.round((config.value.field_positions[key].x + dx) * 10) / 10
                config.value.field_positions[key].y = Math.round((config.value.field_positions[key].y + dy) * 10) / 10
            } else if (config.value.custom_fields[key]) {
                config.value.custom_fields[key].x = Math.round((config.value.custom_fields[key].x + dx) * 10) / 10
                config.value.custom_fields[key].y = Math.round((config.value.custom_fields[key].y + dy) * 10) / 10
            }
        }
    }

    // ====== DOUBLE-CLICK INLINE EDIT ======
    function onCanvasDblClick(e: MouseEvent) {
        const canvas = canvasRef.value
        if (!canvas) return
        const canvasRect = canvas.getBoundingClientRect()
        const px = (e.clientX - canvasRect.left) * (canvas.width / canvasRect.width)
        const py = (e.clientY - canvasRect.top) * (canvas.height / canvasRect.height)
        const key = getFieldAtPos(px, py)
        if (!key) return
        const field = allFields.value[key]
        if (!field) return
        const scale = canvasScale.value
        const scaleRatio = canvasRect.width / canvas.width
        const fieldX = field.x * scale * scaleRatio
        const fieldY = field.y * scale * scaleRatio
        const fieldFontSize = Math.round(field.size * scale * 0.35 * scaleRatio)
        let leftOffset = fieldX
        if (field.align === 'C') leftOffset = fieldX - 80
        else if (field.align === 'R') leftOffset = fieldX - 160
        inlineEditPos.value = {
            left: `${Math.max(0, leftOffset)}px`,
            top: `${fieldY - fieldFontSize - 4}px`,
            width: `${Math.max(120, 200)}px`,
            fontSize: `${Math.max(12, fieldFontSize)}px`
        }
        inlineEditField.value = key
        inlineEditValue.value = field.value
        selectedFields.value = new Set([key])
        nextTick(() => {
            const input = document.querySelector('.canvas-inline-input') as HTMLInputElement
            if (input) { input.focus(); input.select() }
        })
    }

    let _isSavingInline = false
    function saveInlineEdit() {
        if (_isSavingInline) return
        const key = inlineEditField.value
        if (!key) return
        _isSavingInline = true
        const newValue = inlineEditValue.value
        const field = allFields.value[key]
        if (!field) { cancelInlineEdit(); _isSavingInline = false; return }
        if (field.isCustom) {
            if (config.value.custom_fields[key]) config.value.custom_fields[key].value = newValue
        } else {
            fieldOverrides.value = { ...fieldOverrides.value, [key]: newValue }
        }
        inlineEditField.value = null
        nextTick(() => { drawCanvas(); _isSavingInline = false })
        toast.add({ severity: 'success', summary: 'Đã sửa', detail: `${fieldLabels[key] || key}: ${newValue}`, life: 1500 })
    }

    function cancelInlineEdit() {
        inlineEditField.value = null
        nextTick(() => drawCanvas())
    }

    function onInlineEditKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') { e.preventDefault(); saveInlineEdit() }
        else if (e.key === 'Escape') { e.preventDefault(); cancelInlineEdit() }
    }

    // ====== INIT ======
    function initCanvas() {
        const img = new Image()
        img.onload = () => {
            templateImage.value = img
            templateLoaded.value = true
            nextTick(() => drawCanvas())
        }
        img.src = '/phoimau.jpg'
    }

    async function loadVniFont() {
        try {
            const font = new FontFace('QuyY Font', 'url(/quyyfont.ttf)')
            const loaded = await font.load()
            document.fonts.add(loaded)
        } catch (e) {
            console.warn('Không thể load font VNI:', e)
        }
    }

    return {
        canvasRef, canvasWidth, canvasHeight,
        selectedFields, fieldOverrides,
        inlineEditField, inlineEditValue, inlineEditPos,
        allFields,
        drawCanvas, initCanvas, loadVniFont,
        onCanvasMouseDown, onCanvasMouseMove, onCanvasMouseUp,
        onCanvasKeyDown, onCanvasDblClick,
        saveInlineEdit, cancelInlineEdit, onInlineEditKeydown
    }
}
