<script setup lang="ts">
import { PDFDocument, rgb } from 'pdf-lib'
import fontkit from '@pdf-lib/fontkit'
import { convertUnicodeToVni } from '~/composables/useVniConverter'
import type { ProcessedRecord } from '~/composables/useDataProcessor'
import type { LunarResult } from '~/composables/useLunarConverter'

useHead({ title: 'QuyY Print - In Lá Phái Quy Y' })

// ===================== COMPOSABLES =====================
const toast = useToast()
const { config, saveConfig, resetConfig, updateDateFields, clearDateFields, exportConfig } = useConfigManager()
const { convertDate } = useLunarConverter()
const { readExcelFile, validateExcel, processAll, getDemoData } = useDataProcessor()

// ===================== STATE =====================
// Canvas
const canvasRef = ref<HTMLCanvasElement | null>(null)
const templateImage = ref<HTMLImageElement | null>(null)
const templateLoaded = ref(false)
const A4_WIDTH_MM = 297
const A4_HEIGHT_MM = 210
const MM_TO_PT = 2.8346
const canvasScale = ref(2.5)
const canvasWidth = computed(() => Math.round(A4_WIDTH_MM * canvasScale.value))
const canvasHeight = computed(() => Math.round(A4_HEIGHT_MM * canvasScale.value))

// Selected fields (cho chỉnh tọa độ)
const selectedFields = ref<Set<string>>(new Set())
const isDragging = ref(false)
const dragStartPos = ref({ x: 0, y: 0 })
const dragFieldStartPositions = ref<Record<string, { x: number; y: number }>>({})

// Inline canvas editing
const inlineEditField = ref<string | null>(null)
const inlineEditValue = ref('')
const inlineEditPos = ref({ left: '0px', top: '0px', width: '200px', fontSize: '14px' })

// Field value overrides (cho standard fields - lưu tạm, không vào config)
const fieldOverrides = ref<Record<string, string>>({})

// Excel data
const excelData = ref<Record<string, unknown>[]>([])
const recordCount = ref(0)
const excelFileName = ref('')

// Processed records (từ Excel hoặc nhập nhanh)
const processedRecords = ref<ProcessedRecord[]>([])
const currentRecordIndex = ref(0)
const isUsingDemoData = ref(true)

// Ngày quy y
const selectedDate = ref<Date | null>(null)
const lunarInfo = ref<LunarResult | null>(null)

// UI
const showAdvanced = ref(false)
const showQuickEntry = ref(false)
const showFieldsPanel = ref(false)
const isGeneratingPdf = ref(false)
const pdfPreviewUrl = ref('')
const highlightDate = ref(false)

// Nhập nhanh
const quickForm = ref({
  ho_ten: '',
  phap_danh: '',
  sinh_nam: '',
  dia_chi: ''
})

// ===================== COMPUTED =====================
const currentRecord = computed(() => {
  if (processedRecords.value.length === 0) return null
  return processedRecords.value[currentRecordIndex.value] || null
})

const totalRecords = computed(() => processedRecords.value.length)

const fieldLabels: Record<string, string> = {
  phap_danh: 'Pháp danh', ho_ten: 'Họ tên', sinh_nam: 'Năm sinh', dia_chi: 'Địa chỉ',
  phat_lich: 'Phật lịch', ngay_duong: 'Ngày dương', thang_duong: 'Tháng dương',
  nam_duong: 'Năm dương', ngay_am: 'Ngày âm', thang_am: 'Tháng âm', nam_am: 'Năm âm'
}

const allFields = computed(() => {
  const result: Record<string, { label: string; value: string; x: number; y: number; size: number; align: 'L' | 'C' | 'R'; isCustom: boolean }> = {}

  // 4 field chính (data từ record hiện tại, có thể bị override)
  for (const [key, pos] of Object.entries(config.value.field_positions)) {
    const rec = currentRecord.value
    let value = ''
    // Ưu tiên override > data gốc
    if (fieldOverrides.value[key] !== undefined) {
      value = fieldOverrides.value[key]
    } else if (rec) {
      if (key === 'phap_danh') value = rec.phap_danh
      else if (key === 'ho_ten') value = rec.ho_ten
      else if (key === 'sinh_nam') value = rec.sinh_nam
      else if (key === 'dia_chi') value = rec.dia_chi
    }
    result[key] = { label: fieldLabels[key] || key, value, x: pos.x, y: pos.y, size: pos.size, align: pos.align, isCustom: false }
  }

  // Custom fields (giá trị cố định)
  for (const [key, cf] of Object.entries(config.value.custom_fields)) {
    result[key] = { label: fieldLabels[key] || key, value: cf.value, x: cf.x, y: cf.y, size: cf.size, align: cf.align, isCustom: true }
  }

  return result
})

// Xóa overrides khi chuyển record
watch(currentRecordIndex, () => {
  fieldOverrides.value = {}
})

// ===================== TEMPLATE IMAGE =====================
onMounted(() => {
  const img = new Image()
  img.onload = () => {
    templateImage.value = img
    templateLoaded.value = true
    // Load demo data ban đầu
    processedRecords.value = getDemoData()
    isUsingDemoData.value = true
    nextTick(() => drawCanvas())
  }
  img.src = '/phoimau.jpg'
})

// ===================== CANVAS DRAWING =====================
function drawCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

  // Vẽ ảnh nền
  if (templateImage.value && templateLoaded.value) {
    ctx.drawImage(templateImage.value, 0, 0, canvasWidth.value, canvasHeight.value)
  } else {
    ctx.fillStyle = '#f5f5f0'
    ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  }

  // Vẽ các fields
  const scale = canvasScale.value
  for (const [key, field] of Object.entries(allFields.value)) {
    if (!field.value) continue

    const x = field.x * scale
    const y = field.y * scale
    const displaySize = Math.round(field.size * scale * 0.35)

    let displayText = field.value
    if (config.value.use_vni_font) {
      displayText = convertUnicodeToVni(displayText)
    }

    // Font
    const fontFamily = config.value.use_vni_font ? "'QuyY Font', serif" : "'Arial', sans-serif"
    ctx.font = `${displaySize}px ${fontFamily}`
    ctx.fillStyle = field.isCustom ? '#cc0000' : '#0000cc'

    // Align
    const metrics = ctx.measureText(displayText)
    let drawX = x
    if (field.align === 'C') drawX = x - metrics.width / 2
    else if (field.align === 'R') drawX = x - metrics.width

    ctx.fillText(displayText, drawX, y)

    // Selection highlight
    const isSelected = selectedFields.value.has(key)
    if (isSelected) {
      const pad = 4
      const rectX = field.align === 'C' ? x - metrics.width / 2 - pad
        : field.align === 'R' ? x - metrics.width - pad
        : drawX - pad
      const rectY = y - displaySize - pad
      const rectW = metrics.width + pad * 2
      const rectH = displaySize + pad * 2

      ctx.strokeStyle = '#22c55e'
      ctx.lineWidth = 2
      ctx.setLineDash([4, 3])
      ctx.strokeRect(rectX, rectY, rectW, rectH)
      ctx.setLineDash([])
    }
  }
}

// Watch để redraw
watch([() => config.value.field_positions, () => config.value.custom_fields, currentRecordIndex, () => config.value.use_vni_font, selectedFields, fieldOverrides], () => {
  nextTick(() => drawCanvas())
}, { deep: true })

// ===================== MOUSE / KEYBOARD =====================
function getFieldAtPos(px: number, py: number): string | null {
  const scale = canvasScale.value
  const canvas = canvasRef.value
  if (!canvas) return null
  const ctx = canvas.getContext('2d')
  if (!ctx) return null

  const pad = 6 // padding quanh text cho dễ click

  for (const [key, field] of Object.entries(allFields.value)) {
    if (!field.value) continue

    const fx = field.x * scale
    const fy = field.y * scale
    const displaySize = Math.round(field.size * scale * 0.35)

    let displayText = field.value
    if (config.value.use_vni_font) {
      displayText = convertUnicodeToVni(displayText)
    }

    const fontFamily = config.value.use_vni_font ? "'QuyY Font', serif" : "'Arial', sans-serif"
    ctx.font = `${displaySize}px ${fontFamily}`
    const metrics = ctx.measureText(displayText)
    const textWidth = metrics.width

    // Tính vị trí x thực tế sau align
    let rectX = fx
    if (field.align === 'C') rectX = fx - textWidth / 2
    else if (field.align === 'R') rectX = fx - textWidth

    // Bounding box: [rectX - pad, fy - displaySize - pad] → [rectX + textWidth + pad, fy + pad]
    const x1 = rectX - pad
    const y1 = fy - displaySize - pad
    const x2 = rectX + textWidth + pad
    const y2 = fy + pad

    if (px >= x1 && px <= x2 && py >= y1 && py <= y2) {
      return key
    }
  }
  return null
}

function onCanvasMouseDown(e: MouseEvent) {
  // Nếu đang inline edit, bỏ qua mousedown
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

    // Start drag
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

// ===================== DOUBLE-CLICK = INLINE EDIT =====================
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

  // Tính vị trí input overlay (lấy theo tọa độ CSS thực tế trên canvas element)
  const scale = canvasScale.value
  const scaleRatio = canvasRect.width / canvas.width
  const fieldX = field.x * scale * scaleRatio
  const fieldY = field.y * scale * scaleRatio
  const fieldFontSize = Math.round(field.size * scale * 0.35 * scaleRatio)

  // Offset cho align
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
    // Custom field → lưu cố định vào config
    if (config.value.custom_fields[key]) {
      config.value.custom_fields[key].value = newValue
    }
  } else {
    // Standard field → lưu vào biến tạm (spread = new object → guaranteed reactive)
    fieldOverrides.value = { ...fieldOverrides.value, [key]: newValue }
  }

  inlineEditField.value = null
  nextTick(() => {
    drawCanvas()
    _isSavingInline = false
  })
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

function onCanvasMouseUp() {
  isDragging.value = false
}

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

// ===================== NGÀY QUY Y =====================
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
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: 'Không thể chuyển đổi ngày', life: 3000 })
  }
}

function formatDateISO(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

function clearDate() {
  selectedDate.value = null
  lunarInfo.value = null
  clearDateFields()
}

// ===================== EDITABLE LUNAR INFO =====================
const lunarDisplayText = computed(() => {
  if (!lunarInfo.value) return ''
  const li = lunarInfo.value
  return `${li.lunar_day}/${li.lunar_month} ${li.lunar_year_name}`
})

function onLunarTextChange(text: string) {
  // Parse "27/10 Ất Tỵ" hoặc "27/10"
  const parts = text.trim().split(/[\s/]+/)
  if (parts.length >= 2) {
    const day = parts[0]!
    const month = parts[1]!
    const yearName = parts.slice(2).join(' ')

    if (config.value.custom_fields.ngay_am) config.value.custom_fields.ngay_am.value = day
    if (config.value.custom_fields.thang_am) config.value.custom_fields.thang_am.value = month
    if (yearName && config.value.custom_fields.nam_am) config.value.custom_fields.nam_am.value = yearName

    // Cập nhật lunarInfo để hiển thị đúng
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

// ===================== EXCEL =====================
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

    // Validate
    const warnings = validateExcel(data)
    if (warnings.has_warnings) {
      toast.add({ severity: 'warn', summary: 'Cảnh báo dữ liệu', detail: warnings.summary, life: 5000 })
    }

    // Process
    const { dataList, errorCount, errorSummary } = processAll(data)
    processedRecords.value = dataList
    currentRecordIndex.value = 0

    // Xóa ngày quy y khi chọn Excel mới
    clearDate()

    toast.add({ severity: 'success', summary: 'Đã tải Excel', detail: `${count} bản ghi${errorCount > 0 ? ` (${errorCount} lỗi)` : ''}`, life: 3000 })
  } catch (err: unknown) {
    toast.add({ severity: 'error', summary: 'Lỗi đọc Excel', detail: String(err), life: 5000 })
  }
  // Reset input
  input.value = ''
}

// Record navigation
function prevRecord() {
  if (currentRecordIndex.value > 0) currentRecordIndex.value--
}
function nextRecord() {
  if (currentRecordIndex.value < totalRecords.value - 1) currentRecordIndex.value++
}

// ===================== NHẬP NHANH =====================
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

// ===================== PDF GENERATION =====================
function highlightDatePicker() {
  toast.add({ severity: 'warn', summary: 'Chưa chọn ngày', detail: 'Vui lòng chọn Ngày Quy Y trước', life: 3000 })
  highlightDate.value = true
  setTimeout(() => { highlightDate.value = false }, 3000)
}

async function generatePdf() {
  if (processedRecords.value.length === 0) {
    toast.add({ severity: 'warn', summary: 'Không có dữ liệu', detail: 'Vui lòng tải Excel hoặc nhập nhanh', life: 3000 })
    return
  }
  if (!selectedDate.value && !isUsingDemoData.value) {
    highlightDatePicker()
    return
  }

  isGeneratingPdf.value = true
  try {
    const pdfDoc = await PDFDocument.create()
    pdfDoc.registerFontkit(fontkit)

    // Load font
    const fontResp = await fetch('/quyyfont.ttf')
    const fontBytes = await fontResp.arrayBuffer()
    const customFont = await pdfDoc.embedFont(fontBytes)

    // Load background image (chỉ khi user BẬT tùy chọn)
    let bgImage: Awaited<ReturnType<typeof pdfDoc.embedJpg>> | null = null
    if (config.value.use_background_image) {
      try {
        const bgResp = await fetch('/phoimau.jpg')
        const bgBytes = await bgResp.arrayBuffer()
        bgImage = await pdfDoc.embedJpg(bgBytes)
      } catch { /* skip */ }
    }

    const pageWidth = A4_WIDTH_MM * MM_TO_PT
    const pageHeight = A4_HEIGHT_MM * MM_TO_PT

    for (const record of processedRecords.value) {
      const page = pdfDoc.addPage([pageWidth, pageHeight])

      // Background
      if (bgImage) {
        page.drawImage(bgImage, { x: 0, y: 0, width: pageWidth, height: pageHeight })
      }

      // Draw standard fields
      for (const [key, pos] of Object.entries(config.value.field_positions)) {
        let text = ''
        // Áp dụng override nếu có (chỉ cho record đang hiển thị)
        if (record === processedRecords.value[currentRecordIndex.value] && fieldOverrides.value[key] !== undefined) {
          text = fieldOverrides.value[key]
        } else {
          if (key === 'phap_danh') text = record.phap_danh
          else if (key === 'ho_ten') text = record.ho_ten
          else if (key === 'sinh_nam') text = record.sinh_nam
          else if (key === 'dia_chi') text = record.dia_chi
        }
        if (!text) continue

        if (config.value.use_vni_font) text = convertUnicodeToVni(text)
        drawTextField(page, text, pos.x, pos.y, pos.size, pos.align, customFont, pageHeight)
      }

      // Draw custom fields
      for (const [, cf] of Object.entries(config.value.custom_fields)) {
        if (!cf.value) continue
        let text = cf.value
        if (config.value.use_vni_font) text = convertUnicodeToVni(text)
        drawTextField(page, text, cf.x, cf.y, cf.size, cf.align, customFont, pageHeight)
      }
    }

    const pdfBytes = await pdfDoc.save()
    const blob = new Blob([pdfBytes], { type: 'application/pdf' })

    if (pdfPreviewUrl.value) URL.revokeObjectURL(pdfPreviewUrl.value)
    pdfPreviewUrl.value = URL.createObjectURL(blob)

    toast.add({ severity: 'success', summary: 'PDF đã tạo', detail: `${processedRecords.value.length} trang - đang tải xuống...`, life: 3000 })

    // Auto download
    const a = document.createElement('a')
    a.href = pdfPreviewUrl.value
    a.download = `QuyY_${processedRecords.value.length}pages.pdf`
    a.click()
  } catch (err) {
    console.error(err)
    toast.add({ severity: 'error', summary: 'Lỗi tạo PDF', detail: String(err), life: 5000 })
  } finally {
    isGeneratingPdf.value = false
  }
}

function drawTextField(page: any, text: string, xMm: number, yMm: number, size: number, align: string, font: any, pageHeight: number) {
  const x = xMm * MM_TO_PT
  const y = pageHeight - (yMm * MM_TO_PT)

  let drawX = x
  if (align === 'C') {
    const textWidth = font.widthOfTextAtSize(text, size)
    drawX = x - textWidth / 2
  } else if (align === 'R') {
    const textWidth = font.widthOfTextAtSize(text, size)
    drawX = x - textWidth
  }

  page.drawText(text, { x: drawX, y, size, font, color: rgb(0, 0, 0) })
}

async function downloadPdf() {
  if (!pdfPreviewUrl.value) {
    await generatePdf()
  }
  if (pdfPreviewUrl.value) {
    const a = document.createElement('a')
    a.href = pdfPreviewUrl.value
    a.download = `QuyY_${processedRecords.value.length}pages.pdf`
    a.click()
  }
}

function printViaIframe(blobUrl: string) {
  // Xóa iframe cũ nếu có
  const old = document.getElementById('print-iframe')
  if (old) old.remove()

  const iframe = document.createElement('iframe')
  iframe.id = 'print-iframe'
  iframe.style.position = 'fixed'
  iframe.style.top = '-9999px'
  iframe.style.left = '-9999px'
  iframe.style.width = '0'
  iframe.style.height = '0'
  iframe.style.border = 'none'
  iframe.src = blobUrl
  document.body.appendChild(iframe)

  iframe.onload = () => {
    try {
      iframe.contentWindow?.focus()
      iframe.contentWindow?.print()
    } catch {
      // Fallback nếu iframe bị chặn cross-origin
      window.open(blobUrl, '_blank')
    }
  }
}

function printPdf() {
  if (!pdfPreviewUrl.value) return
  printViaIframe(pdfPreviewUrl.value)
}

async function quickPrint() {
  if (!selectedDate.value && !isUsingDemoData.value) {
    highlightDatePicker()
    return
  }
  if (!pdfPreviewUrl.value) {
    await generatePdf()
  }
  printPdf()
}

async function printSingleRecord(idx: number) {
  const record = processedRecords.value[idx]
  if (!record) return

  try {
    const pdfDoc = await PDFDocument.create()
    pdfDoc.registerFontkit(fontkit)

    const fontResp = await fetch('/quyyfont.ttf')
    const fontBytes = await fontResp.arrayBuffer()
    const customFont = await pdfDoc.embedFont(fontBytes)

    let bgImage: Awaited<ReturnType<typeof pdfDoc.embedJpg>> | null = null
    if (config.value.use_background_image) {
      try {
        const bgResp = await fetch('/phoimau.jpg')
        const bgBytes = await bgResp.arrayBuffer()
        bgImage = await pdfDoc.embedJpg(bgBytes)
      } catch { /* skip */ }
    }

    const pageWidth = A4_WIDTH_MM * MM_TO_PT
    const pageHeight = A4_HEIGHT_MM * MM_TO_PT
    const page = pdfDoc.addPage([pageWidth, pageHeight])

    if (bgImage) {
      page.drawImage(bgImage, { x: 0, y: 0, width: pageWidth, height: pageHeight })
    }

    for (const [key, pos] of Object.entries(config.value.field_positions)) {
      let text = ''
      if (key === 'phap_danh') text = record.phap_danh
      else if (key === 'ho_ten') text = record.ho_ten
      else if (key === 'sinh_nam') text = record.sinh_nam
      else if (key === 'dia_chi') text = record.dia_chi
      if (!text) continue
      if (config.value.use_vni_font) text = convertUnicodeToVni(text)
      drawTextField(page, text, pos.x, pos.y, pos.size, pos.align, customFont, pageHeight)
    }

    for (const [, cf] of Object.entries(config.value.custom_fields)) {
      if (!cf.value) continue
      let text = cf.value
      if (config.value.use_vni_font) text = convertUnicodeToVni(text)
      drawTextField(page, text, cf.x, cf.y, cf.size, cf.align, customFont, pageHeight)
    }

    const pdfBytes = await pdfDoc.save()
    const blob = new Blob([pdfBytes], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    printViaIframe(url)
    toast.add({ severity: 'info', summary: 'In', detail: `Đang in: ${record.ho_ten}`, life: 2000 })
  } catch (err) {
    console.error(err)
    toast.add({ severity: 'error', summary: 'Lỗi', detail: String(err), life: 5000 })
  }
}

// ===================== VNI FONT LOADING =====================
onMounted(async () => {
  try {
    const font = new FontFace('QuyY Font', 'url(/quyyfont.ttf)')
    const loaded = await font.load()
    document.fonts.add(loaded)
  } catch (e) {
    console.warn('Không thể load font VNI:', e)
  }
})

// ===================== SAVE CONFIG =====================
function onSaveConfig() {
  saveConfig()
  toast.add({ severity: 'success', summary: 'Đã lưu', detail: 'Cấu hình đã được lưu', life: 2000 })
}

function onResetConfig() {
  resetConfig()
  toast.add({ severity: 'info', summary: 'Đã reset', detail: 'Cấu hình đã khôi phục mặc định', life: 2000 })
}

function onExportConfig() {
  const jsonStr = exportConfig()
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'quyy_config.json'
  a.click()
}

// ===================== INLINE EDIT CUSTOM VALUE =====================
function onCustomValueChange(key: string, newValue: string) {
  if (config.value.custom_fields[key]) {
    config.value.custom_fields[key].value = newValue
  }
}

// Field editing dialog
const editingField = ref<{ key: string; label: string; x: number; y: number; size: number; align: string } | null>(null)
const showEditDialog = ref(false)

function openFieldEdit(key: string) {
  const f = allFields.value[key]
  if (!f) return
  editingField.value = { key, label: f.label, x: f.x, y: f.y, size: f.size, align: f.align }
  showEditDialog.value = true
}

function saveFieldEdit() {
  if (!editingField.value) return
  const { key, x, y, size, align } = editingField.value
  const alignTyped = align as 'L' | 'C' | 'R'
  if (config.value.field_positions[key]) {
    Object.assign(config.value.field_positions[key], { x, y, size, align: alignTyped })
  } else if (config.value.custom_fields[key]) {
    Object.assign(config.value.custom_fields[key], { x, y, size, align: alignTyped })
  }
  showEditDialog.value = false
  toast.add({ severity: 'success', summary: 'Đã cập nhật', detail: editingField.value.label, life: 2000 })
}
</script>

<template>
  <div class="page-container">
    <Toast />

    <!-- ============ TOOLBAR ============ -->
    <div class="toolbar">
      <div class="toolbar-left">
        <!-- Upload Excel -->
        <label class="btn-upload" tabindex="0">
          <i class="pi pi-file-excel" />
          <span>{{ excelFileName || 'Tải Excel' }}</span>
          <input type="file" accept=".xlsx,.xls" hidden @change="onExcelUpload" />
        </label>
        <span v-if="recordCount > 0 && !isUsingDemoData" class="record-badge">
          {{ recordCount }} bản ghi
        </span>
        <span v-else-if="isUsingDemoData" class="record-badge demo">Demo</span>

        <!-- Divider -->
        <div class="toolbar-divider" />

        <!-- Ngày Quy Y -->
        <div class="date-group" :class="{ 'highlight-pulse': highlightDate }">
          <label class="date-label">📅 Ngày Quy Y:</label>
          <DatePicker v-model="selectedDate" dateFormat="dd/mm/yy" placeholder="Chọn ngày..."
            showIcon class="date-input" @update:modelValue="onDateChange" />
          <Button v-if="selectedDate" icon="pi pi-times" severity="secondary" text rounded size="small"
            @click="clearDate" v-tooltip.bottom="'Xóa ngày'" />
        </div>

        <!-- Lunar Info (editable) -->
        <div v-if="lunarInfo" class="lunar-edit-group">
          <span class="lunar-label">🌙 ÂL:</span>
          <input type="text" class="lunar-inline" :value="lunarDisplayText"
            @change="(e: Event) => onLunarTextChange((e.target as HTMLInputElement).value)" 
            v-tooltip.bottom="'Sửa ngày âm lịch'" />
          <span class="lunar-label">☸️ PL:</span>
          <input type="text" class="lunar-inline pl-input" :value="config.custom_fields.phat_lich?.value || ''"
            @change="(e: Event) => onBuddhistYearChange((e.target as HTMLInputElement).value)"
            v-tooltip.bottom="'Sửa Phật lịch'" />
        </div>
      </div>

      <div class="toolbar-right">
        <!-- Actions: In luôn đặt trước -->
        <Button label="In hàng loạt" icon="pi pi-print" severity="warn" @click="quickPrint"
          v-tooltip.bottom="'Tạo PDF và In ngay'" />
        <Button label="Tạo PDF" icon="pi pi-file-pdf" severity="success" :loading="isGeneratingPdf"
          @click="generatePdf" v-tooltip.bottom="'Tạo và tải PDF xuống'" />

        <div class="toolbar-divider" />

        <!-- Toggle Fields Panel -->
        <Button :icon="showFieldsPanel ? 'pi pi-times' : 'pi pi-sliders-h'" 
          :severity="showFieldsPanel ? 'secondary' : 'contrast'" text rounded
          v-tooltip.bottom="showFieldsPanel ? 'Ẩn bảng fields' : 'Hiện bảng fields'"
          @click="showFieldsPanel = !showFieldsPanel" />
      </div>
    </div>

    <!-- ============ MAIN AREA ============ -->
    <div class="main-area">
      <!-- LEFT: Records List -->
      <div class="records-panel">
        <div class="records-header">
          <i class="pi pi-users" /> Danh sách ({{ totalRecords }})
        </div>
        <div class="records-list">
          <div v-for="(rec, idx) in processedRecords" :key="idx"
            class="record-item" :class="{ active: idx === currentRecordIndex }"
            @click="currentRecordIndex = idx">
            <span class="rec-idx">{{ idx + 1 }}</span>
            <div class="rec-info">
              <span class="rec-name">{{ rec.ho_ten || '(chưa có tên)' }}</span>
              <span v-if="rec.phap_danh" class="rec-phap">{{ rec.phap_danh }}</span>
            </div>
            <button class="rec-print-btn" :class="{ visible: idx === currentRecordIndex }"
              @click.stop="printSingleRecord(idx)" title="In người này">
              <i class="pi pi-print" />
            </button>
          </div>
          <div v-if="processedRecords.length === 0" class="records-empty">
            Chưa có dữ liệu
          </div>
        </div>
      </div>

      <!-- CENTER: Canvas -->
      <div class="canvas-panel">
        <div class="canvas-header">
          <span class="canvas-title">
            <i class="pi pi-image" /> Canvas Preview
          </span>

          <!-- Record Navigation -->
          <div v-if="totalRecords > 0" class="record-nav">
            <Button icon="pi pi-chevron-left" text rounded size="small" :disabled="currentRecordIndex === 0"
              @click="prevRecord" />
            <span class="record-pos">{{ currentRecordIndex + 1 }} / {{ totalRecords }}</span>
            <Button icon="pi pi-chevron-right" text rounded size="small"
              :disabled="currentRecordIndex >= totalRecords - 1" @click="nextRecord" />
          </div>
        </div>

        <div class="canvas-wrapper">
          <div class="canvas-container">
            <canvas ref="canvasRef" :width="canvasWidth" :height="canvasHeight" tabindex="0"
              @mousedown="onCanvasMouseDown" @mousemove="onCanvasMouseMove" @mouseup="onCanvasMouseUp"
              @mouseleave="onCanvasMouseUp" @keydown="onCanvasKeyDown" @dblclick="onCanvasDblClick" />

            <!-- Inline edit overlay -->
            <input v-if="inlineEditField" v-model="inlineEditValue"
              class="canvas-inline-input"
              :style="{ left: inlineEditPos.left, top: inlineEditPos.top, width: inlineEditPos.width, fontSize: inlineEditPos.fontSize }"
              @blur="saveInlineEdit" @keydown="onInlineEditKeydown" @click.stop />
          </div>
        </div>

        <!-- Selection info -->
        <div v-if="selectedFields.size > 0" class="selection-info">
          <i class="pi pi-arrows-alt" />
          {{ selectedFields.size }} field đang chọn – Phím ←↑→↓ di chuyển
        </div>
      </div>

      <!-- RIGHT: Fields Panel (toggle) -->
      <div v-if="showFieldsPanel" class="fields-panel">
        <!-- Fields list -->
        <div class="panel-section">
          <div class="panel-header">
            <i class="pi pi-list" /> Danh sách Fields
            <Button icon="pi pi-save" text rounded size="small" v-tooltip.left="'Lưu cấu hình'" @click="onSaveConfig" />
          </div>

          <div class="fields-table">
            <div class="field-row header">
              <span class="col-name">Field</span>
              <span class="col-val">Giá trị</span>
              <span class="col-x">X</span>
              <span class="col-y">Y</span>
              <span class="col-action"></span>
            </div>
            <div v-for="(field, key) in allFields" :key="key" class="field-row"
              :class="{ selected: selectedFields.has(key as string), custom: field.isCustom }"
              @click="selectedFields = new Set([key as string])">
              <span class="col-name" :title="field.label">{{ field.label }}</span>
              <span class="col-val">
                <input v-if="field.isCustom" type="text" class="inline-val-input"
                  :value="config.custom_fields[key as string]?.value || ''"
                  @input="(e: Event) => onCustomValueChange(key as string, (e.target as HTMLInputElement).value)"
                  @click.stop placeholder="..." />
                <span v-else class="val-readonly" :title="field.value">{{ field.value || '—' }}</span>
              </span>
              <span class="col-x">{{ field.x.toFixed(1) }}</span>
              <span class="col-y">{{ field.y.toFixed(1) }}</span>
              <span class="col-action">
                <Button icon="pi pi-pencil" text rounded size="small" @click.stop="openFieldEdit(key as string)" />
              </span>
            </div>
          </div>
        </div>

        <!-- Expandable: Nhập nhanh -->
        <div class="panel-section">
          <div class="panel-header clickable" @click="showQuickEntry = !showQuickEntry">
            <i :class="showQuickEntry ? 'pi pi-chevron-down' : 'pi pi-chevron-right'" />
            ✍️ Nhập nhanh (không cần Excel)
          </div>
          <div v-if="showQuickEntry" class="quick-entry-form">
            <div class="form-row">
              <label>Họ tên <span class="required">*</span></label>
              <InputText v-model="quickForm.ho_ten" placeholder="Nguyễn Văn A" class="w-full" />
            </div>
            <div class="form-row">
              <label>Pháp danh</label>
              <InputText v-model="quickForm.phap_danh" placeholder="Tâm Minh" class="w-full" />
            </div>
            <div class="form-row-2col">
              <div>
                <label>Năm sinh</label>
                <InputText v-model="quickForm.sinh_nam" placeholder="1990" />
              </div>
              <div>
                <label>Địa chỉ</label>
                <InputText v-model="quickForm.dia_chi" placeholder="TP.HCM" />
              </div>
            </div>
            <div class="form-actions">
              <Button label="Áp dụng" icon="pi pi-check" size="small" @click="applyQuickEntry" />
              <Button label="Xóa" icon="pi pi-refresh" size="small" severity="secondary" text @click="clearQuickForm" />
            </div>
          </div>
        </div>

        <!-- Expandable: Cài đặt nâng cao -->
        <div class="panel-section">
          <div class="panel-header clickable" @click="showAdvanced = !showAdvanced">
            <i :class="showAdvanced ? 'pi pi-chevron-down' : 'pi pi-chevron-right'" />
            ⚙️ Cài đặt nâng cao
          </div>
          <div v-if="showAdvanced" class="advanced-settings">
            <div class="setting-item">
              <label>Sử dụng Font VNI</label>
              <InputSwitch v-model="config.use_vni_font" />
            </div>
            <div class="setting-item">
              <label>In kèm ảnh nền (phôi mẫu)</label>
              <InputSwitch v-model="config.use_background_image" />
            </div>
            <div class="setting-item">
              <Button label="Reset mặc định" icon="pi pi-undo" size="small" severity="danger" text
                @click="onResetConfig" />
              <Button label="Export Config" icon="pi pi-download" size="small" severity="secondary" text
                @click="onExportConfig" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ EDIT FIELD DIALOG ============ -->
    <Dialog v-model:visible="showEditDialog" :header="editingField?.label || 'Chỉnh sửa'" modal
      :style="{ width: '360px' }">
      <div v-if="editingField" class="edit-dialog-body">
        <div class="form-row">
          <label>X (mm)</label>
          <InputNumber v-model="editingField.x" :minFractionDigits="1" :maxFractionDigits="1" />
        </div>
        <div class="form-row">
          <label>Y (mm)</label>
          <InputNumber v-model="editingField.y" :minFractionDigits="1" :maxFractionDigits="1" />
        </div>
        <div class="form-row">
          <label>Cỡ chữ</label>
          <InputNumber v-model="editingField.size" :min="6" :max="72" />
        </div>
        <div class="form-row">
          <label>Căn lề</label>
          <SelectButton v-model="editingField.align" :options="[
            { label: 'Trái', value: 'L' },
            { label: 'Giữa', value: 'C' },
            { label: 'Phải', value: 'R' }
          ]" optionLabel="label" optionValue="value" />
        </div>
      </div>
      <template #footer>
        <Button label="Hủy" severity="secondary" text @click="showEditDialog = false" />
        <Button label="Lưu" icon="pi pi-check" @click="saveFieldEdit" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  overflow: hidden;
}

/* ===== TOOLBAR ===== */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  background: var(--surface-card);
  border-bottom: 1px solid var(--surface-border);
  flex-wrap: wrap;
  min-height: 52px;
}
.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.toolbar-divider {
  width: 1px;
  height: 28px;
  background: var(--surface-border);
}

.btn-upload {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--primary-color);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-upload:hover { filter: brightness(1.1); }
.btn-upload i { font-size: 1.1rem; }

.record-badge {
  background: var(--green-100);
  color: var(--green-700);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}
.record-badge.demo {
  background: var(--blue-100);
  color: var(--blue-700);
}

.date-group {
  display: flex;
  align-items: center;
  gap: 6px;
}
.date-label {
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}
.date-input { width: 145px; }
:deep(.date-input .p-inputtext) { font-size: 0.85rem; padding: 6px 8px; }

/* Highlight animation khi chưa chọn ngày */
.date-group.highlight-pulse {
  animation: date-pulse 0.6s ease-in-out 5;
  border-radius: 8px;
}
@keyframes date-pulse {
  0%, 100% { background: transparent; box-shadow: none; }
  50% { background: rgba(251,146,60,0.2); box-shadow: 0 0 0 3px rgba(251,146,60,0.4); }
}

.lunar-edit-group {
  display: flex;
  align-items: center;
  gap: 4px;
  background: linear-gradient(135deg, var(--yellow-100), var(--orange-100));
  padding: 3px 10px;
  border-radius: 8px;
  white-space: nowrap;
}
.lunar-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--orange-800);
}
.lunar-inline {
  width: 130px;
  border: 1px solid transparent;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(255,255,255,0.5);
  color: var(--orange-900);
  transition: all 0.15s;
}
.lunar-inline.pl-input { width: 55px; text-align: center; }
.lunar-inline:hover { border-color: var(--orange-300); background: rgba(255,255,255,0.8); }
.lunar-inline:focus { outline: none; border-color: var(--orange-500); background: white; box-shadow: 0 0 0 2px rgba(251,146,60,0.2); }



/* ===== MAIN AREA ===== */
.main-area {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* LEFT: Records List */
.records-panel {
  width: 200px;
  min-width: 160px;
  border-right: 1px solid var(--surface-border);
  display: flex;
  flex-direction: column;
  background: var(--surface-ground);
}
.records-header {
  padding: 8px 12px;
  font-weight: 700;
  font-size: 0.8rem;
  color: var(--text-color);
  background: var(--surface-card);
  border-bottom: 1px solid var(--surface-border);
  display: flex;
  align-items: center;
  gap: 6px;
}
.records-list {
  flex: 1;
  overflow-y: auto;
}
.record-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  cursor: pointer;
  border-bottom: 1px solid var(--surface-100);
  transition: background 0.12s;
  font-size: 0.8rem;
}
.record-item:hover { background: var(--surface-hover); }
.record-item.active {
  background: var(--green-50);
  border-left: 3px solid var(--green-500);
}
.rec-idx {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--surface-200);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  flex-shrink: 0;
}
.record-item.active .rec-idx {
  background: var(--green-500);
  color: white;
}
.rec-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}
.rec-name {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rec-phap {
  font-size: 0.72rem;
  color: var(--text-color-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.records-empty {
  padding: 20px;
  text-align: center;
  color: var(--text-color-secondary);
  font-size: 0.8rem;
}
.rec-print-btn {
  margin-left: auto;
  flex-shrink: 0;
  border: none;
  background: none;
  cursor: pointer;
  padding: 3px 5px;
  border-radius: 4px;
  color: var(--text-color-secondary);
  opacity: 0.15;
  transition: all 0.15s;
  font-size: 0.8rem;
}
.rec-print-btn.visible,
.record-item:hover .rec-print-btn { opacity: 0.6; }
.rec-print-btn:hover { opacity: 1 !important; color: var(--green-600); background: var(--green-50); }

/* CENTER: Canvas */
.canvas-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: auto;
  padding: 12px;
}
.canvas-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.canvas-title {
  font-size: 0.85rem;
  color: var(--text-color-secondary);
}
.record-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}
.record-pos {
  font-weight: 700;
  font-size: 0.9rem;
  min-width: 60px;
  text-align: center;
}
.canvas-wrapper {
  display: flex;
  justify-content: center;
  overflow: auto;
}
.canvas-container {
  position: relative;
  display: inline-block;
}
.canvas-container canvas {
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  cursor: crosshair;
  max-width: 100%;
  height: auto;
}

/* Inline edit input overlay */
.canvas-inline-input {
  position: absolute;
  z-index: 10;
  padding: 3px 6px;
  border: 2px solid #22c55e;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.95);
  color: #1a1a1a;
  font-weight: 600;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15), 0 0 0 3px rgba(34, 197, 94, 0.2);
  outline: none;
  min-width: 60px;
}
.selection-info {
  text-align: center;
  padding: 6px;
  color: var(--green-600);
  font-weight: 600;
  font-size: 0.85rem;
}

/* RIGHT: Fields panel */
.fields-panel {
  width: 380px;
  min-width: 320px;
  border-left: 1px solid var(--surface-border);
  overflow-y: auto;
  background: var(--surface-ground);
}

.panel-section {
  border-bottom: 1px solid var(--surface-border);
}
.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--text-color);
  background: var(--surface-card);
}
.panel-header.clickable {
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}
.panel-header.clickable:hover { background: var(--surface-hover); }

/* Fields table */
.fields-table {
  font-size: 0.8rem;
}
.field-row {
  display: flex;
  align-items: center;
  padding: 6px 14px;
  border-bottom: 1px solid var(--surface-100);
  cursor: pointer;
  transition: background 0.15s;
}
.field-row:hover { background: var(--surface-hover); }
.field-row.selected { background: var(--green-50); border-left: 3px solid var(--green-500); }
.field-row.custom .col-name { color: var(--red-600); }
.field-row.header {
  font-weight: 700;
  background: var(--surface-card);
  cursor: default;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-color-secondary);
}
.col-name { width: 80px; min-width: 70px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-val { flex: 1; min-width: 50px; overflow: hidden; }
.col-x, .col-y { width: 42px; text-align: right; font-variant-numeric: tabular-nums; }
.col-action { width: 32px; text-align: center; }

/* Inline value editing */
.inline-val-input {
  width: 100%;
  border: 1px solid transparent;
  border-radius: 4px;
  padding: 2px 5px;
  font-size: 0.8rem;
  background: transparent;
  color: var(--text-color);
  transition: all 0.15s;
  font-variant-numeric: tabular-nums;
}
.inline-val-input:hover {
  border-color: var(--surface-300);
  background: var(--surface-0);
}
.inline-val-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background: var(--surface-0);
  box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb, 59, 130, 246), 0.15);
}
.val-readonly {
  color: var(--text-color-secondary);
  font-size: 0.78rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

/* Quick entry */
.quick-entry-form {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.form-row { display: flex; flex-direction: column; gap: 3px; }
.form-row label { font-size: 0.8rem; font-weight: 600; }
.form-row .required { color: var(--red-500); }
.form-row-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.form-row-2col label { font-size: 0.8rem; font-weight: 600; display: block; margin-bottom: 3px; }
.form-actions { display: flex; gap: 8px; margin-top: 4px; }
:deep(.quick-entry-form .p-inputtext) { font-size: 0.85rem; padding: 6px 8px; }

/* Advanced settings */
.advanced-settings {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 0.85rem;
}

/* Edit dialog */
.edit-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.edit-dialog-body .form-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.edit-dialog-body label {
  font-weight: 600;
  font-size: 0.85rem;
}
</style>
