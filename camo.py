import binascii
import hashlib
import hmac
import re
from memoize import mproperty
from lxml import html
import six


class CamoClient(object):
    def __init__(self, server, key):
        self.server = re.sub('/+$', '', server)
        self.key = key

    def image_url(self, url):
        return self.server + Image(url, self.key).path

    def _rewrite_url(self, url):
        if url.startswith(self.server):
            return url
        elif not any(map(url.startswith, ["http://", "https://"])):
            return url
        else:
            return self.image_url(url)

    def _rewrite_image_urls(self, node):
        for img in node.xpath('.//img'):
            if img.get('src'):
                img.set('src', self._rewrite_url(img.get('src')))
        return node

    def parse_html(self, string):
        doc = html.fromstring(string.join(['<div>', '</div>']))
        doc = self._rewrite_image_urls(doc)
        return six.ensure_str(b''.join(map(html.tostring, doc)))


class Image(object):
    def __init__(self, url, key):
        self.url = url
        self.key = key

    @mproperty
    def path(self):
        return "/%s/%s" % (self.digest, self.encoded_url)

    @mproperty
    def digest(self):
        return hmac.new(six.b(self.key), six.b(self.url), hashlib.sha1).hexdigest()

    @mproperty
    def encoded_url(self):
        if six.PY2:
            return self.url.encode("hex")
        return binascii.hexlify(six.b(self.url)).decode("utf-8")
