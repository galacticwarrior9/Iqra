
# QuranBot

[![Discord](https://img.shields.io/discord/610613297452023837?label=Support%20Server)](https://discord.gg/Ud3MHJR) 
[Invite](https://discordapp.com/oauth2/authorize?client_id=706134327200841870&scope=bot&permissions=1068032)

This is a simple bot that can play Qur'an recitations in voice chat. There are currently 35+ reciters available. 

All audio is sourced from [QuranicAudio](https://quranicaudio.com/).

If you are looking for a bot that can send Qur'an in text chat, check out [IslamBot](https://top.gg/bot/352815253828141056).

## Commands

### -qplay
Plays a surah in the voice channel you are connected to. 
```
-qplay <surah number> <optional reciter>
```
If no reciter is specified, Mishary al-Afasy's recitation will be used.

**Example 1**: `-qplay 1 abu bakr al-shatri`
This would play Abu Bakr al-Shatri's recitation of Surah al-Fatiha.

**Example 2**: `-qplay 112 sudais`
This would play Abdul Rahman al-Sudais' recitation of Surah al-Ikhlas. 

### -qayah
Plays the recitation of a single ayah in voice chat.
```
-qplay <surah>:<ayah> <optional reciter>
```
If no reciter is specified, Mishary al-Afasy's recitation will be used.

**Example**: `-qayah 2:255 hatem farid`
This would play Hatem Farid's recitation of Surah al-Baqarah, ayah 255.

### -qpage
Plays the recitation of a page from a standard 604-page *mushaf*.
```
-qpage <page> <optional reciter>
```
If no reciter is specified, Mishary al-Afasy's recitation will be used.

**Example**: `-qayah 10 yasser al-dussary`
This would play Yasser al-Dussary's recitation of the 10th page of a standard *mushaf*.

### -reciters
Gets the list of reciters for `-qplay`, `-qayah` and `-qpage`.

### -qlive
Plays a live audio stream from al-Masjid al-Ḥarām in Makkah.

### -qvolume
Changes the volume of the bot. 
```
-qvolume <volume>
```
`<volume>` must be a number between 0 and 100, e.g. `-qvolume 50`.

### -qstop
Stops playing.

### -qhelp
Lists all commands and how to use them. 
