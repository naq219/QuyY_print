<script setup lang="ts">
import { PDFDocument, rgb } from 'pdf-lib'
import fontkit from '@pdf-lib/fontkit'

// ===================== STATE =====================
const toast = useToast()

// Canvas refs
const canvasRef = ref<HTMLCanvasElement | null>(null)
const canvasContainerRef = ref<HTMLDivElement | null>(null)

// Template image
const templateImage = ref<HTMLImageElement | null>(null)
const templateLoaded = ref(false)

// A4 Landscape dimensions (mm)
const A4_WIDTH_MM = 297
const A4_HEIGHT_MM = 210
const MM_TO_PT = 2.8346 // mm to PDF points

// Canvas scale (pixels per mm)
const canvasScale = ref(2.5)
const canvasWidth = computed(() => Math.round(A4_WIDTH_MM * canvasScale.value))
const canvasHeight = computed(() => Math.round(A4_HEIGHT_MM * canvasScale.value))

// Fields
interface FieldConfig {
  label: string
  value: string
  x: number // mm
  y: number // mm
  size: number // font size
  align: 'L' | 'C' | 'R'
  color: string
}

const fields = ref<Record<string, FieldConfig>>({
  phap_danh: { label: 'Pháp danh', value: 'Tâm Minh', x: 199.0, y: 139.4, size: 18, align: 'L', color: '#0000ff' },
  ho_ten: { label: 'Họ tên', value: 'Nguyễn Văn An', x: 199.8, y: 128.2, size: 18, align: 'L', color: '#0000ff' },
  sinh_nam: { label: 'Năm sinh', value: '1990', x: 199.4, y: 147.0, size: 12, align: 'L', color: '#0000ff' },
  dia_chi: { label: 'Địa chỉ', value: 'P.10, Q.Gò Vấp, TP.HCM', x: 199.8, y: 154.2, size: 12, align: 'L', color: '#0000ff' },
})

// Selected fields
const selectedFields = ref<Set<string>>(new Set())
const isDragging = ref(false)
const dragStartPos = ref({ x: 0, y: 0 })
const dragFieldStartPositions = ref<Record<string, { x: number; y: number }>>({})

// Editing
const editingField = ref<string | null>(null)
const editDialog = ref(false)
const editForm = ref({ x: 0, y: 0, size: 12, value: '', align: 'L' as 'L' | 'C' | 'R' })

// PDF Preview
const pdfPreviewUrl = ref<string | null>(null)
const generating = ref(false)

// Align options
const alignOptions = [
  { label: 'Trái (L)', value: 'L' },
  { label: 'Giữa (C)', value: 'C' },
  { label: 'Phải (R)', value: 'R' }
]

// ===================== TEMPLATE IMAGE =====================
onMounted(() => {
  loadTemplateImage('/phoimau.jpg')
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  if (pdfPreviewUrl.value) URL.revokeObjectURL(pdfPreviewUrl.value)
})

function loadTemplateImage(src: string) {
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => {
    templateImage.value = img
    templateLoaded.value = true
    nextTick(() => redrawCanvas())
  }
  img.onerror = () => {
    templateLoaded.value = false
    toast.add({ severity: 'warn', summary: 'Chưa có phôi mẫu', detail: 'Upload ảnh phôi mẫu để bắt đầu', life: 3000 })
    nextTick(() => redrawCanvas())
  }
  img.src = src
}

// Upload custom template
const fileInputRef = ref<HTMLInputElement | null>(null)
function triggerUpload() {
  fileInputRef.value?.click()
}
function handleFileUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    toast.add({ severity: 'error', summary: 'Lỗi', detail: 'Chỉ hỗ trợ file ảnh (jpg, png)', life: 3000 })
    return
  }
  const url = URL.createObjectURL(file)
  loadTemplateImage(url)
  toast.add({ severity: 'success', summary: 'Đã tải', detail: `Phôi mẫu: ${file.name}`, life: 2000 })
}

// ===================== CANVAS DRAWING =====================
function redrawCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Clear
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

  // Draw background
  if (templateImage.value && templateLoaded.value) {
    ctx.drawImage(templateImage.value, 0, 0, canvasWidth.value, canvasHeight.value)
  } else {
    // Placeholder
    ctx.fillStyle = '#f0f0f0'
    ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
    ctx.fillStyle = '#999'
    ctx.font = '16px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('Chưa có phôi mẫu - Click "Upload Phôi Mẫu" để bắt đầu', canvasWidth.value / 2, canvasHeight.value / 2)
  }

  // Draw fields
  const scale = canvasScale.value
  for (const [name, field] of Object.entries(fields.value)) {
    const isSelected = selectedFields.value.has(name)
    const x = field.x * scale
    const y = field.y * scale
    const fontSize = Math.max(8, field.size * scale * 0.35)

    ctx.font = `${fontSize}px Arial`
    ctx.fillStyle = isSelected ? '#00cc00' : field.color

    // Align
    if (field.align === 'C') ctx.textAlign = 'center'
    else if (field.align === 'R') ctx.textAlign = 'right'
    else ctx.textAlign = 'left'

    ctx.fillText(field.value || `[${field.label}]`, x, y)

    // Selection highlight
    if (isSelected) {
      const metrics = ctx.measureText(field.value || `[${field.label}]`)
      let rectX = x
      if (field.align === 'C') rectX = x - metrics.width / 2
      else if (field.align === 'R') rectX = x - metrics.width

      ctx.strokeStyle = '#00cc00'
      ctx.lineWidth = 1.5
      ctx.setLineDash([4, 2])
      ctx.strokeRect(rectX - 3, y - fontSize - 2, metrics.width + 6, fontSize + 8)
      ctx.setLineDash([])
    }
  }
  ctx.textAlign = 'left' // Reset
}

// Watch fields changes
watch(fields, () => redrawCanvas(), { deep: true })
watch(selectedFields, () => redrawCanvas(), { deep: true })

// ===================== MOUSE EVENTS =====================
function getFieldAtPosition(px: number, py: number): string | null {
  const canvas = canvasRef.value
  if (!canvas) return null
  const ctx = canvas.getContext('2d')
  if (!ctx) return null

  const scale = canvasScale.value
  // Check fields in reverse order (top-most first)
  const entries = Object.entries(fields.value).reverse()
  for (const [name, field] of entries) {
    const x = field.x * scale
    const y = field.y * scale
    const fontSize = Math.max(8, field.size * scale * 0.35)
    ctx.font = `${fontSize}px Arial`
    const metrics = ctx.measureText(field.value || `[${field.label}]`)

    let rectX = x
    if (field.align === 'C') rectX = x - metrics.width / 2
    else if (field.align === 'R') rectX = x - metrics.width

    if (px >= rectX - 5 && px <= rectX + metrics.width + 5 &&
        py >= y - fontSize - 3 && py <= y + 6) {
      return name
    }
  }
  return null
}

function onCanvasMouseDown(e: MouseEvent) {
  const rect = canvasRef.value?.getBoundingClientRect()
  if (!rect) return
  const px = e.clientX - rect.left
  const py = e.clientY - rect.top

  const hitField = getFieldAtPosition(px, py)

  if (hitField) {
    if (e.ctrlKey || e.metaKey) {
      // Ctrl+Click: toggle
      if (selectedFields.value.has(hitField)) {
        selectedFields.value.delete(hitField)
      } else {
        selectedFields.value.add(hitField)
      }
    } else {
      // Normal click: select single
      if (!selectedFields.value.has(hitField)) {
        selectedFields.value.clear()
        selectedFields.value.add(hitField)
      }
    }

    // Start drag
    isDragging.value = true
    dragStartPos.value = { x: px, y: py }
    dragFieldStartPositions.value = {}
    for (const fname of selectedFields.value) {
      dragFieldStartPositions.value[fname] = { x: fields.value[fname].x, y: fields.value[fname].y }
    }
  } else {
    // Click empty area
    selectedFields.value.clear()
  }
  // Trigger reactivity
  selectedFields.value = new Set(selectedFields.value)
}

function onCanvasMouseMove(e: MouseEvent) {
  if (!isDragging.value || selectedFields.value.size === 0) return
  const rect = canvasRef.value?.getBoundingClientRect()
  if (!rect) return

  const px = e.clientX - rect.left
  const py = e.clientY - rect.top
  const dx = (px - dragStartPos.value.x) / canvasScale.value
  const dy = (py - dragStartPos.value.y) / canvasScale.value

  for (const fname of selectedFields.value) {
    const startPos = dragFieldStartPositions.value[fname]
    if (startPos) {
      fields.value[fname].x = Math.round((startPos.x + dx) * 10) / 10
      fields.value[fname].y = Math.round((startPos.y + dy) * 10) / 10
    }
  }
}

function onCanvasMouseUp() {
  isDragging.value = false
}

// ===================== KEYBOARD EVENTS =====================
function handleKeyDown(e: KeyboardEvent) {
  // Only handle if no input is focused
  if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'TEXTAREA') return
  if (editDialog.value) return

  const step = 0.4 // mm per arrow key press

  if (selectedFields.value.size > 0) {
    let dx = 0, dy = 0
    if (e.key === 'ArrowLeft') dx = -step
    else if (e.key === 'ArrowRight') dx = step
    else if (e.key === 'ArrowUp') dy = -step
    else if (e.key === 'ArrowDown') dy = step

    if (dx !== 0 || dy !== 0) {
      e.preventDefault()
      for (const fname of selectedFields.value) {
        fields.value[fname].x = Math.round((fields.value[fname].x + dx) * 10) / 10
        fields.value[fname].y = Math.round((fields.value[fname].y + dy) * 10) / 10
      }
    }
  }

  // Ctrl+A: select all
  if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
    e.preventDefault()
    selectedFields.value = new Set(Object.keys(fields.value))
  }

  // Escape: deselect all
  if (e.key === 'Escape') {
    selectedFields.value.clear()
    selectedFields.value = new Set()
  }
}

// ===================== FIELD EDITING =====================
function openEditDialog(fieldName: string) {
  editingField.value = fieldName
  const f = fields.value[fieldName]
  editForm.value = { x: f.x, y: f.y, size: f.size, value: f.value, align: f.align }
  editDialog.value = true
}

function saveEditDialog() {
  if (!editingField.value) return
  const f = fields.value[editingField.value]
  f.x = editForm.value.x
  f.y = editForm.value.y
  f.size = editForm.value.size
  f.value = editForm.value.value
  f.align = editForm.value.align
  editDialog.value = false
  toast.add({ severity: 'success', summary: 'Đã cập nhật', detail: `Field: ${editingField.value}`, life: 1500 })
}

function selectFieldFromTable(fieldName: string) {
  selectedFields.value.clear()
  selectedFields.value.add(fieldName)
  selectedFields.value = new Set(selectedFields.value)
}

// ===================== PDF GENERATION =====================
async function generatePreviewPDF() {
  generating.value = true
  try {
    const pdfDoc = await PDFDocument.create()
    pdfDoc.registerFontkit(fontkit)

    // Try to load custom font, fallback to standard
    let customFont
    try {
      const fontResp = await fetch('/quyyfont.ttf')
      if (fontResp.ok) {
        const fontBytes = await fontResp.arrayBuffer()
        customFont = await pdfDoc.embedFont(fontBytes)
      }
    } catch {
      // Fallback: use standard font
    }

    // A4 Landscape: 841.89 x 595.28 points
    const pageWidth = A4_WIDTH_MM * MM_TO_PT
    const pageHeight = A4_HEIGHT_MM * MM_TO_PT
    const page = pdfDoc.addPage([pageWidth, pageHeight])

    // Draw background image
    if (templateImage.value && templateLoaded.value) {
      try {
        // Get image data from canvas
        const tempCanvas = document.createElement('canvas')
        tempCanvas.width = 2000
        tempCanvas.height = Math.round(2000 * A4_HEIGHT_MM / A4_WIDTH_MM)
        const tempCtx = tempCanvas.getContext('2d')!
        tempCtx.drawImage(templateImage.value, 0, 0, tempCanvas.width, tempCanvas.height)
        const dataUrl = tempCanvas.toDataURL('image/jpeg', 0.9)
        const base64 = dataUrl.split(',')[1]
        const bgBytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0))
        const bgImage = await pdfDoc.embedJpg(bgBytes)
        page.drawImage(bgImage, { x: 0, y: 0, width: pageWidth, height: pageHeight })
      } catch (err) {
        console.warn('Could not embed background image:', err)
      }
    }

    // Draw text fields
    const font = customFont || await pdfDoc.embedFont('Helvetica' as any)
    for (const [, field] of Object.entries(fields.value)) {
      const x = field.x * MM_TO_PT
      const y = pageHeight - (field.y * MM_TO_PT) // Flip Y axis
      const text = field.value || ''
      if (!text) continue

      const textWidth = font.widthOfTextAtSize(text, field.size)
      let drawX = x
      if (field.align === 'C') drawX = x - textWidth / 2
      else if (field.align === 'R') drawX = x - textWidth

      page.drawText(text, {
        x: drawX,
        y: y,
        size: field.size,
        font: font,
        color: rgb(0, 0, 0)
      })
    }

    const pdfBytes = await pdfDoc.save()
    const blob = new Blob([pdfBytes], { type: 'application/pdf' })

    if (pdfPreviewUrl.value) URL.revokeObjectURL(pdfPreviewUrl.value)
    pdfPreviewUrl.value = URL.createObjectURL(blob)

    toast.add({ severity: 'success', summary: 'PDF sẵn sàng!', detail: 'Xem preview bên dưới hoặc tải về', life: 2000 })
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Lỗi tạo PDF', detail: err.message, life: 5000 })
  } finally {
    generating.value = false
  }
}

function downloadPDF() {
  if (!pdfPreviewUrl.value) return
  const a = document.createElement('a')
  a.href = pdfPreviewUrl.value
  a.download = 'quyy_print_test.pdf'
  a.click()
}

function printPDF() {
  if (!pdfPreviewUrl.value) return
  const w = window.open(pdfPreviewUrl.value)
  if (w) {
    w.addEventListener('load', () => {
      setTimeout(() => w.print(), 500)
    })
  }
}
</script>

<template>
  <div class="grid gap-4">
    <!-- Toolbar -->
    <div class="col-12">
      <div class="card p-3">
        <div class="flex flex-wrap items-center gap-3">
          <Button icon="pi pi-upload" label="Upload Phôi Mẫu" severity="secondary" size="small" @click="triggerUpload" />
          <input ref="fileInputRef" type="file" accept="image/*" class="hidden" @change="handleFileUpload" />

          <Divider layout="vertical" class="hidden md:block" />

          <Button icon="pi pi-file-pdf" label="Tạo PDF Preview" severity="warn" size="small"
                  :loading="generating" @click="generatePreviewPDF" />
          <Button icon="pi pi-download" label="Tải PDF" severity="success" size="small"
                  :disabled="!pdfPreviewUrl" @click="downloadPDF" />
          <Button icon="pi pi-print" label="In Ngay" severity="info" size="small"
                  :disabled="!pdfPreviewUrl" @click="printPDF" />

          <div class="ml-auto text-sm text-muted-color">
            <span v-if="selectedFields.size > 0" class="text-primary font-semibold">
              {{ selectedFields.size }} field đang chọn – Phím ←↑→↓ di chuyển
            </span>
            <span v-else>Click field để chọn • Ctrl+Click chọn nhiều • Ctrl+A chọn tất cả</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Canvas + Field Table -->
    <div class="col-12">
      <div class="flex gap-4 flex-col xl:flex-row">
        <!-- Canvas -->
        <div class="flex-1">
          <div class="card p-3">
            <div class="text-sm font-semibold mb-2 text-muted-color">
              📐 Canvas Preview ({{ A4_WIDTH_MM }}×{{ A4_HEIGHT_MM }}mm - A4 Landscape)
            </div>
            <div ref="canvasContainerRef" class="canvas-container" style="overflow: auto; border: 1px solid var(--surface-border); border-radius: 8px;">
              <canvas
                ref="canvasRef"
                :width="canvasWidth"
                :height="canvasHeight"
                style="cursor: crosshair; display: block;"
                @mousedown="onCanvasMouseDown"
                @mousemove="onCanvasMouseMove"
                @mouseup="onCanvasMouseUp"
                @mouseleave="onCanvasMouseUp"
              />
            </div>
          </div>
        </div>

        <!-- Field Table -->
        <div class="xl:w-[420px]">
          <div class="card p-3">
            <div class="text-sm font-semibold mb-2 text-muted-color">📋 Danh sách Fields</div>
            <DataTable :value="Object.entries(fields).map(([k, v]) => ({ name: k, ...v }))"
                       size="small" stripedRows scrollable scrollHeight="400px"
                       selectionMode="single"
                       @row-click="(e: any) => selectFieldFromTable(e.data.name)"
                       @row-dblclick="(e: any) => openEditDialog(e.data.name)">
              <Column field="label" header="Field" style="min-width: 100px" />
              <Column field="x" header="X (mm)" style="min-width: 70px">
                <template #body="{ data }">{{ data.x.toFixed(1) }}</template>
              </Column>
              <Column field="y" header="Y (mm)" style="min-width: 70px">
                <template #body="{ data }">{{ data.y.toFixed(1) }}</template>
              </Column>
              <Column field="size" header="Size" style="min-width: 50px" />
              <Column field="align" header="Align" style="min-width: 50px" />
              <Column header="" style="width: 40px">
                <template #body="{ data }">
                  <Button icon="pi pi-pencil" text rounded size="small" @click.stop="openEditDialog(data.name)" />
                </template>
              </Column>
            </DataTable>
          </div>
        </div>
      </div>
    </div>

    <!-- PDF Preview -->
    <div v-if="pdfPreviewUrl" class="col-12">
      <div class="card p-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-muted-color">📄 PDF Preview</span>
          <div class="flex gap-2">
            <Button icon="pi pi-download" label="Tải PDF" size="small" severity="success" @click="downloadPDF" />
            <Button icon="pi pi-print" label="In Ngay" size="small" @click="printPDF" />
          </div>
        </div>
        <iframe :src="pdfPreviewUrl" style="width: 100%; height: 500px; border: 1px solid var(--surface-border); border-radius: 8px;" />
      </div>
    </div>
  </div>

  <!-- Edit Dialog -->
  <Dialog v-model:visible="editDialog" :header="`Chỉnh sửa: ${editingField}`" modal :style="{ width: '400px' }">
    <div class="flex flex-col gap-4 pt-2">
      <div class="flex flex-col gap-1">
        <label class="text-sm font-semibold">Giá trị hiển thị</label>
        <InputText v-model="editForm.value" />
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div class="flex flex-col gap-1">
          <label class="text-sm font-semibold">X (mm)</label>
          <InputNumber v-model="editForm.x" :min="0" :max="297" :maxFractionDigits="1" />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-sm font-semibold">Y (mm)</label>
          <InputNumber v-model="editForm.y" :min="0" :max="210" :maxFractionDigits="1" />
        </div>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div class="flex flex-col gap-1">
          <label class="text-sm font-semibold">Font Size</label>
          <InputNumber v-model="editForm.size" :min="6" :max="72" />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-sm font-semibold">Căn lề</label>
          <Select v-model="editForm.align" :options="alignOptions" optionLabel="label" optionValue="value" />
        </div>
      </div>
    </div>
    <template #footer>
      <Button label="Hủy" severity="secondary" text @click="editDialog = false" />
      <Button label="Lưu" icon="pi pi-check" @click="saveEditDialog" />
    </template>
  </Dialog>
</template>

<style scoped>
.canvas-container {
  max-width: 100%;
}
</style>
