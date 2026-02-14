#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆瓣读书封面获取器
根据书名获取豆瓣读书上最新出版版本的书籍封面（缩略图和高清图）
"""

import requests
import json
import os
import sys
from urllib.parse import quote
import time

class DoubanBookCover:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.request_count = 0  # 记录请求次数
        self.last_request_time = time.time()  # 上次请求时间
        self.base_delay = 2  # 基础延迟时间（秒）
        self.max_delay = 30  # 最大延迟时间（秒）
        self.request_interval = 3  # 请求间隔（秒）
        
    def _control_request_rate(self):
        """
        智能请求频率控制
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # 计算需要等待的时间
        wait_time = max(0, self.request_interval - time_since_last)
        
        if wait_time > 0:
            print(f"智能延迟: {wait_time:.1f}秒")
            time.sleep(wait_time)
        
        # 更新请求信息
        self.last_request_time = time.time()
        self.request_count += 1
        
        # 每10次请求增加延迟时间
        if self.request_count % 10 == 0:
            self.request_interval = min(self.request_interval * 1.5, self.max_delay)
            print(f"累计请求 {self.request_count} 次，调整请求间隔为 {self.request_interval:.1f}秒")
        
    def search_book(self, book_title):
        """
        搜索书籍信息
        """
        try:
            # 尝试多种搜索方法
            search_methods = [
                # self._search_via_douban_api,
                self._search_via_web_page,
                # self._search_via_alternative_api,
                # self._search_via_dangdang,
                # self._search_via_demo_data
            ]
            
            # 控制请求频率
            self._control_request_rate()
            
            max_retries = 3  # 最大重试次数
            retry_count = 0
            
            while retry_count < max_retries:
                for method in search_methods:
                    try:
                        result = method(book_title)
                        if result:
                            print('========================================')
                            print(result)
                            return result
                    except requests.RequestException as e:
                        status_code = getattr(e.response, 'status_code', None)
                        
                        if status_code in [429, 418, 503]:
                            # 频率限制或反爬虫错误
                            retry_count += 1
                            if retry_count >= max_retries:
                                print(f"搜索方法失败（达到最大重试次数）: {e}")
                                break
                            
                            # 指数退避策略
                            backoff_time = min(2 ** retry_count, self.max_delay)
                            print(f"遇到频率限制，{backoff_time}秒后重试 ({retry_count}/{max_retries})...")
                            time.sleep(backoff_time)
                            # 增加请求间隔
                            self.request_interval = min(self.request_interval * 2, self.max_delay)
                        else:
                            print(f"搜索方法失败: {e}")
                    except Exception as e:
                        print(f"搜索方法失败: {e}")
                else:
                    # 所有方法都尝试失败
                    break
            
            print(f"所有搜索方法都未找到书籍: {book_title}")
            return None
                
        except Exception as e:
            print(f"搜索请求失败: {e}")
            return None
    
    def _search_via_douban_api(self, book_title):
        """
        通过豆瓣API搜索，获取最新版本
        """
        try:
            # 使用豆瓣图书搜索API，获取多个结果以便选择最新版本
            search_url = f"https://api.douban.com/v2/book/search?q={quote(book_title)}&count=10"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            books = data.get('books', [])
            
            if books:
                # 按出版日期排序，获取最新版本
                latest_book = self._get_latest_version(books)
                return latest_book
            return None
            
        except Exception as e:
            print(f"豆瓣API搜索失败: {e}")
        return None
    
    def _get_latest_version(self, books):
        """
        从多个版本中选择最新出版的版本
        """
        if not books:
            return None
        
        # 按出版日期排序，获取最新版本
        def parse_date(pubdate):
            if not pubdate:
                return (0, 0, 0)  # 默认最早日期
            
            try:
                # 处理不同的日期格式
                if '-' in pubdate:
                    parts = pubdate.split('-')
                    if len(parts) >= 3:
                        return (int(parts[0]), int(parts[1]), int(parts[2]))
                    elif len(parts) == 2:
                        return (int(parts[0]), int(parts[1]), 1)
                    else:
                        return (int(parts[0]), 1, 1)
                else:
                    # 只有年份
                    return (int(pubdate), 1, 1)
            except:
                return (0, 0, 0)
        
        # 按出版日期降序排序（最新的在前）
        sorted_books = sorted(books, key=lambda x: parse_date(x.get('pubdate', '')), reverse=True)
        
        latest_book = sorted_books[0]
        print(f"找到 {len(books)} 个版本，选择最新版本: {latest_book.get('pubdate', '未知日期')}")
        
        return latest_book

    def _search_via_demo_data(self, book_title):
        """
        使用演示数据（当API不可用时）
        """
        # 为《活着》提供最新版本（2021年）的演示数据
        if "活着" in book_title:
            # 使用2021年北京十月文艺出版社版本的封面图片URL
            # 这是2021年定本版本的封面
            cover_url = 'https://img9.doubanio.com/view/subject/s/public/s33834064.jpg'
            
            demo_data = {
                'title': '活着（定本·2021新版 精装）',
                'author': ['余华'],
                'publisher': '北京十月文艺出版社',
                'pubdate': '2021-10-1',
                'images': {
                    'small': cover_url,
                    'medium': cover_url.replace('/s/', '/m/'),
                    'large': cover_url.replace('/s/', '/l/')
                }
            }
            print("使用演示数据（豆瓣API暂时不可用）- 2021年北京十月文艺出版社版本")
            return demo_data
        return None
    
    def _search_via_dangdang(self, book_title):
        """
        通过当当网搜索获取最新版本封面
        """
        try:
            import re
            from bs4 import BeautifulSoup
            
            search_url = f"https://search.dangdang.com/?key={quote(book_title)}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找书籍链接
            book_links = soup.find_all('a', {'name': 'itemlist-title'})
            if book_links:
                book_url = book_links[0].get('href')
                if book_url:
                    # 访问书籍详情页
                    book_response = self.session.get(book_url, timeout=10)
                    book_response.raise_for_status()
                    
                    book_soup = BeautifulSoup(book_response.text, 'html.parser')
                    
                    # 查找封面图片
                    img_tag = book_soup.find('img', {'id': 'largePic'})
                    if img_tag:
                        cover_url = img_tag.get('src')
                        if cover_url:
                            # 构造书籍信息
                            title_elem = book_soup.find('h1', {'id': 'product_title'})
                            title = title_elem.get_text().strip() if title_elem else book_title
                            
                            return {
                                'title': title,
                                'author': ['余华'],
                                'publisher': '作家出版社',
                                'pubdate': '2021-3-1',
                                'images': {
                                    'small': cover_url,
                                    'medium': cover_url,
                                    'large': cover_url
                                }
                            }
            
            return None
            
        except Exception as e:
            print(f"当当网搜索失败: {e}")
            return None
    
    def _search_via_web_page(self, book_title):
        """
        通过豆瓣网页搜索，打印搜索结果
        """
        try:
            search_url = f"https://www.douban.com/search?cat=1001&q={quote(book_title)}"
            print(f"正在搜索豆瓣读书: {search_url}")
            
            # 控制请求频率
            self._control_request_rate()
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # 解析搜索结果并打印
            return self._parse_and_print_search_results(response.text, book_title)
            
            book_id = self._extract_book_id_from_search(response.text)
            if book_id:
                return self._get_book_info(book_id)
            return None
            
        except Exception as e:
            print(f"网页搜索失败: {e}")
            return None
    
    def _parse_and_print_search_results(self, html_content, book_title):
        """
        解析并打印豆瓣搜索结果
        """
        try:
            from bs4 import BeautifulSoup
            import re
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            print(f"\n=== 豆瓣读书搜索结果: {book_title} ===")
            
            # 查找搜索结果
            result_items = soup.find_all('div', class_='result')
            
            if not result_items:
                # 尝试其他可能的搜索结果容器
                result_items = soup.find_all('div', class_='item-root')
            
            if not result_items:
                # 尝试查找书籍链接
                book_links = soup.find_all('a', href=re.compile(r'/subject/\d+/'))
                if book_links:
                    print(f"找到 {len(book_links)} 个相关书籍:")
                    for i, link in enumerate(book_links[:10], 1):  # 只显示前10个
                        href = link.get('href', '')
                        title = link.get_text().strip()
                        if title and href:
                            # 从链接中提取真正的书籍ID
                            book_id_match = re.search(r'/subject/(\d+)/', href)
                            if book_id_match:
                                book_id = book_id_match.group(1)
                                # print(f"{i}. 标题: {title}")
                                # print(f"   链接: {href}")
                                # print(f"   书籍ID: {book_id}")
                                # print()
                else:
                    print("未找到相关书籍")
                return
            
            print(f"找到 {len(result_items)} 个搜索结果:")
            print("result_items ====== ", result_items)
            
            for i, item in enumerate(result_items[:10], 1):  # 只显示前10个结果
                try:
                    # 提取标题
                    title_elem = item.find('a', class_='title')
                    if not title_elem:
                        title_elem = item.find('a')
                    
                    title = title_elem.get_text().strip() if title_elem else "未知标题"
                    href = title_elem.get('href', '') if title_elem else ''
                    
                    # 从链接中提取真正的书籍ID
                    book_id = "未知ID"
                    if href:
                        # 处理豆瓣的跳转链接
                        if 'link2' in href:
                            # 从URL参数中提取真正的书籍ID
                            url_match = re.search(r'url=.*?%2Fsubject%2F(\d+)%2F', href)
                            if url_match:
                                book_id = url_match.group(1)
                        else:
                            # 直接从链接中提取
                            book_id_match = re.search(r'/subject/(\d+)/', href)
                            if book_id_match:
                                book_id = book_id_match.group(1)
                    
                    # 提取其他信息
                    rating_elem = item.find('span', class_='rating_nums')
                    rating = rating_elem.get_text().strip() if rating_elem else "无评分"
                    
                    # 提取作者和出版社信息
                    info_elem = item.find('p', class_='')
                    if not info_elem:
                        info_elem = item.find('div', class_='info')
                    
                    info_text = info_elem.get_text().strip() if info_elem else ""
                    
                    # print(f"{i}. 标题: {title}")
                    # print(f"   书籍ID: {book_id}")
                    # print(f"   链接: {href}")
                    # print(f"   评分: {rating}")
                    # print(f"   信息: {info_text}")
                    
                    # 获取页面内容
                    if book_id != "未知ID":
                        print("书籍ID ====== ", book_id)
                        result = self._get_and_print_book_page(book_id, title, book_title)
                        if result:
                            print("找到匹配的书籍信息，返回结果")
                            return result
                    
                except Exception as e:
                    print(f"解析第{i}个结果时出错: {e}")
                    continue
            
            print("=" * 50)
            
        except Exception as e:
            print(f"解析搜索结果失败: {e}")
            print("原始HTML内容片段:")
            print(html_content[:1000] + "..." if len(html_content) > 1000 else html_content)
    
    def _get_and_print_book_page(self, book_id, title, search_title):
        """
        根据书籍ID获取页面内容并打印，只保留标题匹配的版本
        返回书籍信息字典，包含封面图片URL等
        """
        try:
            book_url = f"https://book.douban.com/subject/{book_id}/"
            print(f"   正在获取页面内容: {book_url}")
            
            response = self.session.get(book_url, timeout=10)
            response.raise_for_status()
            
            # 解析页面内容
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"   --- 页面内容详情 ---")
            
            # 提取书籍标题
            title_elem = soup.find('h1')
            if title_elem:
                page_title = title_elem.get_text().strip()
                print(f"   页面标题: {page_title}")
                
                # 检查标题是否匹配搜索的书籍名
                if not self._is_title_match(page_title, search_title):
                    print(f"   ⚠️  标题不匹配，跳过此版本")
                    return None
            else:
                print(f"   ⚠️  未找到页面标题，跳过此版本")
                return None
            
            # 提取作者信息
            author_info = "未知作者"
            author_elem = soup.find('a', {'name': 'author'})
            if author_elem:
                author_info = author_elem.get_text().strip()
                print(f"   作者: {author_info}")
            
            # 提取出版社信息
            publisher_info = "未知出版社"
            publisher_elem = soup.find('span', string='出版社:')
            if publisher_elem:
                publisher_elem = publisher_elem.find_next_sibling('a')
                if publisher_elem:
                    publisher_info = publisher_elem.get_text().strip()
                    print(f"   出版社: {publisher_info}")
            
            # 提取出版日期
            pubdate = "未知"
            pubdate_elem = soup.find('span', string='出版年:')
            if pubdate_elem:
                # 尝试多种方式获取出版年
                pubdate_info = pubdate_elem.find_next_sibling('text')
                if not pubdate_info:
                    pubdate_info = pubdate_elem.parent.find_next_sibling('text')
                if not pubdate_info:
                    # 查找包含出版年的文本
                    pubdate_text = pubdate_elem.parent.get_text()
                    import re
                    year_match = re.search(r'(\d{4})', pubdate_text)
                    if year_match:
                        pubdate = year_match.group(1)
                else:
                    pubdate = pubdate_info.strip()
                print(f"   出版年: {pubdate}")
            else:
                print(f"   出版年: {pubdate}")
            
            # 检查出版日期是否大于2015年
            try:
                if pubdate and pubdate != "未知":
                    # 提取年份（处理不同格式的日期）
                    import re
                    year_match = re.search(r'(\d{4})', str(pubdate))
                    if year_match:
                        year = int(year_match.group(1))
                        if year <= 2015:
                            print(f"   ⚠️ 出版年不符合要求（{year}），跳过")
                            return None
                        else:
                            print(f"   ✓ 出版年符合要求（{year}）")
                    else:
                        print(f"   ⚠️ 无法解析出版年（{pubdate}），跳过")
                        return None
                else:
                    print(f"   ⚠️ 出版年未知，跳过")
                    return None
            except Exception as e:
                print(f"   ⚠️ 解析出版年时出错（{e}），跳过")
                return None

            # 提取ISBN
            isbn_elem = soup.find('span', string='ISBN:')
            if isbn_elem:
                isbn_info = isbn_elem.find_next_sibling('text')
                if isbn_info:
                    print(f"   ISBN: {isbn_info.strip()}")
            
            # 提取评分
            rating_elem = soup.find('strong', class_='rating_num')
            if rating_elem:
                rating = rating_elem.get_text().strip()
                print(f"   评分: {rating}")
            
            # 提取评分人数
            rating_people_elem = soup.find('a', class_='rating_people')
            if rating_people_elem:
                rating_people = rating_people_elem.get_text().strip()
                print(f"   评分人数: {rating_people}")
            
            # 提取封面图片
            cover_elem = soup.find('img', {'title': title})
            if not cover_elem:
                cover_elem = soup.find('img', id='mainpic')
            if not cover_elem:
                # 尝试其他可能的封面图片选择器
                cover_elem = soup.find('img', class_='nbg')
            if not cover_elem:
                cover_elem = soup.find('div', id='mainpic').find('img') if soup.find('div', id='mainpic') else None
            
            # 初始化封面图片URL
            small_cover = ""
            medium_cover = ""
            large_cover = ""
            
            if cover_elem:
                cover_url = cover_elem.get('src', '')
                print(f"   封面图片: {cover_url}")
                
                # 获取不同尺寸的封面图片
                if cover_url:
                    # 构造不同尺寸的图片URL
                    base_url = cover_url.replace('/l/', '/').replace('/m/', '/').replace('/s/', '/')
                    small_cover = base_url.replace('/public/', '/s/public/')
                    medium_cover = base_url.replace('/public/', '/m/public/')
                    large_cover = base_url.replace('/public/', '/l/public/')
                    
                    print(f"   缩略图: {small_cover}")
                    print(f"   中等尺寸: {medium_cover}")
                    print(f"   高清图: {large_cover}")
                    
                    # 验证图片URL是否可访问
                    print(f"   验证图片可访问性:")
                    for size_name, url in [("缩略图", small_cover), ("中等尺寸", medium_cover), ("高清图", large_cover)]:
                        try:
                            response = self.session.head(url, timeout=5)
                            if response.status_code == 200:
                                print(f"     ✓ {size_name}: 可访问")
                            else:
                                print(f"     ✗ {size_name}: 状态码 {response.status_code}")
                        except Exception as e:
                            print(f"     ✗ {size_name}: 访问失败 - {e}")
            else:
                print(f"   封面图片: 未找到")
            
            # 提取内容简介
            intro_elem = soup.find('div', {'id': 'link-report'})
            if intro_elem:
                intro_text = intro_elem.get_text().strip()
                if intro_text:
                    # 只显示前200个字符
                    intro_preview = intro_text[:200] + "..." if len(intro_text) > 200 else intro_text
                    print(f"   内容简介: {intro_preview}")
            
            print(f"   --- 页面内容结束 ---")
            
            # 返回书籍信息字典
            book_info = {
                'title': page_title,
                'author': [author_info],
                'publisher': publisher_info,
                'pubdate': pubdate,
                'images': {
                    'small': small_cover,
                    'medium': medium_cover,
                    'large': large_cover
                }
            }
            
            return book_info
            
        except Exception as e:
            print(f"   获取页面内容失败: {e}")
            return None
    
    def _is_title_match(self, page_title, search_title):
        """
        检查页面标题是否与搜索的书籍名匹配
        """
        # 清理标题，移除括号内容和其他修饰词
        def clean_title(title):
            import re
            # 移除括号及其内容
            title = re.sub(r'[（(].*?[）)]', '', title)
            # 移除版本标识
            title = re.sub(r'(新版|精装|典藏|定本|2021|2020|2019|2018|2017|2016|2015|2014|2013|2012|2011|2010)', '', title)
            # 移除多余空格
            title = re.sub(r'\s+', '', title)
            return title.strip()
        
        clean_page_title = clean_title(page_title)
        clean_search_title = clean_title(search_title)
        
        # 检查是否包含主要关键词
        return clean_search_title in clean_page_title or clean_page_title in clean_search_title
    
    def _search_via_alternative_api(self, book_title):
        """
        通过备用API搜索，获取最新版本
        """
        try:
            # 尝试使用豆瓣图书的备用搜索接口，获取多个结果
            search_url = f"https://frodo.douban.com/api/v2/search/subjects?q={quote(book_title)}&type=book&count=10"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            subjects = data.get('subjects', [])
            
            if subjects:
                # 构造书籍信息格式并选择最新版本
                books = []
                for subject in subjects:
                    book_info = {
                        'title': subject.get('title', ''),
                        'author': subject.get('author', []),
                        'publisher': subject.get('publisher', ''),
                        'pubdate': subject.get('pubdate', ''),
                        'images': subject.get('pic', {})
                    }
                    books.append(book_info)
                
                # 选择最新版本
                latest_book = self._get_latest_version(books)
                return latest_book
            return None
            
        except Exception as e:
            print(f"备用API搜索失败: {e}")
            return None

    def _extract_book_id_from_search(self, html_content):
        """
        从搜索结果页面提取书籍ID
        """
        import re
        
        # 查找搜索结果中的书籍链接
        pattern = r'/subject/(\d+)/'
        matches = re.findall(pattern, html_content)
        
        if matches:
            return matches[0]  # 返回第一个匹配的书籍ID
        return None
    
    def _get_book_info(self, book_id):
        """
        获取书籍详细信息
        """
        try:
            # 使用豆瓣图书API获取详细信息
            api_url = f"https://api.douban.com/v2/book/{book_id}"
            
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            book_data = response.json()
            return book_data
            
        except requests.RequestException as e:
            print(f"获取书籍信息失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"解析书籍信息失败: {e}")
            return None
    
    def get_book_covers(self, book_title="活着"):
        """
        获取书籍封面
        """
        print(f"正在搜索书籍: {book_title}")
        
        book_info = self.search_book(book_title)
        print(book_info)    
        if not book_info:
            return None
        
        # 提取书籍信息
        title = book_info.get('title', '未知标题')
        author = ', '.join(book_info.get('author', ['未知作者']))
        publisher = book_info.get('publisher', '未知出版社')
        pubdate = book_info.get('pubdate', '未知出版日期')
        
        print(f"\n找到书籍:")
        print(f"标题: {title}")
        print(f"作者: {author}")
        print(f"出版社: {publisher}")
        print(f"出版日期: {pubdate}")
        
        # 获取封面图片
        images = book_info.get('images', {})
        
        # 处理不同API返回的图片格式
        if isinstance(images, str):
            # 如果images是字符串，构造不同尺寸的URL
            base_url = images.replace('/l/', '/').replace('/m/', '/').replace('/s/', '/')
            small_cover = base_url.replace('/public/', '/s/public/')
            medium_cover = base_url.replace('/public/', '/m/public/')
            large_cover = base_url.replace('/public/', '/l/public/')
        else:
            # 如果是字典格式
            small_cover = images.get('small', '')  # 缩略图
            large_cover = images.get('large', '')  # 高清图
            medium_cover = images.get('medium', '')  # 中等尺寸
        
        covers = {
            'title': title,
            'author': author,
            'publisher': publisher,
            'pubdate': pubdate,
            'small_cover': small_cover,
            'medium_cover': medium_cover,
            'large_cover': large_cover
        }
        
        return covers
    
    def verify_image_url(self, url):
        """
        验证图片URL是否可访问
        """
        if not url:
            return False
        
        try:
            # 使用GET请求而不是HEAD，因为有些服务器对HEAD请求有限制
            response = self.session.get(url, timeout=10, stream=True)
            return response.status_code == 200
        except:
            return False
    
    def download_cover(self, url, filename):
        """
        下载封面图片
        """
        if not url:
            print(f"无效的图片URL: {url}")
            return False
        
        # 增强请求头以应对反爬虫
        enhanced_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://book.douban.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            # 使用增强的请求头
            response = self.session.get(url, timeout=30, headers=enhanced_headers)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"封面已保存: {filename}")
                return True
            else:
                print(f"下载封面失败，状态码: {response.status_code}")
                
                # 如果是反爬虫错误，尝试备用方案
                if response.status_code == 418:
                    print("检测到反爬虫机制，尝试备用下载方法...")
                    return self._download_with_alternative_method(url, filename)
                
                return False
            
        except requests.RequestException as e:
            print(f"下载封面失败: {e}")
            return False

    def _download_with_alternative_method(self, url, filename):
        """
        备用下载方法：尝试使用不同的策略绕过反爬虫
        """
        import time
        import random
        
        # 策略1：添加延迟后重试
        print("策略1: 添加随机延迟后重试...")
        time.sleep(random.uniform(2, 5))
        
        # 使用不同的User-Agent
        alternative_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://book.douban.com/',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }
        
        try:
            response = self.session.get(url, timeout=30, headers=alternative_headers)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"备用方法成功保存: {filename}")
                return True
        except:
            pass
        
        # 策略2：尝试使用requests的原始方法
        print("策略2: 使用原始requests方法...")
        try:
            response = requests.get(url, timeout=30, headers=alternative_headers)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"原始方法成功保存: {filename}")
                return True
        except:
            pass
        
        print("所有备用方法都失败了")
        return False

    def save_covers(self, covers, book_title="活着", category=""):
        """
        保存中等尺寸的封面到分类文件夹
        """
        if not covers:
            return
        
        # 创建保存目录，只到分类层
        if category:
            save_dir = f"covers/{category}"
        else:
            save_dir = "covers"
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"\n正在下载封面到目录: {save_dir}")
        
        # 按优先级下载封面：高清图 → 中等尺寸 → 缩略图
        cover_urls = [
            ('large_cover', '高清图'),
            ('medium_cover', '中等尺寸'),
            ('small_cover', '缩略图')
        ]
        
        downloaded = False
        for cover_type, description in cover_urls:
            url = covers.get(cover_type)
            if url:
                # 使用书籍名称作为文件名
                safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title}.jpg"
                filepath = os.path.join(save_dir, filename)
                
                if self.download_cover(url, filepath):
                    print(f"✓ {description}封面下载成功: {filename}")
                    downloaded = True
                    break
                else:
                    print(f"✗ {description}封面下载失败，尝试下一个...")
            else:
                print(f"✗ 未找到{description}封面URL，尝试下一个...")
        
        if not downloaded:
            print(f"✗ 所有尺寸的封面都无法下载")
        
        # 保存书籍信息到分类文件夹
        info_file = os.path.join(save_dir, f"{book_title}_info.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(covers, f, ensure_ascii=False, indent=2)
        print(f"✓ 书籍信息已保存: {info_file}")
        
        return save_dir

def load_books_from_json(json_file="bookNames.json"):
    """
    从JSON文件加载书籍列表
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        books = []
        for category, book_list in data.items():
            for book in book_list:
                books.append({
                    'title': book,
                    'category': category
                })
        
        return books
    except FileNotFoundError:
        print(f"错误：找不到文件 {json_file}")
        return []
    except json.JSONDecodeError as e:
        print(f"错误：JSON文件格式不正确 - {e}")
        return []
    except Exception as e:
        print(f"错误：读取JSON文件失败 - {e}")
        return []

def main():
    """
    主函数
    """
    print("豆瓣读书封面获取器")
    print("=" * 50)
    
    # 从JSON文件加载书籍列表
    books = load_books_from_json()
    
    if not books:
        print("没有找到书籍列表，程序退出")
        return
    
    print(f"从JSON文件中加载了 {len(books)} 本书籍")
    print("=" * 50)
    
    # 创建获取器实例
    cover_getter = DoubanBookCover()
    
    # 初始化计数器
    success_count = 0
    failed_count = 0
    failed_books = []  # 存储失败的书籍名称和原因
    
    # 逐一处理每本书
    for i, book_info in enumerate(books, 1):
        book_title = book_info['title']
        category = book_info['category']
        
        print(f"\n[{i}/{len(books)}] 正在处理: {book_title} (分类: {category})")
        print("-" * 60)
        
        try:
            # 获取封面信息
            covers = cover_getter.get_book_covers(book_title)
            
            if covers:
                # 保存封面
                save_dir = cover_getter.save_covers(covers, book_title, category)
                print(f"✓ 成功处理: {book_title}")
                print(f"  保存位置: {save_dir}")
                success_count += 1
                
                # 显示封面URL
                print(f"  封面URL:")
                if covers.get('small_cover'):
                    print(f"    缩略图: {covers['small_cover']}")
                if covers.get('medium_cover'):
                    print(f"    中等尺寸: {covers['medium_cover']}")
                if covers.get('large_cover'):
                    print(f"    高清图: {covers['large_cover']}")
            else:
                print(f"✗ 未能获取到书籍封面信息: {book_title}")
                failed_count += 1
                failed_books.append(f"{book_title} - 未能获取到封面信息")
                
        except Exception as e:
            print(f"✗ 处理书籍时出错: {book_title} - {e}")
            failed_count += 1
            failed_books.append(f"{book_title} - 处理出错: {e}")
        
        # 添加延迟，避免请求过于频繁
        if i < len(books):
            print("等待2秒后处理下一本书...")
            time.sleep(2)
    
    # 显示最终统计
    print("\n" + "=" * 60)
    print("处理完成！")
    print(f"成功处理: {success_count} 本书")
    print(f"处理失败: {failed_count} 本书")
    print(f"总计处理: {len(books)} 本书")
    
    # 显示失败的书籍名称
    if failed_books:
        print("\n失败的书籍列表:")
        print("-" * 40)
        for failed_book in failed_books:
            print(f"• {failed_book}")
        print("-" * 40)

if __name__ == "__main__":
    main()
