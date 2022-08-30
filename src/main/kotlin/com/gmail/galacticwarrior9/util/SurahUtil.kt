package com.gmail.galacticwarrior9.util

import com.gmail.galacticwarrior9.Iqra
import com.google.gson.JsonObject
import com.google.gson.JsonParser
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException
import java.io.InputStream
import java.io.InputStreamReader
import java.net.URL
import java.net.URLConnection

const val surahInfoUrl = "https://api.quran.com/api/v4/chapters/%d?language=%s"

enum class RevelationLocation {
    MAKKAH,
    MADINAH;

    fun asAdjective(): String {
        return when (this) {
            MADINAH -> "Medinan"
            MAKKAH -> "Meccan"
        }
    }
}

data class SurahMeta(val arabicName: String,
                     val transliteratedName: String,
                     val translatedName: String,
                     val verseCount: Int,
                     val revelationLocation: RevelationLocation
)

/**
 * @param surahNum - the order in which this surah appears in the Qur'an.
 * @param languageCode - the quran.com API language code to use when fetching the SurahMeta.
 * @return the SurahMeta for this surah, or null if the SurahMeta could not be retrieved.
 * @throws IllegalArgumentException if an invalid surah number was specified.
 */
suspend fun getSurahMeta(surahNum: Int, languageCode: String = "en"): SurahMeta? = withContext(Dispatchers.IO) {
    if (surahNum < 1 || surahNum > 114) {
        throw IllegalArgumentException("Invalid surah number.")
    }

    val url = URL(surahInfoUrl.format(surahNum, languageCode))
    val request: URLConnection
    try {
        request = url.openConnection()
        request.connect()
    } catch (ex: IOException) {
        Iqra.logger.error("Failed to connect to $url!")
        return@withContext null
    }

    val json: JsonObject
    try {
        json = JsonParser.parseReader(InputStreamReader(request.content as InputStream)).asJsonObject.get("chapter").asJsonObject
    } catch (ex: Exception) {
        Iqra.logger.error("Failed to parse JSON at $url!")
        return@withContext null
    }

    val arabicName = json.get("name_arabic").asString
    val transliteratedName = json.get("name_complex").asString
    val verseCount = json.get("verses_count").asInt
    val translatedName = json.get("translated_name").asJsonObject.get("name").asString
    val revelationLocation = json.get("revelation_place").asString

    return@withContext SurahMeta(arabicName, transliteratedName, translatedName, verseCount, RevelationLocation.valueOf(revelationLocation.toUpperCase()))
}
