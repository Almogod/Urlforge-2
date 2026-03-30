from collections import deque
import redis
import json
from src.config import config

from urllib.parse import urlparse

class URLFrontier:
    def __init__(self, base_domain=None):
        self.queue = deque()
        self.visited = set()
        self.base_domain = base_domain
        if base_domain and "://" in base_domain:
            self.base_domain = urlparse(base_domain).netloc

    def add(self, url):
        if not url:
            return
        
        # Domain locking: only add if same domain
        if self.base_domain:
            parsed = urlparse(url)
            if parsed.netloc and parsed.netloc != self.base_domain:
                return

        if url not in self.visited:
            self.queue.append(url)
            self.visited.add(url) # Mark as visited immediately to avoid multiple additions

    def get(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def size(self):
        return len(self.queue)

class RedisURLFrontier:
    """Enterprise-grade frontier using Redis for distributed crawling."""
    def __init__(self, job_id: str):
        self.r = redis.from_url(config.REDIS_URL)
        self.queue_key = f"frontier:queue:{job_id}"
        self.visited_key = f"frontier:visited:{job_id}"

    def add(self, url):
        if not self.r.sismember(self.visited_key, url):
            self.r.lpush(self.queue_key, url)

    def get(self):
        url = self.r.rpop(self.queue_key)
        if url:
            url = url.decode('utf-8')
            self.r.sadd(self.visited_key, url)
            return url
        return None

    def size(self):
        return self.r.llen(self.queue_key)

    def clear(self):
        self.r.delete(self.queue_key, self.visited_key)
