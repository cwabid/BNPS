from bs4 import BeautifulSoup

def get_top_heads(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        links = {
            "/".join(tag.get('href', '').split("/")[:4])
            for tag in soup.find_all('a', class_='title-link')
            if tag.get('href', '').startswith("https://en.prothomalo.com")
        }
        return list(links)
    except Exception:
        return []



def extract_titles_and_links(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        data = []
        for li in soup.find_all('li', class_='child-section'):
            a_tag = li.find('a')
            if a_tag:
                title = a_tag.text.strip()
                href = a_tag.get('href', '')
                data.append({'title': title, 'link': href})
        return data
    except Exception:
        return []
