


# Iqra

[![Discord](https://img.shields.io/discord/610613297452023837?label=Support%20Server)](https://discord.gg/Ud3MHJR) 
[Invite](https://discordapp.com/oauth2/authorize?client_id=706134327200841870&scope=bot&permissions=1068032)

This is a simple bot that can play recitations of surahs, ayahs and mushaf pages from the Qur'an in voice chat, along with a live audio stream from Makkah. It currently supports 120+ reciters.

## Commands

### -qplay
`-qplay`  instructs the bot to play a recitation of a surah, ayah or page from the Qur'an. 
#### Playing a surah
```
-qplay <surah number> <optional reciter>
```
If no reciter is specified, Mishary al-Afasy's recitation will be used. 
[Click here for the list of **surah** reciters](https://github.com/galacticwarrior9/QuranBot/blob/master/Reciters.md).

**Example 1**: `-qplay surah 1 abu bakr al-shatri`
This would play Abu Bakr al-Shatri's recitation of Surah al-Fatiha.

**Example 2**: `-qplay surah 112 abdul rahman al-sudais`
This would play Abdul Rahman al-Sudais' recitation of Surah al-Ikhlas. 

#### Playing a single ayah
```
-qplay ayah <surah>:<ayah> <optional reciter>
```
If no reciter is specified, Mishary al-Afasy's recitation will be used.

**Example**: `-qayah ayah 2:255 hatem farid`
This would play Hatem Farid's recitation of Surah al-Baqarah, ayah 255.

#### Playing a page from the mushaf

```
-qplay page <page number> <optional reciter>
```
`<page>` must be between 1 and 604.
If no reciter is specified, Mishary al-Afasy's recitation will be used.

**Example**: `-qplay page 10 hani al-rifai`
This would play Hani al-Rifai's recitation of the 10th page of a standard *mushaf*.

### -reciters
Gets the list of reciters for `-qplay`.
[Click here for the list of **surah** reciters.](https://github.com/galacticwarrior9/QuranBot/blob/master/Reciters.md)
#### -qsearch
Use 	`-qsearch` to search the list of reciters for `-qplay`. For example, `-qsearch dossary` would return Ibrahim al-Dossary and Yasser al-Dossary.

### -qlive
Plays a live audio stream.

 - Type `-qlive makkah` for a stream from al-Masjid al-Ḥarām in Makkah.
-    Type `-qlive quran` for Qur'an radio.

### -qvolume
Changes the volume of the bot. 
```
-qvolume <volume>
```
`<volume>` must be a number between 0 and 100, e.g. `-qvolume 50`.

### -qstop
Disconnects the bot from voice chat.

### -qhelp
Lists all commands and how to use them. 

## Sources

 - [mp3quran.net](http://mp3quran.net/) for the `-qplay` recitations.
 -  [everyayah.com](https://everyayah.com/) for the `-qpage` and `qayah`  recitations.
 - [haramain.info](http://www.haramain.info/) for the live Makkah audio.
