import { usePrimeVue } from 'primevue/config'

export default defineNuxtPlugin(() => {
    const primevue = usePrimeVue()
    primevue.config.locale = {
        ...primevue.config.locale,
        // DatePicker Vietnamese locale
        dayNames: ['Chủ nhật', 'Thứ hai', 'Thứ ba', 'Thứ tư', 'Thứ năm', 'Thứ sáu', 'Thứ bảy'],
        dayNamesShort: ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
        dayNamesMin: ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
        monthNames: ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'],
        monthNamesShort: ['Th1', 'Th2', 'Th3', 'Th4', 'Th5', 'Th6', 'Th7', 'Th8', 'Th9', 'Th10', 'Th11', 'Th12'],
        today: 'Hôm nay',
        clear: 'Xóa',
        weekHeader: 'Tuần',
        firstDayOfWeek: 1, // Thứ hai
        dateFormat: 'dd/mm/yy',
        chooseDate: 'Chọn ngày',
        chooseMonth: 'Chọn tháng',
        chooseYear: 'Chọn năm',
        prevDecade: 'Thập kỷ trước',
        nextDecade: 'Thập kỷ sau',
        prevYear: 'Năm trước',
        nextYear: 'Năm sau',
        prevMonth: 'Tháng trước',
        nextMonth: 'Tháng sau',
    }
})
