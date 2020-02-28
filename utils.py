import json
from urllib.parse import unquote
from shutil import copyfile

base = "https://en.wikipedia.org/wiki/"
base_two_slash = "https://en.wikipedia.org//wiki/"


def fix_url_with_two_slashes(urls):
    for i, url in enumerate(urls):
        if url.startswith(base_two_slash):
            urls[i] = url.replace(base_two_slash, base)
    return urls


def fix_those_damn_special_characters():
    with open('pages_scraped.json',encoding='utf-8') as f:
        file = json.load(f)
        for link in file:
            file[link] = str(file[link].encode('ascii','ignore'))


def create_concept_list_from_urls(urls):
    page_names = list()
    for url in urls:
        if url.startswith(base): # filter out the "wikipedia.org/w/index.php?title=...&redirect=no" types
            page_name = unquote(url.split(base)[1].replace("_", " "))
            if '#' in page_name:
                page_names.extend(page_name.split('#'))
            else:
                page_names.append(page_name)
    return page_names


urls = fix_url_with_two_slashes(list(json.load(open('redirect.json',encoding='utf-8')).keys()))
page_names = create_concept_list_from_urls(urls)
autophrase = r"C:\Users\Ankita Anand\Desktop\autophrase\data\EN"
src = autophrase + '\wiki_quality.txt'
dst = autophrase + '\wiki_quality_plus_concepts.txt'
copyfile(src, dst)

depth_two_concept_list = open(dst, 'a')
for page in page_names:
    depth_two_concept_list.write(page + '\n')

