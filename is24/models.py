from bs4 import BeautifulSoup
from datetime import datetime
import re


class AutoRepr(object):
    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))


class Expose(AutoRepr):
    def __init__(self, id, html_doc):
        soup = BeautifulSoup(html_doc, 'html.parser')
        self.id = id
        self.total_rent = Expose.__extract_total_rent(soup)
        self.living_space = Expose.__extract_living_space(soup)
        self.rooms = Expose.__extract_rooms(soup)
        self.age = Expose.__extract_age(id, soup)
        self.floor = Expose.__extract_floor(id, soup)
        self.has_balcony = Expose.__extract_has_balcony(soup)
        self.has_kitchen = Expose.__extract_has_kitchen(soup)
        self.has_cellar = Expose.__extract_has_cellar(soup)
        self.has_elevator = Expose.__extract_has_elevator(soup)
        self.needs_wbs = Expose.__extract_needs_wbs(soup)

    def __extract_total_rent(soup):
        tr_text = soup.find('dd', {'class': 'is24qa-gesamtmiete'}).text
        total_rent = float(
            re.sub('[^0-9,.]', '', tr_text)
            .replace('.', '')
            .replace(',', '.')
            .rstrip('.')
        )
        return total_rent

    def __extract_living_space(soup):
        ls_text = soup.find('dd', {'class': 'is24qa-wohnflaeche-ca'}).text
        living_space = float(ls_text
                             .replace(',', '.')
                             .replace('m²', '')
                             .strip())
        return living_space

    def __extract_rooms(soup):
        rooms_text = soup.find('dd', {'class': 'is24qa-zimmer'}).text
        rooms = float(rooms_text.replace(',', '.').strip())
        return rooms

    def __extract_age(id, soup):
        try:
            baujahr_text = soup.find('dd', {'class': 'is24qa-baujahr'}).text
            baujahr = int(baujahr_text.strip())
            current_year = datetime.now().year
            age = current_year - baujahr
            return age
        except AttributeError:
            print(f'Expose {id} has no age data')
            return None

    def __extract_floor(id, soup):
        try:
            floor_text = soup.find(
                'dd', {'class': 'is24qa-etage'}).text.strip()
            floor_num = re.sub('[^0-9,.]', ',', floor_text + ',').split(',')[0]
            floor = int(floor_num)
            return floor
        except AttributeError:
            print(f'Expose {id} has no floor data')
            return None

    def __extract_has_attr(class_name, soup):
        tag = soup.find('span', {'class': class_name})
        return tag is not None

    def __extract_has_balcony(soup):
        return Expose.__extract_has_attr('is24qa-balkon-terrasse-label', soup)

    def __extract_has_kitchen(soup):
        return Expose.__extract_has_attr('is24qa-einbaukueche-label', soup)

    def __extract_has_cellar(soup):
        return Expose.__extract_has_attr('is24qa-keller-label', soup)

    def __extract_has_elevator(soup):
        return Expose.__extract_has_attr('is24qa-personenaufzug-label', soup)

    def __extract_needs_wbs(soup):
        return Expose.__extract_has_attr(
            'is24qa-wohnberechtigungsschein-erforderlich-label',
            soup
        )
