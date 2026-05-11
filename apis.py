import requests as re
from bs4 import BeautifulSoup

def get_credit_rate() -> float:
    """
    Получает актуальную ставку ЦБ РФ
    :return: Ключевая ставка в десятичном формате (0.14). При ошибке возвращает значение 0.15
    """
    url = 'https://www.cbr.ru/hd_base/keyrate/'
    try:
        ask = re.get(url).text
    except Exception:
        return 0.15
    soup = BeautifulSoup(ask, 'html.parser')

    string = soup.find_all('td')[1].text
    cbr_rate = float(string.replace(',', '.')) / 100
    return cbr_rate
