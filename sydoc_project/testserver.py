# check_urls.py

from django.test import Client
from django.urls import get_resolver, URLPattern, URLResolver
from django.contrib.auth.models import User

client = Client()

# Optional: Login if your pages require authentication
# user = User.objects.get(username='your_username')
# client.force_login(user)

def extract_urls(urlpatterns, base=''):
    urls = []
    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            urls.append(base + pattern.pattern.regex.pattern.strip('^$'))
        elif isinstance(pattern, URLResolver):
            nested_base = base + pattern.pattern.regex.pattern.strip('^$')
            urls += extract_urls(pattern.url_patterns, nested_base)
    return urls

def check_urls():
    urls = extract_urls(get_resolver().url_patterns)
    for url in urls:
        url = '/' + url  # Ensure URL starts with /
        print(f'Checking {url} ...', end=' ')
        try:
            response = client.get(url)
            print(f'Status: {response.status_code}')
        except Exception as e:
            print(f'Error: {e}')

if __name__ == "__main__":
    check_urls()
