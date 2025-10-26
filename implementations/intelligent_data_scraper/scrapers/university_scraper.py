import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from config import Config

logger = logging.getLogger(__name__)

class UniversityScraper(BaseScraper):
    """University scraper for academic profiles and course pages"""
    
    def get_source_name(self) -> str:
        return "university"
    
    def search_person(self, name: str) -> List[Dict[str, Any]]:
        """Search for university profiles"""
        candidates = []
        
        # Common university domains to search (trimmed to reduce rate limits)
        university_domains = [
            'dartmouth.edu', 'tuck.dartmouth.edu', 'mit.edu', 'harvard.edu',
            'berkeley.edu', 'princeton.edu', 'yale.edu'
        ]
        
        for domain in university_domains:
            try:
                # Prefer DuckDuckGo HTML endpoint to avoid 429s
                ddg_results = self._search_domain_duckduckgo(domain, name)
                candidates.extend(ddg_results)

                # Fallback to Bing if needed
                if not ddg_results:
                    bing_results = self._search_domain_bing(domain, name)
                    candidates.extend(bing_results)
            
            except Exception as e:
                logger.warning(f"Error searching {domain} for {name}: {e}")
                continue
        
        return candidates

    def _search_domain_duckduckgo(self, domain: str, name: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        try:
            q = f"site:{domain} {name}"
            url = f"https://duckduckgo.com/html/?q={q}"
            response = self.make_request(url)
            if not response:
                return results
            soup = BeautifulSoup(response.content, 'html.parser')
            items = soup.select('a.result__a')
            for a in items[:5]:
                title = a.get_text().strip()
                href = a.get('href', '')
                # Normalize DuckDuckGo redirect links
                if href.startswith('/l/?uddg=') or 'duckduckgo.com/l/?uddg=' in href:
                    import urllib.parse as up
                    parsed = up.urlparse(href)
                    q = up.parse_qs(parsed.query)
                    real = q.get('uddg', [''])[0]
                    if real:
                        href = up.unquote(real)
                snippet = ''
                snip_el = a.find_parent('div', class_='result__body')
                if snip_el:
                    snip_text = snip_el.get_text(separator=' ', strip=True)
                    snippet = snip_text[:240]
                candidate = {
                    'title': title,
                    'url': href,
                    'snippet': snippet,
                    'university': domain,
                    'confidence_score': self._calculate_confidence(name, title, snippet)
                }
                results.append(candidate)
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed for {domain}: {e}")
        return results

    def _search_domain_bing(self, domain: str, name: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        try:
            q = f"site:{domain} {name}"
            url = f"https://www.bing.com/search?q={q}"
            response = self.make_request(url)
            if not response:
                return results
            soup = BeautifulSoup(response.content, 'html.parser')
            for li in soup.select('li.b_algo')[:5]:
                a = li.find('a')
                if not a:
                    continue
                title = a.get_text().strip()
                href = a.get('href', '')
                # Ensure absolute scheme
                if href.startswith('//'):
                    href = 'https:' + href
                snippet_el = li.find('p')
                snippet = snippet_el.get_text(strip=True) if snippet_el else ''
                candidate = {
                    'title': title,
                    'url': href,
                    'snippet': snippet,
                    'university': domain,
                    'confidence_score': self._calculate_confidence(name, title, snippet)
                }
                results.append(candidate)
        except Exception as e:
            logger.warning(f"Bing search failed for {domain}: {e}")
        return results
    
    def _calculate_confidence(self, search_name: str, title: str, snippet: str) -> float:
        """Calculate confidence score for university profile"""
        confidence = 0.0
        search_name_lower = search_name.lower()
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        
        # Name in title
        if search_name_lower in title_lower:
            confidence += 0.4
        
        # Name in snippet
        if search_name_lower in snippet_lower:
            confidence += 0.2
        
        # Academic keywords
        academic_keywords = ['professor', 'prof', 'faculty', 'researcher', 'lecturer', 'instructor']
        for keyword in academic_keywords:
            if keyword in title_lower or keyword in snippet_lower:
                confidence += 0.2
                break
        
        # Department keywords
        dept_keywords = ['department', 'school', 'college', 'institute', 'center']
        for keyword in dept_keywords:
            if keyword in title_lower or keyword in snippet_lower:
                confidence += 0.1
                break
        
        return min(confidence, 1.0)
    
    def scrape_person(self, person_info: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape detailed information from university profile"""
        url = person_info.get('url')
        if not url:
            logger.warning("No university profile URL provided for detailed scraping")
            return {}
        
        try:
            response = self.make_request(url)
            if not response:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            result = {
                'name': person_info.get('title', ''),
                'url': url,
                'university': person_info.get('university', ''),
                'title': '',
                'department': '',
                'email': '',
                'phone': '',
                'office': '',
                'research_interests': [],
                'education': [],
                'publications': [],
                'courses': [],
                'biography': ''
            }
            
            # Extract title/position
            title_selectors = ['h1', 'h2', '.title', '.position', '.job-title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    result['title'] = title_elem.get_text().strip()
                    break
            
            # Extract department
            dept_selectors = ['.department', '.school', '.college', '.institute']
            for selector in dept_selectors:
                dept_elem = soup.select_one(selector)
                if dept_elem:
                    result['department'] = dept_elem.get_text().strip()
                    break
            
            # Extract contact information
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, soup.get_text())
            if email_match:
                result['email'] = email_match.group()
            
            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            phone_match = re.search(phone_pattern, soup.get_text())
            if phone_match:
                result['phone'] = phone_match.group()
            
            # Extract research interests
            research_selectors = ['.research-interests', '.research', '.interests', '.expertise']
            for selector in research_selectors:
                research_elem = soup.select_one(selector)
                if research_elem:
                    interests_text = research_elem.get_text()
                    # Split by common separators
                    interests = [interest.strip() for interest in re.split(r'[,;]', interests_text)]
                    result['research_interests'] = [i for i in interests if len(i) > 3][:10]
                    break
            
            # Extract education
            education_selectors = ['.education', '.degrees', '.academic-background']
            for selector in education_selectors:
                education_elem = soup.select_one(selector)
                if education_elem:
                    education_items = education_elem.find_all(['li', 'p'])
                    for item in education_items[:5]:
                        education_text = item.get_text().strip()
                        if education_text:
                            result['education'].append(education_text)
                    break
            
            # Extract publications
            pub_selectors = ['.publications', '.papers', '.research-output']
            for selector in pub_selectors:
                pub_elem = soup.select_one(selector)
                if pub_elem:
                    pub_items = pub_elem.find_all(['li', 'p'])
                    for item in pub_items[:10]:
                        pub_text = item.get_text().strip()
                        if pub_text:
                            result['publications'].append(pub_text)
                    break
            
            # Extract courses
            course_selectors = ['.courses', '.teaching', '.classes']
            for selector in course_selectors:
                course_elem = soup.select_one(selector)
                if course_elem:
                    course_items = course_elem.find_all(['li', 'p'])
                    for item in course_items[:10]:
                        course_text = item.get_text().strip()
                        if course_text:
                            result['courses'].append(course_text)
                    break
            
            # Extract biography
            bio_selectors = ['.biography', '.bio', '.about', '.profile']
            for selector in bio_selectors:
                bio_elem = soup.select_one(selector)
                if bio_elem:
                    result['biography'] = bio_elem.get_text().strip()
                    break
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping university profile {url}: {e}")
            return {}


