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
        self.total_rent = Expose.__extract_total_rent(id, soup)
        self.living_space = Expose.__extract_living_space(id, soup)
        self.rooms = Expose.__extract_rooms(id, soup)
        self.age = Expose.__extract_age(id, soup)
        self.floor = Expose.__extract_floor(id, soup)
        (self.zipcode, self.city, self.district) = Expose.__extract_address(id, soup)
        self.has_balcony = Expose.__extract_has_balcony(soup)
        self.has_kitchen = Expose.__extract_has_kitchen(soup)
        self.has_cellar = Expose.__extract_has_cellar(soup)
        self.has_elevator = Expose.__extract_has_elevator(soup)
        self.needs_wbs = Expose.__extract_needs_wbs(soup)

    def __extract_total_rent(id, soup):
        try:
            tr_text = soup.find('dd', {'class': 'is24qa-gesamtmiete'}).text
            total_rent = float(
                re.sub('[^0-9,.]', '', tr_text)
                .replace('.', '')
                .replace(',', '.')
                .rstrip('.')
            )
            return total_rent
        except:
            print(f'Expose {id} has no total rent')
            return None

    def __extract_living_space(id, soup):
        try:
            ls_text = soup.find('dd', {'class': 'is24qa-wohnflaeche-ca'}).text
            living_space = float(ls_text
                                 .replace('.', '')
                                 .replace(',', '.')
                                 .replace('m²', '')
                                 .strip())
            return living_space
        except:
            print(f'Expose {id} has no living space data')
            return None

    def __extract_rooms(id, soup):
        try:
            rooms_text = soup.find('dd', {'class': 'is24qa-zimmer'}).text
            rooms = float(rooms_text.replace(',', '.').strip())
            return rooms
        except:
            print(f'Expose {id} has no room data')
            return None

    def __extract_age(id, soup):
        try:
            baujahr_text = soup.find('dd', {'class': 'is24qa-baujahr'}).text
            baujahr = int(baujahr_text.strip())
            current_year = datetime.now().year
            age = current_year - baujahr
            return age
        except:
            print(f'Expose {id} has no age data')
            return None

    def __extract_floor(id, soup):
        try:
            floor_text = soup.find(
                'dd', {'class': 'is24qa-etage'}).text.strip()
            floor_num = re.sub('[^0-9,.]', ',', floor_text + ',').split(',')[0]
            floor = int(floor_num)
            return floor
        except:
            print(f'Expose {id} has no floor data')
            return None

    def __extract_address(id, soup):
        try:
            address_text = soup.find(
                'span', {'class': 'zip-region-and-country'}).text.strip()
            address_match = re.search(
                '(.+?(?=\s))\ (.+?(?=,|$|\ )),*\ *(.*)', address_text)
            try:
                zipcode = address_match.group(1).strip()
            except:
                print(f'Could not find zipcode for expose {id}')
                zipcode = None
            try:
                city = address_match.group(2).strip()
            except:
                print(f'Could not find city for expose {id}')
                city = None
            try:
                district_str = address_match.group(3).strip()
                district = district_str if district_str != '' else None
            except:
                print(f'Could not find district for expose {id}')
                district = None
            return (zipcode, city, district)
        except:
            print(f'Expose {id} has no address data')
            return (None, None, None)

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
