export const LANGUAGE_STORAGE_KEY = "proxmenux-ui-language"
export const DEFAULT_LANGUAGE = "en"

export type LanguageCode = "en" | "es" | "fr" | "de" | "it" | "pt" | "sk" | "sv" | "zh-CN"

export type LanguageStatus = "complete" | "partial" | "needs-translation"

export interface SupportedLanguage {
  code: LanguageCode
  englishName: string
  nativeName: string
  status: LanguageStatus
}

export const SUPPORTED_LANGUAGES: SupportedLanguage[] = [
  { code: "en", englishName: "English", nativeName: "English", status: "complete" },
  { code: "de", englishName: "German", nativeName: "Deutsch", status: "complete" },
  { code: "es", englishName: "Spanish", nativeName: "Español", status: "complete" },
  { code: "fr", englishName: "French", nativeName: "Français", status: "complete" },
  { code: "it", englishName: "Italian", nativeName: "Italiano", status: "complete" },
  { code: "pt", englishName: "Portuguese", nativeName: "Português", status: "complete" },
  { code: "sk", englishName: "Slovak", nativeName: "Slovenčina", status: "complete" },
  { code: "sv", englishName: "Swedish", nativeName: "Svenska", status: "complete" },
  { code: "zh-CN", englishName: "Chinese (Simplified)", nativeName: "简体中文", status: "complete" },
]

export function isSupportedLanguage(value: string | null | undefined): value is LanguageCode {
  return SUPPORTED_LANGUAGES.some((language) => language.code === value)
}

export function detectBrowserLanguage(): LanguageCode {
  if (typeof navigator === "undefined") return DEFAULT_LANGUAGE

  const candidates = [navigator.language, ...(navigator.languages || [])]
  for (const candidate of candidates) {
    const normalized = candidate?.toLowerCase()
    if (normalized === "zh" || normalized?.startsWith("zh-cn") || normalized?.startsWith("zh-hans")) {
      return "zh-CN"
    }
    const code = normalized?.split("-")[0]
    if (isSupportedLanguage(code)) return code
  }

  return DEFAULT_LANGUAGE
}
