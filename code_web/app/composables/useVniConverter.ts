/**
 * Chuyển đổi Unicode Tiếng Việt → VNI-Windows Encoding
 * Port 1:1 từ Python code_python/core/utils.py
 */

const UNICODE_CHARS = [
    "À", "Á", "Â", "Ã", "È", "É", "Ê", "Ì", "Í", "Ò",
    "Ó", "Ô", "Õ", "Ù", "Ú", "Ý", "à", "á", "â", "ã",
    "è", "é", "ê", "ì", "í", "ò", "ó", "ô", "õ", "ù",
    "ú", "ý", "Ă", "ă", "Đ", "đ", "Ĩ", "ĩ", "Ũ", "ũ",
    "Ơ", "ơ", "Ư", "ư", "Ạ", "ạ", "Ả", "ả", "Ấ", "ấ",
    "Ầ", "ầ", "Ẩ", "ẩ", "Ẫ", "ẫ", "Ậ", "ậ", "Ắ", "ắ",
    "Ằ", "ằ", "Ẳ", "ẳ", "Ẵ", "ẵ", "Ặ", "ặ", "Ẹ", "ẹ",
    "Ẻ", "ẻ", "Ẽ", "ẽ", "Ế", "ế", "Ề", "ề", "Ể", "ể",
    "Ễ", "ễ", "Ệ", "ệ", "Ỉ", "ỉ", "Ị", "ị", "Ọ", "ọ",
    "Ỏ", "ỏ", "Ố", "ố", "Ồ", "ồ", "Ổ", "ổ", "Ỗ", "ỗ",
    "Ộ", "ộ", "Ớ", "ớ", "Ờ", "ờ", "Ở", "ở", "Ỡ", "ỡ",
    "Ợ", "ợ", "Ụ", "ụ", "Ủ", "ủ", "Ứ", "ứ", "Ừ", "ừ",
    "Ử", "ử", "Ữ", "ữ", "Ự", "ự", "Ỳ", "ỳ", "Ỵ", "ỵ",
    "Ỷ", "ỷ", "Ỹ", "ỹ"
]

const VNI_WIN_CHARS = [
    "AØ", "AÙ", "AÂ", "AÕ", "EØ", "EÙ", "EÂ", "Ì", "Í", "OØ",
    "OÙ", "OÂ", "OÕ", "UØ", "UÙ", "YÙ", "aø", "aù", "aâ", "aõ",
    "eø", "eù", "eâ", "ì", "í", "oø", "où", "oâ", "oõ", "uø",
    "uù", "yù", "AÊ", "aê", "Ñ", "ñ", "Ó", "ó", "UÕ", "uõ",
    "Ô", "ô", "Ö", "ö", "AÏ", "aï", "AÛ", "aû", "AÁ", "aá",
    "AÀ", "aà", "AÅ", "aå", "AÃ", "aã", "AÄ", "aä", "AÉ", "aé",
    "AÈ", "aè", "AÚ", "aú", "AÜ", "aü", "AË", "aë", "EÏ", "eï",
    "EÛ", "eû", "EÕ", "eõ", "EÁ", "eá", "EÀ", "eà", "EÅ", "eå",
    "EÃ", "eã", "EÄ", "eä", "Æ", "æ", "Ò", "ò", "OÏ", "oï",
    "OÛ", "oû", "OÁ", "oá", "OÀ", "oà", "OÅ", "oå", "OÃ", "oã",
    "OÄ", "oä", "ÔÙ", "ôù", "ÔØ", "ôø", "ÔÛ", "ôû", "ÔÕ", "ôõ",
    "ÔÏ", "ôï", "UÏ", "uï", "UÛ", "uû", "ÖÙ", "öù", "ÖØ", "öø",
    "ÖÛ", "öû", "ÖÕ", "öõ", "ÖÏ", "öï", "YØ", "yø", "Î", "î",
    "YÛ", "yû", "YÕ", "yõ"
]

// Build lookup map
const UNICODE_TO_VNI_MAP: Record<string, string> = {}
UNICODE_CHARS.forEach((u, i) => {
    UNICODE_TO_VNI_MAP[u] = VNI_WIN_CHARS[i] ?? u
})

/**
 * Chuyển đổi chuỗi Unicode dựng sẵn sang VNI-Windows encoding
 * Dùng khi cần hiển thị text bằng font VNI (quyyfont.ttf)
 * 
 * @param text - Chuỗi Unicode tiếng Việt
 * @returns Chuỗi đã chuyển sang VNI encoding
 */
export function convertUnicodeToVni(text: string): string {
    if (!text) return ''

    // Normalize về NFC (dựng sẵn) để khớp với bảng map
    const normalized = text.normalize('NFC')

    let result = ''
    for (const char of normalized) {
        result += UNICODE_TO_VNI_MAP[char] || char
    }
    return result
}

/**
 * Kiểm tra xem chuỗi có chứa ký tự tiếng Việt không
 */
export function hasVietnamese(text: string): boolean {
    if (!text) return false
    const normalized = text.normalize('NFC')
    for (const char of normalized) {
        if (UNICODE_TO_VNI_MAP[char]) return true
    }
    return false
}
