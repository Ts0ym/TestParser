from bs4 import BeautifulSoup, PageElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
import time
import re


class DNSProduct:

    def __init__(self,
                 dns_product_link: str,
                 price: int,
                 image_link: str,
                 rating: float,
                 service_rating: str,
                 name: str,
                 stats: [str],
                 category: str):
        self.dns_product_link = dns_product_link
        self.price = price
        self.image_link = image_link
        self.rating = rating
        self.service_rating = service_rating
        self.name = name
        self.stats = stats
        self.category = category

    def __str__(self):
        return (f"Product name: {self.name}\n"
                f"Price: {self.price}\n"
                f"DNS link: {self.dns_product_link}\n"
                f"Image link: {self.image_link}\n"
                f"Rating: {self.rating}\n"
                f"Service rating: {self.service_rating}\n"
                f"Stats: {' '.join(i for i in self.stats)}\n"
                f"Category: {self.category}\n")

    @staticmethod
    def parse_dns_product(product_string: PageElement):
        title_element = product_string.find("a", class_="catalog-product__name")
        title = title_element.text if title_element else ""
        dns_product_link = "https://www.dns-shop.ru" + title_element['href'] if title_element else ""

        price_element = product_string.find("div", class_="product-buy__price")
        price = 0
        if price_element:
            price_text = price_element.text.strip()
            price = re.sub(r'\D', '', price_text)

        image_element = product_string.find("img")
        if image_element:
            image_link = image_element.get('src') or image_element.get('data-src')
        else:
            image_link = ""

        rating_element = product_string.find("a", class_="catalog-product__rating")
        rating = rating_element['data-rating'] if rating_element else ""

        service_rating_element = product_string.find("a", class_="catalog-product__service-rating")
        service_rating = service_rating_element.text if service_rating_element else ""

        parsed_title = title.split('[')
        name = parsed_title[0] if parsed_title else ""
        stats = parsed_title[1].rstrip(']').split(', ') if len(parsed_title) > 1 else []

        return dns_product_link, price, image_link, rating, service_rating, name, stats


def parse_dns_catalog_category(category_id: str) -> None:
    base_dns_catalog_url = "https://www.dns-shop.ru/catalog/"
    url = base_dns_catalog_url + category_id
    all_products = []

    driver = Driver(uc=True, headless=True)
    driver.get(url)

    print(f"<- parsing {url} started...->")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.loaded"))
        )

        soup = BeautifulSoup(driver.page_source, features="html.parser")
        products_selector = soup.find_all("div", class_='catalog-product')
        products_category = soup.find("h1", class_="title").get_text()
        print(products_category)

        for product in products_selector:
            product_object = DNSProduct(*DNSProduct.parse_dns_product(product), products_category)
            all_products.append(product_object)
            print(product_object)

        try:
            show_more_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "pagination-widget__show-more-btn"))
            )
            show_more_button.click()
            WebDriverWait(driver, 30).until(
                EC.staleness_of(show_more_button)
            )
        except Exception as e:
            print("No more pages to load or error:", e)
            break

    driver.quit()


def main():
    dns_category_id = "17a892f816404e77/noutbuki/"
    parse_dns_catalog_category(dns_category_id)


if __name__ == "__main__":
    main()

    # Странный фикс ошибки OSError которая вылетает при закрытии браузера
    try:
        time.sleep(0.1)
    except OSError:
        pass
