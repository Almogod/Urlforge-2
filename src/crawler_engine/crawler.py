import asyncio

from .frontier import URLFrontier
from .parser import extract_links
from .scheduler import run_workers
from .graph import CrawlGraph

def crawl(start_url, limit=200, extra_headers=None):
    frontier = URLFrontier()
    frontier.add(start_url)
    
    # Initialize the graph
    graph = CrawlGraph()

    # Pass the graph into the scheduler/worker system
    pages = asyncio.run(
        run_workers(frontier, extract_links, graph, limit=limit, extra_headers=extra_headers)
    )

    return pages, graph
