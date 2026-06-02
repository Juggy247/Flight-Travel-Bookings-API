from database import SessionLocal
from models.user import User
from models.airport import Airport
from models.booking import Booking
from models.payment import Payment
from models.flight import Flight
airports = [
    # Asia
    {"code": "KUL", "name": "Kuala Lumpur International Airport", "city": "Kuala Lumpur", "country": "Malaysia", "timezone": "Asia/Kuala_Lumpur"},
    {"code": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore", "timezone": "Asia/Singapore"},
    {"code": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand", "timezone": "Asia/Bangkok"},
    {"code": "NRT", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan", "timezone": "Asia/Tokyo"},
    {"code": "HND", "name": "Haneda Airport", "city": "Tokyo", "country": "Japan", "timezone": "Asia/Tokyo"},
    {"code": "ICN", "name": "Incheon International Airport", "city": "Seoul", "country": "South Korea", "timezone": "Asia/Seoul"},
    {"code": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong", "timezone": "Asia/Hong_Kong"},
    {"code": "CGK", "name": "Soekarno-Hatta International Airport", "city": "Jakarta", "country": "Indonesia", "timezone": "Asia/Jakarta"},
    {"code": "MNL", "name": "Ninoy Aquino International Airport", "city": "Manila", "country": "Philippines", "timezone": "Asia/Manila"},
    {"code": "DPS", "name": "Ngurah Rai International Airport", "city": "Bali", "country": "Indonesia", "timezone": "Asia/Makassar"},
    {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "Delhi", "country": "India", "timezone": "Asia/Kolkata"},

    # Europe
    {"code": "WAW", "name": "Warsaw Chopin Airport", "city": "Warsaw", "country": "Poland", "timezone": "Europe/Warsaw"},
    {"code": "KRK", "name": "John Paul II International Airport", "city": "Krakow", "country": "Poland", "timezone": "Europe/Warsaw"},
    {"code": "LHR", "name": "Heathrow Airport", "city": "London", "country": "United Kingdom", "timezone": "Europe/London"},
    {"code": "LGW", "name": "Gatwick Airport", "city": "London", "country": "United Kingdom", "timezone": "Europe/London"},
    {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France", "timezone": "Europe/Paris"},
    {"code": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands", "timezone": "Europe/Amsterdam"},
    {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany", "timezone": "Europe/Berlin"},
    {"code": "MUC", "name": "Munich Airport", "city": "Munich", "country": "Germany", "timezone": "Europe/Berlin"},
    {"code": "MAD", "name": "Adolfo Suarez Madrid Barajas Airport", "city": "Madrid", "country": "Spain", "timezone": "Europe/Madrid"},
    {"code": "BCN", "name": "Barcelona El Prat Airport", "city": "Barcelona", "country": "Spain", "timezone": "Europe/Madrid"},
    {"code": "FCO", "name": "Leonardo da Vinci International Airport", "city": "Rome", "country": "Italy", "timezone": "Europe/Rome"},
    {"code": "MXP", "name": "Milan Malpensa Airport", "city": "Milan", "country": "Italy", "timezone": "Europe/Rome"},
    {"code": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland", "timezone": "Europe/Zurich"},
    {"code": "VIE", "name": "Vienna International Airport", "city": "Vienna", "country": "Austria", "timezone": "Europe/Vienna"},
    {"code": "PRG", "name": "Vaclav Havel Airport Prague", "city": "Prague", "country": "Czech Republic", "timezone": "Europe/Prague"},
    {"code": "BUD", "name": "Budapest Ferenc Liszt International Airport", "city": "Budapest", "country": "Hungary", "timezone": "Europe/Budapest"},

    # Middle East
    {"code": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "UAE", "timezone": "Asia/Dubai"},
    {"code": "AUH", "name": "Abu Dhabi International Airport", "city": "Abu Dhabi", "country": "UAE", "timezone": "Asia/Dubai"},
    {"code": "DOH", "name": "Hamad International Airport", "city": "Doha", "country": "Qatar", "timezone": "Asia/Qatar"},

    # Americas
    {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "USA", "timezone": "America/New_York"},
    {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA", "timezone": "America/Los_Angeles"},
    {"code": "ORD", "name": "O'Hare International Airport", "city": "Chicago", "country": "USA", "timezone": "America/Chicago"},
    {"code": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada", "timezone": "America/Toronto"},
    {"code": "GRU", "name": "Guarulhos International Airport", "city": "Sao Paulo", "country": "Brazil", "timezone": "America/Sao_Paulo"},

    # Australia & Pacific
    {"code": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia", "timezone": "Australia/Sydney"},
    {"code": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia", "timezone": "Australia/Melbourne"},
    {"code": "AKL", "name": "Auckland Airport", "city": "Auckland", "country": "New Zealand", "timezone": "Pacific/Auckland"},

    # Africa
    {"code": "JNB", "name": "O.R. Tambo International Airport", "city": "Johannesburg", "country": "South Africa", "timezone": "Africa/Johannesburg"},
    {"code": "CAI", "name": "Cairo International Airport", "city": "Cairo", "country": "Egypt", "timezone": "Africa/Cairo"},
]

def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Airport).first()
        if existing:
            print("⚠️  Airports already seeded — skipping.")
            return

        for airport in airports:
            db.add(Airport(**airport))

        db.commit()
        print(f"✅ Seeded {len(airports)} airports successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()