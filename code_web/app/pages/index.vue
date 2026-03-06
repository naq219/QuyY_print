<script setup lang="ts">
import { PDFDocument, rgb } from 'pdf-lib'
import fontkit from '@pdf-lib/fontkit'
import { convertUnicodeToVni } from '~/composables/useVniConverter'
import type { ProcessedRecord } from '~/composables/useDataProcessor'
import type { LunarResult } from '~/composables/useLunarConverter'

useHead({ title: 'QuyY Print - In Lá Phái Quy Y' })

// ===================== COMPOSABLES =====================
const toast = useToast()
const { config, saveConfig, updateDateFields, clearDateFields } = useConfigManager()
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
const isGeneratingPdf = ref(false)
const pdfPreviewUrl = ref('')

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

const allFields = computed(() => {
  // Gộp field_positions + custom_fields cho render/chỉnh sửa
  const result: Record<string, { label: string; value: string; x: number; y: number; size: number; align: 'L' | 'C' | 'R'; isCustom: boolean }> = {}

  const fieldLabels: Record<string, string> = {
    phap_danh: 'Pháp danh', ho_ten: 'Họ tên', sinh_nam: 'Năm sinh', dia_chi: 'Địa chỉ',
    phat_lich: 'Phật lịch', ngay_duong: 'Ngày dương', thang_duong: 'Tháng dương',
    nam_duong: 'Năm dương', ngay_am: 'Ngày âm', thang_am: 'Tháng âm', nam_am: 'Năm âm'
  }

  // 4 field chính (data từ record hiện tại)
  for (const [key, pos] of Object.entries(config.value.field_positions)) {
    const rec = currentRecord.value
    let value = ''
    if (rec) {
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
watch([() => config.value.field_positions, () => config.value.custom_fields, currentRecordIndex, () => config.value.use_vni_font, selectedFields], () => {
  nextTick(() => drawCanvas())
}, { deep: true })

// ===================== MOUSE / KEYBOARD =====================
function getFieldAtPos(px: number, py: number): string | null {
  const scale = canvasScale.value
  let closest: string | null = null
  let minDist = 20

  for (const [key, field] of Object.entries(allFields.value)) {
    if (!field.value) continue
    const fx = field.x * scale
    const fy = field.y * scale
    const dist = Math.sqrt((px - fx) ** 2 + (py - fy) ** 2)
    if (dist < minDist) {
      minDist = dist
      closest = key
    }
  }
  return closest
}

function onCanvasMouseDown(e: MouseEvent) {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const x = (e.clientX - rect.left) * (canvas.width / rect.width)
  const y = (e.clientY - rect.top) * (canvas.height / rect.height)

  const clickedField = getFieldAtPos(x, y)

  if (clickedField) {
    if (e.ctrlKey || e.metaKey) {
      // Toggle selection
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
async function generatePdf() {
  if (processedRecords.value.length === 0) {
    toast.add({ severity: 'warn', summary: 'Không có dữ liệu', detail: 'Vui lòng tải Excel hoặc nhập nhanh', life: 3000 })
    return
  }
  if (!selectedDate.value && !isUsingDemoData.value) {
    toast.add({ severity: 'warn', summary: 'Chưa chọn ngày', detail: 'Vui lòng chọn Ngày Quy Y trước khi tạo PDF', life: 3000 })
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

    // Load background image (nếu bật)
    let bgImage: Awaited<ReturnType<typeof pdfDoc.embedJpg>> | null = null
    if (templateImage.value) {
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
        if (key === 'phap_danh') text = record.phap_danh
        else if (key === 'ho_ten') text = record.ho_ten
        else if (key === 'sinh_nam') text = record.sinh_nam
        else if (key === 'dia_chi') text = record.dia_chi
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

    toast.add({ severity: 'success', summary: 'PDF đã tạo', detail: `${processedRecords.value.length} trang`, life: 3000 })
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

function printPdf() {
  if (!pdfPreviewUrl.value) return
  const win = window.open(pdfPreviewUrl.value, '_blank')
  if (win) {
    win.addEventListener('load', () => { win.print() })
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
        <div class="date-group">
          <label class="date-label">📅 Ngày Quy Y:</label>
          <DatePicker v-model="selectedDate" dateFormat="dd/mm/yy" placeholder="Chọn ngày..." showIcon
            class="date-input" @update:modelValue="onDateChange" />
          <Button v-if="selectedDate" icon="pi pi-times" severity="secondary" text rounded size="small"
            @click="clearDate" v-tooltip.bottom="'Xóa ngày'" />
        </div>

        <!-- Lunar Info (hiện khi đã chọn ngày) -->
        <div v-if="lunarInfo" class="lunar-badge">
          🌙 {{ lunarInfo.lunar_day }}/{{ lunarInfo.lunar_month }} {{ lunarInfo.lunar_year_name }}
          · ☸️ PL {{ lunarInfo.buddhist_year }}
        </div>
      </div>

      <div class="toolbar-right">
        <!-- VNI Toggle -->
        <div class="vni-toggle">
          <label>Font VNI</label>
          <InputSwitch v-model="config.use_vni_font" />
        </div>

        <div class="toolbar-divider" />

        <!-- Actions -->
        <Button label="Tạo PDF" icon="pi pi-file-pdf" severity="success" :loading="isGeneratingPdf"
          @click="generatePdf" />
        <Button v-if="pdfPreviewUrl" label="Tải PDF" icon="pi pi-download" severity="info" outlined
          @click="downloadPdf" />
        <Button v-if="pdfPreviewUrl" label="In" icon="pi pi-print" severity="warn" @click="printPdf" />
      </div>
    </div>

    <!-- ============ MAIN AREA ============ -->
    <div class="main-area">
      <!-- LEFT: Canvas -->
      <div class="canvas-panel">
        <div class="canvas-header">
          <span class="canvas-title">
            <i class="pi pi-image" /> Canvas Preview ({{ A4_WIDTH_MM }}×{{ A4_HEIGHT_MM }}mm - A4 Landscape)
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
          <canvas ref="canvasRef" :width="canvasWidth" :height="canvasHeight" tabindex="0"
            @mousedown="onCanvasMouseDown" @mousemove="onCanvasMouseMove" @mouseup="onCanvasMouseUp"
            @mouseleave="onCanvasMouseUp" @keydown="onCanvasKeyDown" />
        </div>

        <!-- Selection info -->
        <div v-if="selectedFields.size > 0" class="selection-info">
          <i class="pi pi-arrows-alt" />
          {{ selectedFields.size }} field đang chọn – Phím ←↑→↓ di chuyển
        </div>
      </div>

      <!-- RIGHT: Fields Panel -->
      <div class="fields-panel">
        <!-- Fields list -->
        <div class="panel-section">
          <div class="panel-header">
            <i class="pi pi-list" /> Danh sách Fields
            <Button icon="pi pi-save" text rounded size="small" v-tooltip.left="'Lưu cấu hình'" @click="onSaveConfig" />
          </div>

          <div class="fields-table">
            <div class="field-row header">
              <span class="col-name">Field</span>
              <span class="col-x">X</span>
              <span class="col-y">Y</span>
              <span class="col-size">Size</span>
              <span class="col-action"></span>
            </div>
            <div v-for="(field, key) in allFields" :key="key" class="field-row"
              :class="{ selected: selectedFields.has(key as string), custom: field.isCustom }"
              @click="selectedFields = new Set([key as string])">
              <span class="col-name" :title="field.label">{{ field.label }}</span>
              <span class="col-x">{{ field.x.toFixed(1) }}</span>
              <span class="col-y">{{ field.y.toFixed(1) }}</span>
              <span class="col-size">{{ field.size }}</span>
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
              <label>In kèm ảnh nền (phôi mẫu)</label>
              <InputSwitch v-model="config.use_background_image" />
            </div>
            <div class="setting-item">
              <Button label="Reset mặc định" icon="pi pi-undo" size="small" severity="danger" text
                @click="() => { useConfigManager().resetConfig(); toast.add({ severity: 'info', summary: 'Đã reset', life: 2000 }) }" />
              <Button label="Export Config" icon="pi pi-download" size="small" severity="secondary" text
                @click="() => { const blob = new Blob([useConfigManager().exportConfig()], { type: 'application/json' }); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'quyy_config.json'; a.click() }" />
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

.lunar-badge {
  background: linear-gradient(135deg, var(--yellow-100), var(--orange-100));
  color: var(--orange-800);
  padding: 5px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.vni-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

/* ===== MAIN AREA ===== */
.main-area {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* LEFT: Canvas */
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
.canvas-wrapper canvas {
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  cursor: crosshair;
  max-width: 100%;
  height: auto;
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
  width: 320px;
  min-width: 280px;
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
.col-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-x, .col-y { width: 50px; text-align: right; font-variant-numeric: tabular-nums; }
.col-size { width: 35px; text-align: center; }
.col-action { width: 32px; text-align: center; }

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
