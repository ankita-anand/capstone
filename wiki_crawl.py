from bs4 import BeautifulSoup
from urllib.parse import urljoin
from bs4.element import Comment, Doctype, NavigableString

from tqdm import tqdm

import requests
import json

base = "https://en.wikipedia.org/"


def scrape_intro(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = remove_tags(soup)
    matches = soup.find('p')
    text = matches.text
    for sibling in matches.next_siblings:
        if type(sibling) == NavigableString:
            text += str(sibling)
        elif sibling.name != 'p':
            break
        else:
            text += sibling.get_text()
    return text.strip()


def scrape_section(url):
    response = requests.get(url)
    sec_id = (response.url.split('#')[1])

    soup = BeautifulSoup(response.text, 'html.parser')
    match = soup.find(id=sec_id).parent

    next = match.next_sibling
    while type(next) == NavigableString:
        next = next.next_sibling
    if next.name == 'div':
        main_article = 'https://en.wikipedia.org'+next.find('a')['href']
        return main_article, scrape_intro(main_article)

    soup = remove_tags(BeautifulSoup(response.text, 'html.parser'))
    matches = soup.find(id=sec_id).parent
    text = ''
    for sibling in matches.next_siblings:
        if type(sibling) == NavigableString:
            text += str(sibling)
        elif sibling.name != 'p':
            break
        else:
            text += sibling.get_text()
    return response.url, text.strip()


def remove_tags(soup):
    for comments in soup.findAll(text=lambda text: isinstance(text, Comment) or isinstance(text, Doctype)):
        comments.extract()

    matches = list()
    matches.extend(soup.find_all(text=lambda text: isinstance(text, Comment)))
    matches.extend(soup.find_all('div', class_=["toc", "printfooter", "catlinks", "reflist", "refbegin", "references", "noprint", "navigation-not-searchable"]))
    matches.append(soup.find('ol', class_="references"))
    matches.extend(soup.find_all('div', id=["footer", "p-search", "mw-navigation"]))
    matches.extend(soup.find_all('cite', class_="citation"))
    matches.extend(soup.find_all('div', role="navigation"))
    matches.extend(soup.find_all('sup', class_=["reference"]))
    matches.extend(soup.find_all('a', class_="mw-jump-link"))
    matches.extend(soup.find_all('a', href="/wiki/Wikipedia:Citation_needed"))
    matches.extend(soup.find_all('span', class_=['texhtml', 'mw-editsection']))
    matches.extend(soup.find_all('span', id=['References', 'External_links', 'Further_reading', 'See_also']))
    matches.extend(soup.find_all('script'))
    matches.extend(soup.find_all('style'))
    matches.extend(soup.find_all('math'))
    matches.extend(soup.find_all('title'))
    matches.extend(soup.find_all('abbr', title=['View this template',
                                                'Discuss this template',
                                                'Edit this template']))
    for match in matches:
        if match is not None:
            match.decompose()

    is_external_link = soup.find('span', id=['External_links'])
    if is_external_link is not None:
        matches = is_external_link.parent.find_next_siblings()
        for match in matches:
            match.decompose()

    return soup


def scrape_page(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    soup = remove_tags(soup)

    # Remove vertical navigation box with  links to related pages
    matches = soup.find_all('table', class_="vertical-navbox")
    for match in matches:
        match.decompose()
    text = " ".join(t.strip() for t in soup.find_all(text=True))
    return text


def scrape_links(url):
    links_in_page = {}

    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    soup = remove_tags(soup)

    for link in soup.find_all('a'):
        url = urljoin(base, link.get('href'))
        if url.startswith(base) is False:
            continue
        links_in_page[link.text] = url

    return links_in_page


def scrape_depth_two():
    remove_pages = ["https://en.wikipedia.org/wiki/Machine_learning",
                    "https://en.wikipedia.org/wiki/Artificial_intelligence",
                    "https://en.wikipedia.org/wiki/Linear_algebra",
                    "https://en.wikipedia.org/wiki/Probability"]

    go_links = json.loads(open('go.json', "r", encoding="utf-8").read())
    read_pages = set(remove_pages)

    depth_two_tree = {}

    for starter_page in go_links:
        print("Under: " + starter_page)
        for wiki_link in go_links[starter_page]:
            if wiki_link not in read_pages:
                print(wiki_link)
                read_pages.add(wiki_link)
                depth_two_tree[wiki_link] = scrape_links(wiki_link)

    return depth_two_tree


def scrape_depth_one():
    tree = dict()
    root_nodes = ["Machine_learning",
                  "Linear_algebra",
                  "Artificial_intelligence",
                  "Probability"]

    for root_node in root_nodes:
        url = "https://en.wikipedia.org/wiki/" + root_node
        links_in_page = scrape_links(url)
        tree[root_node] = links_in_page
    return tree


def convert_tree_url_to_concepts(pruned_concepts_json):

    pruned_tree = json.loads(open(pruned_concepts_json).read())
    URL_keys = dict()

    for page in pruned_tree.keys():
        page_name = page.split("https://en.wikipedia.org/wiki/")[1]
        for link_text in pruned_tree[page]:
            url = pruned_tree[page][link_text]
            if url.startswith(base + "#"):
                pruned_tree[page][link_text] = base + '/wiki/' + page_name + '#' + url.split('#')[1]

    concept_list = set()

    for parent_page_url in pruned_tree.keys():
        for link_text in pruned_tree[parent_page_url]:
            hash_text = None

            page_url = pruned_tree[parent_page_url][link_text]
            base_hash_link = page_url.split('#')
            base_page_URL = base_hash_link[0]

            if len(base_hash_link) > 1:
                hash_text = '#' + base_hash_link[1]

            concept_list.add(link_text.lower())
            if base_page_URL in URL_keys:
                URL_keys[base_page_URL].add(link_text.lower())
            else:
                URL_keys[base_page_URL] = set()
                URL_keys[base_page_URL].add(link_text.lower())

            URL_keys[base_page_URL].add(hash_text)

    for key in URL_keys:
        URL_keys[key] = list(URL_keys[key])

    return URL_keys


def merge_redirects_with_depth_one_links():
    pruned_depth_one_tree = json.loads(open('go.json', "r", encoding="utf-8").read()) # just the pruned links
    depth_one_tree = json.loads(open('wiki pages and concepts depth two.json', "r", encoding="utf-8").read()) # has the link text and hash text

    depth_one_url = dict()
    for page_url in depth_one_tree:
        new_page_url_key = page_url
        if page_url.startswith("https://en.wikipedia.org//wiki/"):
            new_page_url_key = page_url.replace("https://en.wikipedia.org//wiki/",
                                                "https://en.wikipedia.org/wiki/")

        if new_page_url_key in depth_one_url:
            depth_one_url[new_page_url_key].extend(depth_one_tree[page_url])
        else:
            depth_one_url[new_page_url_key] = depth_one_tree[page_url]

    pruned_depth_one_urls = set()
    for root_pages in pruned_depth_one_tree:
        pruned_depth_one_urls.update(pruned_depth_one_tree[root_pages])

    pruned_depth_one_url_with_hashes = dict()
    for page_url in pruned_depth_one_urls:
        pruned_depth_one_url_with_hashes[page_url] = depth_one_url[page_url]

    link_to_final_page = json.loads(open('go_original_to_final.json', "r", encoding="utf-8").read())
    final_link_to_link_text = dict()

    scrape_only_section = dict()
    for url in pruned_depth_one_url_with_hashes:
        final_url = link_to_final_page[url]
        if '#' in final_url:
            scrape_only_section[final_url] = pruned_depth_one_url_with_hashes[url]
        else:
            final_link_to_link_text[final_url] = pruned_depth_one_url_with_hashes[url]

    return final_link_to_link_text, scrape_only_section


def merge_redirects_with_depth_two_links(depth_two_urls_to_hash_text, original_to_redirected_links):
    link_to_final_page = json.loads(open(original_to_redirected_links, "r", encoding="utf-8").read())
    pruned_depth_two_urls = set(link_to_final_page.values())

    # Merge all the single/two backslash urls
    depth_two_tree_with_hash_text = json.loads(open(depth_two_urls_to_hash_text, "r", encoding="utf-8").read()) # has the link text and hash text
    all_depth_two_urls_with_hash_text = dict()
    for page_url in depth_two_tree_with_hash_text:
        text = depth_two_tree_with_hash_text[page_url]

        if page_url in link_to_final_page:
            page_url = link_to_final_page[page_url]
        elif page_url.startswith(base + "/wiki/") and \
                page_url.replace(base + "/wiki/", base + "wiki/") in link_to_final_page:
            page_url = link_to_final_page[page_url.replace(base + "/wiki/", base + "wiki/")]

        if page_url in all_depth_two_urls_with_hash_text:
            all_depth_two_urls_with_hash_text[page_url].update(text)
        else:
            all_depth_two_urls_with_hash_text[page_url] = set(text)

    pruned_depth_two_url_with_hashes = dict()
    for page_url in pruned_depth_two_urls:
        pruned_depth_two_url_with_hashes[page_url] = all_depth_two_urls_with_hash_text[page_url]

    final_link_to_link_text = dict()
    scrape_only_section = dict()

    for url in pruned_depth_two_url_with_hashes:
        if '#' in url:
            scrape_only_section[url] = pruned_depth_two_url_with_hashes[url]
        else:
            final_link_to_link_text[url] = pruned_depth_two_url_with_hashes[url]

    return final_link_to_link_text, scrape_only_section



if __name__ == "__main__":

    # tree = scrape_depth_one()
    # print(json.dumps(tree, indent=4))

    #URL_keys = convert_tree_url_to_concepts('depth_two_concepts.json')
    #with open('wiki pages and concepts depth two.json', 'w', encoding='utf-8') as f:
    #    json.dump(URL_keys, f, indent=4)

    # depth_two_tree = scrape_depth_two()
    # with open('depth_two_concepts.json', 'w', encoding='utf-8') as f:
    #    json.dump(depth_two_tree, f, indent=4)
 
    # Crawl for depth two page links
    # URL_keys_depth_two_tree = convert_tree_url_to_concepts('depth_two_concepts.json')
    # with open('url_keys_depth_two_concepts.json', 'w', encoding='utf-8') as f:
    #    json.dump(URL_keys_depth_two_tree, f, indent=4)

    final_link_to_link_text, scrape_only_section = merge_redirects_with_depth_two_links('wiki pages and concepts depth two.json',
                                                                                        'go_original_to_final_depth_two.json')

    for page_link, text_and_sections in final_link_to_link_text.items():
        # If there was only a link to a particular section on this page, scrape only this section
        if None not in text_and_sections:
            pass
        else:
            # Scrape the page
            pass

            # Remove the None element
            text_and_sections.remove(None)

            # Go through the rest for the #text
            for s in text_and_sections:
                if s.startswith('#'):
                    # Scrape this section on the page
                    # Check whether it changed only the section and not a main page
                    pass





