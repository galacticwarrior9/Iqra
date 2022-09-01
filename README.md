# Iqra

[![Discord](https://img.shields.io/discord/610613297452023837?label=Support%20Server)](https://discord.gg/Ud3MHJR)
![License](https://img.shields.io/github/license/galacticwarrior9/Iqra)
![Contributors](https://img.shields.io/github/contributors/galacticwarrior9/Iqra)


**Iqra** is an [open-source](https://github.com/galacticwarrior9/Iqra) Discord bot that plays Qur'an recitations in voice channels. Over 140
reciters can be listened to on both a surah-by-surah and ayah-and-ayah basis. 

The bot is written in [Kotlin](https://kotlinlang.org/docs/home.html) and uses the [Java Discord API (JDA)](https://github.com/DV8FromTheWorld/JDA).
The recitations themselves are retrieved from [mp3quran.net](https://mp3quran.net).

## Documentation


### Browing reciters

There are two lists of reciters available: one for surah-by-surah recitations (`/reciters list surah`), and the other for ayah-by-ayah recitations (`/reciters list ayah`).

You can search for specific reciters within these lists using `/reciters search [surah/ayah] <name of reciter>`.

These reciters can be used in the `/play` command to 


### Playing recitations


To play a recitation, you first need to join a voice channel that the bot can also join. You can then use the `/play`
command to select and play a recitation.

**Whole surah recitations** can be played using `/play surah <surah number> <optional reciter name>`, where the reciter name
is an *exact* reciter name from `/reciters list surah`. 

Suppose we wanted to play Abdulrasheed Soufi's recitation of Surah al-Fatihah. We would use the following command:

```kotlin
/play surah 1 Abdulrasheed Soufi
```

**Ayah-by-ayah recitations** can be played using `/play ayah <surah number> <ayah> <optional end ayah> <optional reciter name>`.

The following would play Sahl Yassin's recitation of the first verse of Surah al-Baqarah:

```kotlin
/play ayah 2 1 Sahl Yassin
```

What if we wanted to only listen to verses 255-260? We would just need to specify an end ayah, like so:

```kotlin
/play ayah 2 255 260 Sahl Yassin
```

If all this seems confusing, don't worry — the commands will auto-complete as you type them. 


### Radio

The `/radio` command will stream an online Qur'an radio station to your voice channel. It tends to play a selection of 
short recitations.

### Playback Control


You can pause the bot using `/pause` and then resume it again using `/resume`. If you need the bot to stop playing and 
leave the channel, use `/leave`.


## Information for Developers

To build Iqra, you require JDK 17 or above on your system. Clone this repository, install [Maven](https://maven.apache.org/install.html) and then run the following command:

```
mvn clean install
```

This will build an executable JAR with shaded dependencies in the `/target` folder. 

The bot token must be set in a system environment variable ([Windows]((https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html))/[Linux](https://linuxize.com/post/how-to-set-and-list-environment-variables-in-linux/)) named `token`. You can alternatively hardcode a token in `Launcher.kt`, although this is not recommended.
