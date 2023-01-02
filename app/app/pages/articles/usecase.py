import requests
from bs4 import BeautifulSoup
import datetime
from collections import defaultdict

class GetArticlesUseCase:
    
    def execute(self, request):
        
        # Extract the 'article' and 'top_n' values from the request
        domain = request['domain']
        top_n = int(request['top_n'])
        
        # Code for retrieving users goes here
        result = self.get_articles(domain, n=top_n)
        return {'result': result}
    
    def get_articles(self, domain, n=10):
        # ambil HTML dari situs berita Kompas (nasional, sport, atau sub domain lainnya)
        html = requests.get(domain).text

        # gunakan Beautiful Soup untuk mengekstrak informasi
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # cari element <h3> yang berisi judul artikel
        h3_elements = soup.find_all("h3")

        # ambil judul dan link dari setiap element <h3>
        for h3 in h3_elements[:n]:
            title = h3.text
            link = h3.find("a")["href"]
            articles.append({"title": title, "link": link})
        
        # simpan detail artikel
        article_details = []
        for i, article in enumerate(articles):
            article_details.append(self.detail_article(article['link']))
            
        # ambil link dan title article
        return article_details

    def detail_article(self, link):
        
        # link detail
        link = f"{link}?page=all"
        
        # ambil halaman web
        response = requests.get(link)

        # parse HTML menggunakan Beautiful Soup
        content = BeautifulSoup(response.text, "html.parser")
        
        # ambil semua elemen <p> di dalam <div class="read__content">
        paragraphs = content.find_all("p")
        
        text_paragraphs = []
        # looping setiap elemen <p>
        for p in paragraphs:
            # cetak teks di dalam elemen <p>
            text_paragraphs.append(p.text)

        # menggunakan list comprehension untuk menghapus elemen yang memuat teks "Baca juga:"
        array = [item for item in text_paragraphs if "Baca juga:" not in item and item != ""]
        
        # cari indeks elemen yang memiliki teks "#JernihBerkomentar"
        start_index = -1
        for i, elemen in enumerate(array):
            if "#JernihBerkomentar" in elemen:
                start_index = i
                break

        # hapus elemen setelahnya sampai akhir list array
        if start_index != -1:  # jika elemen ditemukan
            for i in range(start_index, len(array)):
                del array[start_index]
        
        # get artikel detail
        article = {
            "title": content.find("h1").text,
            "link": link,
            "text": array
        }

        # ambil teks artikel
        return article