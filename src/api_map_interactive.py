import requests
import folium

API_URL = "http://127.0.0.1:8000/api/editions-par-annee"
OUTPUT_HTML = "editions_bda_interactive_map.html"


def fetch_data():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    payload = response.json()
    return payload["data"]


def build_map(data):
    # centre approximatif Europe de l'Ouest / France
    m = folium.Map(location=[46.5, 2.5], zoom_start=5)

    for item in data:
        ville = item.get("ville", "")
        latitude = item.get("latitude")
        longitude = item.get("longitude")
        annees = item.get("annees_edition", "")
        pays = item.get("pays", "")

        # transforme les sauts de ligne en <br> pour le HTML
        annees_html = annees.replace("\n", "<br>")

        popup_html = f"""
        <b>Ville :</b> {ville}<br>
        <b>Pays :</b> {pays}<br>
        <b>Années des éditions :</b><br>{annees_html}
        """

        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=ville
        ).add_to(m)

    return m


def main():
    data = fetch_data()
    print(f"{len(data)} villes récupérées depuis l'API.")

    m = build_map(data)
    m.save(OUTPUT_HTML)

    print(f"Carte interactive générée : {OUTPUT_HTML}")


if __name__ == "__main__":
    main()