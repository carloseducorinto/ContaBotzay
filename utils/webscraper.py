import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re

class ContabilizeiScraper:
    def __init__(self):
        self.base_url = "https://www.contabilizei.com.br"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def _fetch_page(self, url: str) -> str:
        """Fetch the content of a webpage."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return ""
    
    def _extract_text(self, html: str) -> str:
        """Extract relevant text content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _search_keywords(self, text: str, query: str) -> List[str]:
        """Search for relevant content based on keywords."""
        query_words = set(word.lower() for word in re.findall(r'\w+', query))
        sentences = re.split(r'[.!?]+', text)
        
        relevant_sentences = []
        for sentence in sentences:
            sentence_words = set(word.lower() for word in re.findall(r'\w+', sentence))
            if query_words.intersection(sentence_words):
                relevant_sentences.append(sentence.strip())
        
        return relevant_sentences
    
    def search_content(self, query: str) -> str:
        """Search the website for content relevant to the query."""
        # Fetch the main page
        main_page = self._fetch_page(self.base_url)
        main_text = self._extract_text(main_page)
        
        # Search for relevant content
        relevant_content = self._search_keywords(main_text, query)
        
        # If no relevant content found, try searching other pages
        if not relevant_content:
            # Add logic to search other relevant pages here
            pass
        
        return "\n".join(relevant_content) if relevant_content else "No relevant information found on the website." 