/**
 * Chuyển đổi Dương lịch → Âm lịch (Việt Nam)
 * Port từ Python: core/lunar_converter.py
 */

const CAN = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý']
const CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']

export interface LunarResult {
    solar_day: number
    solar_month: number
    solar_year: number
    lunar_day: number
    lunar_month: number
    lunar_year: number
    lunar_year_name: string // "Ất Tỵ"
    buddhist_year: number   // dương + 544
}

function getCanChi(year: number): string {
    const canIndex = ((year - 4) % 10 + 10) % 10
    const chiIndex = ((year - 4) % 12 + 12) % 12
    return `${CAN[canIndex]} ${CHI[chiIndex]}`
}

function jdFromDate(dd: number, mm: number, yy: number): number {
    const a = Math.trunc((14 - mm) / 12)
    const y = yy + 4800 - a
    const m = mm + 12 * a - 3
    return dd + Math.trunc((153 * m + 2) / 5) + 365 * y + Math.trunc(y / 4) - Math.trunc(y / 100) + Math.trunc(y / 400) - 32045
}

function getNewMoonDay(k: number, timezone: number = 7): number {
    const T = k / 1236.85
    const T2 = T * T
    const T3 = T2 * T
    const dr = Math.PI / 180

    let Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 = Jd1 + 0.00033 * Math.cos((166.56 + 132.87 * T - 0.009173 * T2) * dr)

    const M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    const Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    const F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3

    let C1 = (0.1734 - 0.000393 * T) * Math.sin(M * dr)
    C1 += 0.0021 * Math.sin(2 * dr * M)
    C1 -= 0.4068 * Math.sin(Mpr * dr)
    C1 += 0.0161 * Math.sin(2 * dr * Mpr)
    C1 -= 0.0004 * Math.sin(3 * dr * Mpr)
    C1 += 0.0104 * Math.sin(2 * dr * F)
    C1 -= 0.0051 * Math.sin((M + Mpr) * dr)
    C1 -= 0.0074 * Math.sin((M - Mpr) * dr)
    C1 += 0.0004 * Math.sin((2 * F + M) * dr)
    C1 -= 0.0004 * Math.sin((2 * F - M) * dr)
    C1 -= 0.0006 * Math.sin((2 * F + Mpr) * dr)
    C1 += 0.0010 * Math.sin((2 * F - Mpr) * dr)
    C1 += 0.0005 * Math.sin((2 * Mpr + M) * dr)

    let deltaT: number
    if (T < -11) {
        deltaT = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
    } else {
        deltaT = -0.000278 + 0.000265 * T + 0.000262 * T2
    }

    const JdNew = Jd1 + C1 - deltaT
    return Math.trunc(JdNew + 0.5 + timezone / 24.0)
}

function getSunLongitude(jdn: number, timezone: number = 7): number {
    const T = (jdn - 2451545.5 - timezone / 24.0) / 36525
    const T2 = T * T
    const dr = Math.PI / 180

    const M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    const L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    let DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * Math.sin(dr * M)
    DL += (0.019993 - 0.000101 * T) * Math.sin(dr * 2 * M) + 0.000290 * Math.sin(dr * 3 * M)

    let L = L0 + DL
    L = L * dr
    L = L - Math.PI * 2 * Math.trunc(L / (Math.PI * 2))
    return Math.trunc(L / Math.PI * 6)
}

function getLunarMonth11(yy: number, timezone: number = 7): number {
    const off = jdFromDate(31, 12, yy) - 2415021
    const k = Math.trunc(off / 29.530588853)
    let nm = getNewMoonDay(k, timezone)
    const sunLong = getSunLongitude(nm, timezone)
    if (sunLong >= 9) {
        nm = getNewMoonDay(k - 1, timezone)
    }
    return nm
}

function getLeapMonthOffset(a11: number, timezone: number = 7): number {
    const k = Math.trunc((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    let last = 0
    let i = 1
    let arc = getSunLongitude(getNewMoonDay(k + i, timezone), timezone)
    while (arc !== last && i < 14) {
        last = arc
        i++
        arc = getSunLongitude(getNewMoonDay(k + i, timezone), timezone)
    }
    return i - 1
}

function solarToLunar(dd: number, mm: number, yy: number, timezone: number = 7): [number, number, number, number] {
    const dayNumber = jdFromDate(dd, mm, yy)
    const k = Math.trunc((dayNumber - 2415021.076998695) / 29.530588853)
    let monthStart = getNewMoonDay(k + 1, timezone)

    if (monthStart > dayNumber) {
        monthStart = getNewMoonDay(k, timezone)
    }

    let a11 = getLunarMonth11(yy, timezone)
    let b11 = a11
    let lunarYear: number

    if (a11 >= monthStart) {
        lunarYear = yy
        a11 = getLunarMonth11(yy - 1, timezone)
    } else {
        lunarYear = yy + 1
        b11 = getLunarMonth11(yy + 1, timezone)
    }

    const lunarDay = dayNumber - monthStart + 1
    const diff = Math.trunc((monthStart - a11) / 29)
    let lunarLeap = 0
    let lunarMonth = diff + 11

    if (b11 - a11 > 365) {
        const leapMonthDiff = getLeapMonthOffset(a11, timezone)
        if (diff >= leapMonthDiff) {
            lunarMonth = diff + 10
            if (diff === leapMonthDiff) {
                lunarLeap = 1
            }
        }
    }

    if (lunarMonth > 12) {
        lunarMonth = lunarMonth - 12
    }
    if (lunarMonth >= 11 && diff < 4) {
        lunarYear -= 1
    }

    return [lunarDay, lunarMonth, lunarYear, lunarLeap]
}

export function useLunarConverter() {
    /**
     * Chuyển đổi ngày dương lịch sang âm lịch
     * @param dateStr - "YYYY-MM-DD" hoặc Date object
     */
    function convertDate(dateStr: string | Date): LunarResult {
        let solarDay: number, solarMonth: number, solarYear: number

        if (typeof dateStr === 'string') {
            // Xử lý "2025-12-16 19:00:07" → lấy phần trước space
            const cleanDate = dateStr.includes(' ') ? dateStr.split(' ')[0] : dateStr
            const parts = cleanDate.split('-')
            solarYear = parseInt(parts[0])
            solarMonth = parseInt(parts[1])
            solarDay = parseInt(parts[2])
        } else {
            solarDay = dateStr.getDate()
            solarMonth = dateStr.getMonth() + 1
            solarYear = dateStr.getFullYear()
        }

        const [lunarDay, lunarMonth, lunarYear] = solarToLunar(solarDay, solarMonth, solarYear)
        const lunarYearName = getCanChi(lunarYear)
        const buddhistYear = solarYear + 544

        return {
            solar_day: solarDay,
            solar_month: solarMonth,
            solar_year: solarYear,
            lunar_day: lunarDay,
            lunar_month: lunarMonth,
            lunar_year: lunarYear,
            lunar_year_name: lunarYearName,
            buddhist_year: buddhistYear
        }
    }

    return { convertDate, getCanChi }
}
