from os import listdir
from os.path import isfile, join
import argparse
import json
import os
import six

def str2bool(v):
    """Return the Boolean value corresponding to a String.

    'yes', 'true', 't', 'y', '1' (case insensitive) will return True.
    'no', 'false', 'f', 'n', '0' (case insensitive) will return false.
    Any other value will raise a argparse.ArgumentTypeError.
    """
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def get_content(filename):
    with open(filename) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content

# See https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/translate/cloud-client/snippets.py
def translate_text_v2(text, source_language, target_language):
    # [START translate_translate_text]
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate
    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(
        text, source_language=source_language, target_language=target_language, format_='text')

    # [END translate_translate_text]
    the_result = result['translatedText']
    
    return the_result

def translate_basic(source_file_content, target_filename, source_language, target_language, no_cache, cache_directory):

    with open(target_filename, "w") as f:
        was_empty_line = False
        was_id = False
        counter = 0
        for x in source_file_content:
            counter = counter + 1
            # ID
            if counter == 1 or was_empty_line:
                f.write(x + "\n")
                was_id = True
                was_empty_line = False
            # Timestamp:
            elif was_id:
                f.write(x + "\n")
                was_id = False
            elif len(x) == 0:
                f.write("\n")
                was_empty_line = True
            # Text
            else:
                text_translated = get_translation(x, source_language, target_language, no_cache, cache_directory)
                if not no_cache:
                    udpate_cache(x, text_translated, source_language, target_language, cache_directory)
                f.write(text_translated + "\n")

            if counter % 100 == 0:
                print ("Processed %d / %d lines" % (counter, len(source_file_content)))

# TODO: optimize I/O, i.e. do not re-open file and read/write for every translation
def udpate_cache(text, text_translated, source_language, target_language, cache_directory):
    if text:
        cache_base_filename = "%s_%s.json" % (source_language, target_language)
        cache_filename = os.path.join(cache_directory, cache_base_filename)
        the_json = None
        if os.path.exists(cache_filename):
            if os.path.isfile(cache_filename):
                with open(cache_filename) as json_data:
                    the_json = json.load(json_data)
            else:
                print("cache file is a directory: %s" % cache_filename)
                exit(1)
        if not the_json:
            the_json = {}
        the_json[text] = text_translated
        with open(cache_filename, 'w') as outfile:
            json.dump(the_json, outfile)

# TODO: optimize I/O, i.e. do not re-open file and read for every translation
def get_from_cache(text, source_language, target_language, cache_directory):
    if text:
        cache_base_filename = "%s_%s.json" % (source_language, target_language)
        cache_filename = os.path.join(cache_directory, cache_base_filename)
        the_json = None
        if os.path.exists(cache_filename):
            if os.path.isfile(cache_filename):
                with open(cache_filename) as json_data:
                    the_json = json.load(json_data)
                    if text in the_json:
                        return the_json[text]
            else:
                print("cache file is a directory: %s" % cache_filename)
                exit(1)

def get_translation(text, source_language, target_language, no_cache, cache_directory):
    if no_cache:
        return translate_text_v2(text, source_language, target_language)
    else:
        text_translated = get_from_cache(text, source_language, target_language, cache_directory)
        if not text_translated:
            text_translated = translate_text_v2(text, source_language, target_language)
            udpate_cache(text, text_translated, source_language, target_language, cache_directory)
        return text_translated



def translate_and_split(text, source_language, target_language, nb_slices, no_cache, cache_directory):
    text_translated = get_translation(text, source_language, target_language, no_cache, cache_directory)
    if not no_cache:
        udpate_cache(text, text_translated, source_language, target_language, cache_directory)
    result = []
    the_split = text_translated.split(" ")
    nb_words_per_slice = round(len(the_split) / nb_slices)
    #print("Nb words per slice %d" % nb_words_per_slice)

    while the_split:
        slice_index = min(nb_words_per_slice, len(the_split))
        s = " ".join(the_split[0:slice_index])
        the_split = the_split[slice_index:]
        # If we reached the number of desired slices, 
        # add the remaining text anyway.
        if len(result) == nb_slices - 1 and the_split:
            s = "%s %s" % (s, " ".join(the_split))
            the_split = []
        result.append(s)
        

    if len(result) != nb_slices:
        print ("Not the correct size")
        print (result)
        exit(2)
    
    return result


def translate_smart(source_file_content, target_filename, source_language, target_language, no_cache, cache_directory):

    with open(target_filename, "w") as f:

        target_buffer = []
        counter = 0
        for x in source_file_content:
            counter = counter + 1
            # ID
            if counter == 1 or was_empty_line:
                was_id = True
                was_empty_line = False
                if target_buffer:
                    t = " ".join(target_buffer)
                    #print(t)
                    #print(len(target_buffer))
                    #print(translate_and_split(t, source_language, target_language, len(target_buffer)))
                    #print("\n\n")
                    lines = translate_and_split(t, source_language, target_language, len(target_buffer), no_cache, cache_directory)
                    for l in lines:
                        f.write(l + "\n")
                    target_buffer = []
                # The new line
                if counter > 1:
                    f.write("\n")
                f.write(x + "\n")
            # Timestamp:
            elif was_id:
                f.write(x + "\n")
                was_id = False
            elif len(x) == 0:
                was_empty_line = True
            # Text
            else:
                target_buffer.append(x)

            if counter % 100 == 0:
                print ("Processed %d / %d lines" % (counter, len(source_file_content)))
        
        if target_buffer:
            t = " ".join(target_buffer)
            #print(t)
            #print(len(target_buffer))
            #print(translate_and_split(t, source_language, target_language, len(target_buffer)))
            #print("\n\n")
            lines = translate_and_split(t, source_language, target_language, len(target_buffer), no_cache, cache_directory)
            for l in lines:
                f.write(l + "\n")
            target_buffer = []



#######################################################################
# Global variables.
m_output_directory = 'output'
m_cache_directory = 'cache'

if __name__ == '__main__':
    #######################################################################
    print("SRT translator")
    print("--------------\n")

    #######################################################################
    # argparse stuff to parse input parameters.

    parser = argparse.ArgumentParser(description='Translates subtitles files (.srt) using Google Translate.')
    parser.add_argument('-f', '--file', type=str, nargs=1, help='The subtitle file to translate.')
    parser.add_argument('-o', '--output_directory', type=str, nargs='?', help='Directory where the generated CSV files are stored, default: \'%s\'.' % m_output_directory)
    parser.add_argument('-c', '--cache_directory', type=str, nargs='?', help='Directory where cache files are stored, default: \'%s\'.' % m_cache_directory)
    parser.add_argument('-sl', '--source_language', type=str, nargs=1, help='Source language (see https://cloud.google.com/translate/docs/languages for supported language codes).')
    parser.add_argument('-tl', '--target_language', type=str, nargs=1, help='Target language (see https://cloud.google.com/translate/docs/languages for supported language codes).')
    parser.add_argument('-ow', '--overwrite_target', type=str2bool, nargs='?', default=False, help='Overwrite target file if it exists already, default: no.')
    parser.add_argument('-nc', '--no_cache', type=str2bool, nargs='?', default=False, help='Do not use translation cache, default: no (i.e. uses cache by default).')
    parser.add_argument('-nj', '--no_text_join', type=str2bool, nargs='?', default=False, help='Do not join texts appearing on multiline on a given timestamp before translating, default: no (i.e. texts on a given timestamp are joined by default, which can avoid sending partial sentences to translation as they might produce lower quality translations).')


    args = parser.parse_args()

    # Check/validate parameters.
    if not args.file:
        print ('files not specified (use -h for details)')
        exit(1)
    elif len(args.file) != 1:
        print ('one single source file allowed (use -h for details)')
        exit(1)
    elif not os.path.exists(args.file[0]):
        print ('file does not exist: %s' % args.file[0])
        exit(1)
    if args.output_directory:
        m_output_directory = args.output_directory
    if not os.path.exists(m_output_directory) or not os.path.isdir(m_output_directory):
        print ('not a valid directory: %s' % m_output_directory)
        exit(1)
    
    if args.cache_directory:
        m_cache_directory = args.cache_directory
    if not os.path.exists(m_cache_directory) or not os.path.isdir(m_cache_directory):
        print ('not a valid directory: %s' % m_cache_directory)
        exit(1)

    source_filename = args.file[0]
    
    source_file_basename = (os.path.basename(source_filename))
    target_filename = os.path.join(m_output_directory, source_file_basename)

    source_language = args.source_language[0]
    target_language = args.target_language[0]

    print ("Source language: %s" % source_language)
    print ("Target language: %s" % target_language)
    print ("Source file: %s" % source_filename)
    print ("Target file: %s" % target_filename)
    print ("Overwrite target: %s" % args.overwrite_target)
    print ("No cache: %s" % args.no_cache)
    if not args.no_cache:
        print ("Cache directory: %s" % m_cache_directory)
    print ("\n")

    if os.path.exists(target_filename):
        if args.overwrite_target and os.path.isfile(target_filename):
            os.remove(target_filename)
        elif os.path.isdir(target_filename):
            print ('target file exists already and is a directory: %s' % target_filename)
            exit(1)
        else:
            print ('target file exists already: %s' % target_filename)
            exit(1)


    source_file_content = get_content(source_filename)

    if args.no_text_join:
        translate_basic(source_file_content, target_filename, source_language, target_language, args.no_cache, m_cache_directory)
    else:        
        translate_smart(source_file_content, target_filename, source_language, target_language, args.no_cache, m_cache_directory)

    print ("\n\nDONE")

    #print ("Translation: " + translate_text('this is a test', 'en', 'fr'))