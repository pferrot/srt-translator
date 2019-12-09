# SRT translator

Simple Python script to translate SRT files using Google translate.

## Requirements

* Python 3 (tested with 3.6.5)
* Google Translate Python library (install with `pip install google-cloud-translate==2.0.0`)
* Google service account key (instructions [here](https://cloud.google.com/docs/authentication/getting-started))

# Usage

```
SRT translator
--------------

usage: srt_translator.py [-h] [-f FILE] [-o [OUTPUT_DIRECTORY]]
                         [-c [CACHE_DIRECTORY]] [-sl SOURCE_LANGUAGE]
                         [-tl TARGET_LANGUAGE] [-ow [OVERWRITE_TARGET]]
                         [-nc [NO_CACHE]] [-nj [NO_TEXT_JOIN]]

Translates subtitles files (.srt) using Google Translate.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  The subtitle file to translate.
  -o [OUTPUT_DIRECTORY], --output_directory [OUTPUT_DIRECTORY]
                        Directory where the generated CSV files are stored,
                        default: 'output'.
  -c [CACHE_DIRECTORY], --cache_directory [CACHE_DIRECTORY]
                        Directory where cache files are stored, default:
                        'cache'.
  -sl SOURCE_LANGUAGE, --source_language SOURCE_LANGUAGE
                        Source language (see
                        https://cloud.google.com/translate/docs/languages for
                        supported language codes).
  -tl TARGET_LANGUAGE, --target_language TARGET_LANGUAGE
                        Target language (see
                        https://cloud.google.com/translate/docs/languages for
                        supported language codes).
  -ow [OVERWRITE_TARGET], --overwrite_target [OVERWRITE_TARGET]
                        Overwrite target file if it exists already, default:
                        no.
  -nc [NO_CACHE], --no_cache [NO_CACHE]
                        Do not use translation cache, default: no (i.e. uses
                        cache by default).
  -nj [NO_TEXT_JOIN], --no_text_join [NO_TEXT_JOIN]
                        Do not join texts appearing on multiline on a given
                        timestamp before translating, default: no (i.e. texts
                        on a given timestamp are joined by default, which can
                        avoid sending partial sentences to translation as they
                        might produce lower quality translations).
```

The list of language codes can be found [here](https://cloud.google.com/translate/docs/languages).

## Example
```
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google/cloud/key.json"

python3 srt_translator.py -f input/test.srt -sl en -tl fr
```

## SRT files structure
The SRT file structure is expected to look like this:

```
1
00:00:24,438 --> 00:00:29,271
(fan humming, clicking)

2
00:00:34,855 --> 00:00:36,855
(switch clicks)
(fan stops)

3
00:00:39,062 --> 00:00:40,271
(sighs)

4
00:00:50,479 --> 00:00:52,312
(sighs)

5
00:01:01,813 --> 00:01:04,312
♪ ♪

6
00:01:06,646 --> 00:01:08,688
(snoring)
(jet engines humming)

7
00:01:17,479 --> 00:01:19,146
♪ ♪

8
00:01:19,229 --> 00:01:22,104
(TV playing indistinctly)

9
00:01:48,938 --> 00:01:51,021
(engine revving)

10
00:01:55,271 --> 00:01:58,104
(wind blowing)

11
00:01:58,187 --> 00:02:00,187
♪ ♪

12
00:02:03,771 --> 00:02:04,855
Man:
Barry.

13
00:02:05,730 --> 00:02:08,563
Barry. Barry.
Wake up, buddy.

14
00:02:12,980 --> 00:02:14,980
Fuches?
Hey.

15
00:02:16,104 --> 00:02:18,104
How long have you
been watching me sleep?

16
00:02:18,187 --> 00:02:21,479
The money
from the Rochester job
just cleared.

17
00:02:21,563 --> 00:02:23,146
One less bad guy
in the world.
```
