
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt


def scrape_data_and_extract_content() -> list or None:
    """
    Scrapt den Content von der Webressource der DINI und löscht alle Daten vor und nach der Tabelle.
    :return:
    """
    response = requests.get("https://dini.de/dienste-projekte/publikationsdienste")

    # Wir prüfen, ob die Anfrage erfolgreich war, indem wir den Statuscode der HTTP-Anfrage prüfen.
    if not response.status_code == 200:
        raise Warning(f"Die HTTP-Anfrage war nicht erfolgreich. Statuscode: {response.status_code}")
    else:
        html_source = response.text
        database = html_source[html_source.index('</thead>'):html_source.index('</tbody>')]

        # Die Tabelleneinträge werden gespalten und in einer Liste gespeichert.
        split_entries = database.split('<td class="dini"')

        # Der letzte Eintrag wird gelöscht, da er leer ist und danach geprüft, ob die Liste genau 540 Einträge umfasst; veraltet, da sich die Menge der verzeichneten Dienste ständig ändert.
        split_entries = split_entries[:-1]
        '''if not len(split_entries) == 540:
            raise Warning("Es wurden nicht alle Einträge oder zu viele Einträge erfasst")'''
        return split_entries

def create_dict_from_content(entries: list) -> dict:
    """
    Bildet die HTML-Rohdaten auf ein Dictionary ab.
    :param entries:
    :return:
    """
    repository_data = {}

    for html_string in entries:

        soup = BeautifulSoup(html_string, 'html.parser')

        # Alle <tr>-Elemente durchgehen
        for tr_tag in soup.select('tr'):
            # Originaler Name und Link extrahieren
            original_name = tr_tag.select_one('.original_name').text.strip()

            # Weitere relevante Informationen extrahieren
            typenorm = tr_tag.select_one('.typenorm').text.strip()
            state = tr_tag.select_one('.state').text.strip()
            platform = tr_tag.select_one('.platform').text.strip()
            count = tr_tag.select_one('.count').text.strip().split('\n')[0]

            # Informationen im Dictionary speichern
            repository_data[original_name] = {
                'typenorm': typenorm,
                'state': state,
                'platform': platform,
                'count': count
            }

    return repository_data


if __name__ == '__main__':

    content = scrape_data_and_extract_content()

    print(create_dict_from_content(content))

    # Nun liegen die Daten in einer Form vor, mit der man verschiedene statistische Untersuchungen vornehmen kann.
    data = create_dict_from_content(content)

    platform_counts = {}
    for entry in data.values():
        platform = entry['platform']
        if platform:
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

    # Identifiziere Plattformen mit weniger als 2% und fasse sie in "Sonstige" zusammen
    total_entries = sum(platform_counts.values())
    threshold = 0.02 * total_entries
    other_count = 0
    other_platforms = []

    for platform, count in platform_counts.items():
        if count < threshold:
            other_count += count
            other_platforms.append(platform)

    for platform in other_platforms:
        del platform_counts[platform]

    platform_counts['Sonstige'] = other_count

    # Erstelle einen Pie-Chart um die relative Verteilung aller Forschungsdatenrepositorien zu visualieren.
    labels = platform_counts.keys()
    sizes = platform_counts.values()
    colors = plt.cm.Paired(range(len(labels)))

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)

    # Speichere oder zeige die Grafik
    '''
    plt.show()
    plt.savefig('relative distribution repos')
    '''
