import { PDFDocument, rgb } from 'pdf-lib'
import fontkit from '@pdf-lib/fontkit'
import { convertUnicodeToVni } from '~/composables/useVniConverter'
import type { ProcessedRecord } from '~/composables/useDataProcessor'

// PDF page constants
const A4_WIDTH_MM = 297
const A4_HEIGHT_MM = 210
const MM_TO_PT = 2.8346

interface PdfDeps {
    config: Ref<any>
    processedRecords: Ref<ProcessedRecord[]>
    currentRecordIndex: Ref<number>
    fieldOverrides: Ref<Record<string, string>>
    selectedDate: Ref<Date | null>
    isUsingDemoData: Ref<boolean>
    highlightDatePicker: () => void
}

/**
 * Composable quản lý tạo PDF, in ấn
 */
export function usePdfGenerator(deps: PdfDeps) {
    const toast = useToast()
    const { config, processedRecords, currentRecordIndex, fieldOverrides, selectedDate, isUsingDemoData, highlightDatePicker } = deps

    // State
    const isGeneratingPdf = ref(false)
    const pdfPreviewUrl = ref('')

    // Helper: vẽ text lên trang PDF
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

    // Helper: load font & background
    async function loadPdfAssets(pdfDoc: any) {
        pdfDoc.registerFontkit(fontkit)
        const fontResp = await fetch('/quyyfont.ttf')
        const fontBytes = await fontResp.arrayBuffer()
        const customFont = await pdfDoc.embedFont(fontBytes)

        let bgImage: any = null
        if (config.value.use_background_image) {
            try {
                const bgResp = await fetch('/phoimau.jpg')
                const bgBytes = await bgResp.arrayBuffer()
                bgImage = await pdfDoc.embedJpg(bgBytes)
            } catch { /* skip */ }
        }
        return { customFont, bgImage }
    }

    // Helper: vẽ tất cả fields lên 1 trang
    function drawAllFields(page: any, record: ProcessedRecord, customFont: any, pageHeight: number, applyOverride = false) {
        for (const [key, pos] of Object.entries(config.value.field_positions)) {
            let text = ''
            if (applyOverride && record === processedRecords.value[currentRecordIndex.value] && fieldOverrides.value[key] !== undefined) {
                text = fieldOverrides.value[key]
            } else {
                if (key === 'phap_danh') text = record.phap_danh
                else if (key === 'ho_ten') text = record.ho_ten
                else if (key === 'sinh_nam') text = record.sinh_nam
                else if (key === 'dia_chi') text = record.dia_chi
            }
            if (!text) continue
            if (config.value.use_vni_font) text = convertUnicodeToVni(text)
            drawTextField(page, text, (pos as any).x, (pos as any).y, (pos as any).size, (pos as any).align, customFont, pageHeight)
        }
        for (const [, cf] of Object.entries(config.value.custom_fields)) {
            if (!(cf as any).value) continue
            let text = (cf as any).value
            if (config.value.use_vni_font) text = convertUnicodeToVni(text)
            drawTextField(page, text, (cf as any).x, (cf as any).y, (cf as any).size, (cf as any).align, customFont, pageHeight)
        }
    }

    // Main: Tạo PDF cho tất cả records
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
            const { customFont, bgImage } = await loadPdfAssets(pdfDoc)
            const pageWidth = A4_WIDTH_MM * MM_TO_PT
            const pageHeight = A4_HEIGHT_MM * MM_TO_PT

            for (const record of processedRecords.value) {
                const page = pdfDoc.addPage([pageWidth, pageHeight])
                if (bgImage) page.drawImage(bgImage, { x: 0, y: 0, width: pageWidth, height: pageHeight })
                drawAllFields(page, record, customFont, pageHeight, true)
            }

            const pdfBytes = await pdfDoc.save()
            const blob = new Blob([pdfBytes], { type: 'application/pdf' })
            if (pdfPreviewUrl.value) URL.revokeObjectURL(pdfPreviewUrl.value)
            pdfPreviewUrl.value = URL.createObjectURL(blob)

            toast.add({ severity: 'success', summary: 'PDF đã tạo', detail: `${processedRecords.value.length} trang - đang tải xuống...`, life: 3000 })
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

    // In qua iframe ẩn (không mở tab mới)
    function printViaIframe(blobUrl: string) {
        const old = document.getElementById('print-iframe')
        if (old) old.remove()
        const iframe = document.createElement('iframe')
        iframe.id = 'print-iframe'
        Object.assign(iframe.style, { position: 'fixed', top: '-9999px', left: '-9999px', width: '0', height: '0', border: 'none' })
        iframe.src = blobUrl
        document.body.appendChild(iframe)
        iframe.onload = () => {
            try { iframe.contentWindow?.focus(); iframe.contentWindow?.print() }
            catch { window.open(blobUrl, '_blank') }
        }
    }

    async function downloadPdf() {
        if (!pdfPreviewUrl.value) await generatePdf()
        if (pdfPreviewUrl.value) {
            const a = document.createElement('a')
            a.href = pdfPreviewUrl.value
            a.download = `QuyY_${processedRecords.value.length}pages.pdf`
            a.click()
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
        if (!pdfPreviewUrl.value) await generatePdf()
        printPdf()
    }

    async function printSingleRecord(idx: number) {
        const record = processedRecords.value[idx]
        if (!record) return
        try {
            const pdfDoc = await PDFDocument.create()
            const { customFont, bgImage } = await loadPdfAssets(pdfDoc)
            const pageWidth = A4_WIDTH_MM * MM_TO_PT
            const pageHeight = A4_HEIGHT_MM * MM_TO_PT
            const page = pdfDoc.addPage([pageWidth, pageHeight])
            if (bgImage) page.drawImage(bgImage, { x: 0, y: 0, width: pageWidth, height: pageHeight })
            drawAllFields(page, record, customFont, pageHeight, false)

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

    return {
        isGeneratingPdf,
        pdfPreviewUrl,
        generatePdf,
        downloadPdf,
        quickPrint,
        printSingleRecord
    }
}
