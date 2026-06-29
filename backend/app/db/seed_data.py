"""Comprehensive seed data for UNTOLD platform."""

CATEGORIES = [
    ("Legends", "legends", "Icons who defined their sport forever"),
    ("Rivalries", "rivalries", "When greatness collides on the world stage"),
    ("Stories", "stories", "Narratives that changed sports history"),
    ("Secrets", "secrets", "Hidden truths behind the headlines"),
]

SPORTS = ["Cricket", "Football", "Basketball", "Tennis", "Boxing", "Hockey", "Formula 1", "Olympics"]

VIDEO_TEMPLATES = [
    ("UNTOLD: The Revolution", "The movement that reshaped modern sport.", "stories", True, True),
    ("UNTOLD: Rise of Dhoni", "From Ranchi to World Cup glory — the captain who rewrote cricket.", "legends", True, True),
    ("UNTOLD: Messi vs Ronaldo", "A decade-long rivalry that divided the football world.", "rivalries", True, True),
    ("UNTOLD: The Last Dance", "Inside the Bulls' dynasty and Jordan's relentless pursuit.", "legends", True, True),
    ("UNTOLD: Malice at the Palace", "The infamous 2004 NBA brawl that shocked America.", "stories", True, True),
    ("UNTOLD: Crime & Penalty", "How a gambling ring nearly destroyed an NHL franchise.", "secrets", False, True),
    ("UNTOLD: Deal with the Devil", "Christy Martin — triumph and tragedy in the ring.", "legends", False, True),
    ("UNTOLD: Breaking Point", "Mardy Fish and the battle no one saw at the US Open.", "stories", False, False),
    ("UNTOLD: The Girlfriend Who Didn't Exist", "The Manti Te'o scandal that captivated a nation.", "secrets", False, True),
    ("UNTOLD: Rise and Fall of AND1", "Streetball culture, billion-dollar dreams, and collapse.", "stories", False, False),
    ("UNTOLD: Senna vs Prost", "Formula 1's deadliest rivalry at 200 mph.", "rivalries", True, False),
    ("UNTOLD: The Hand of God", "Maradona — genius, controversy, and immortality.", "legends", True, True),
    ("UNTOLD: Rumble in the Jungle", "Ali vs Foreman — the fight that shook the world.", "rivalries", True, True),
    ("UNTOLD: The Decision", "When LeBron took his talents to South Beach.", "stories", False, True),
    ("UNTOLD: India's 1983", "The upset that made a billion believers.", "legends", True, True),
    ("UNTOLD: Tiger's Comeback", "Scandal, injury, and the Masters redemption.", "legends", False, True),
    ("UNTOLD: The Fixed Match", "Cricket's darkest hour exposed.", "secrets", True, False),
    ("UNTOLD: Kobe's Mamba Mentality", "The work ethic behind 81 points.", "legends", False, True),
    ("UNTOLD: The Underdog", "Leicester City's impossible Premier League title.", "stories", True, True),
    ("UNTOLD: Battle of the Sexes", "King vs Riggs — more than just a tennis match.", "rivalries", False, False),
]

UNSPLASH = {
    "cricket": "photo-1531415074968-076ba3e9f2e4",
    "football": "photo-1574629810360-7efbbe195018",
    "basketball": "photo-1546519638-68e109498ffc",
    "tennis": "photo-1622163642999-6c563c436f62",
    "boxing": "photo-1549719386-74dfcbf7dbed",
    "hockey": "photo-1515703407324-5f753afd8be8",
    "formula": "photo-1541896836934-ffe607ad7a85",
    "olympics": "photo-1461896836934-ffe607ad7a85",
    "default": "photo-1574629810360-7efbbe195018",
}

SPORT_IMAGE_KEY = {
    "Cricket": "cricket",
    "Football": "football",
    "Basketball": "basketball",
    "Tennis": "tennis",
    "Boxing": "boxing",
    "Hockey": "hockey",
    "Formula 1": "formula",
    "Olympics": "olympics",
}

MOCK_USERS = [
    ("Alex Rivera", "alex@untold.com"),
    ("Priya Sharma", "priya@untold.com"),
    ("James Mitchell", "james@untold.com"),
    ("Sofia Martinez", "sofia@untold.com"),
    ("David Chen", "david@untold.com"),
    ("Emma Wilson", "emma@untold.com"),
    ("Marcus Johnson", "marcus@untold.com"),
    ("Aisha Patel", "aisha@untold.com"),
    ("Ryan O'Brien", "ryan@untold.com"),
    ("Nina Kowalski", "nina@untold.com"),
    ("Carlos Mendez", "carlos@untold.com"),
    ("Yuki Tanaka", "yuki@untold.com"),
    ("Olivia Brown", "olivia@untold.com"),
    ("Hassan Ali", "hassan@untold.com"),
    ("Lena Fischer", "lena@untold.com"),
    ("Tom Bradley", "tom@untold.com"),
    ("Mei Lin", "mei@untold.com"),
    ("Diego Santos", "diego@untold.com"),
    ("Rachel Green", "rachel@untold.com"),
]

SHORT_TITLES = [
    "The Dunk That Changed Everything",
    "Dhoni's Six Heard Around the World",
    "Messi's Impossible Free Kick",
    "The Knockout in 47 Seconds",
    "Greatest Comeback Ever?",
    "World Record Broken Live",
    "When Rivalries Explode",
    "Penalty Shootout Heartbreak",
    "The Handball Controversy",
    "Last-Second Buzzer Beater",
]

def slugify(title: str) -> str:
    return title.lower().replace("'", "").replace(":", "").replace(" ", "-").replace("--", "-")

def image_url(sport: str, w: int = 800) -> str:
    key = SPORT_IMAGE_KEY.get(sport, "default")
    photo = UNSPLASH.get(key, UNSPLASH["default"])
    return f"https://images.unsplash.com/{photo}?w={w}&q=80"

def build_videos() -> list[dict]:
    videos = []
    idx = 0
    for title, desc, cat, featured, trending in VIDEO_TEMPLATES:
        sport = SPORTS[idx % len(SPORTS)]
        videos.append({
            "title": title,
            "slug": slugify(title),
            "description": desc,
            "category": cat,
            "sport": sport,
            "duration": f"1h {8 + (idx % 50)}m",
            "duration_seconds": (68 + idx % 50) * 60,
            "year": 2018 + (idx % 7),
            "rating": "TV-MA",
            "image_url": image_url(sport),
            "hero_image_url": image_url(sport, 1920),
            "is_featured": featured,
            "is_trending": trending,
            "video_type": "documentary",
            "views_count": 50000 + idx * 12000,
        })
        idx += 1

    # Fill to 50 documentaries
    extra_titles = [
        "UNTOLD: The Immortal Eight", "UNTOLD: Cold War on Ice", "UNTOLD: The Bite",
        "UNTOLD: Deflategate", "UNTOLD: The Streak", "UNTOLD: Miracle on Ice",
        "UNTOLD: The Punch", "UNTOLD: Red Card", "UNTOLD: The Trade",
        "UNTOLD: Black Mamba", "UNTOLD: The Catch", "UNTOLD: Golden Point",
        "UNTOLD: The Walk-Off", "UNTOLD: Super Over", "UNTOLD: The Dive",
        "UNTOLD: Hat-trick Hero", "UNTOLD: The Comeback Kid", "UNTOLD: Final Whistle",
        "UNTOLD: The Transfer", "UNTOLD: Night of Champions", "UNTOLD: The Rookie",
        "UNTOLD: Dynasty Falls", "UNTOLD: The Protest", "UNTOLD: Golden Boot",
        "UNTOLD: The Suspension", "UNTOLD: Perfect Game", "UNTOLD: The Heist",
        "UNTOLD: Road to Glory", "UNTOLD: The Benchwarmer", "UNTOLD: Final Lap",
    ]
    cats = ["legends", "rivalries", "stories", "secrets"]
    for i, title in enumerate(extra_titles):
        if len(videos) >= 50:
            break
        sport = SPORTS[i % len(SPORTS)]
        videos.append({
            "title": title,
            "slug": slugify(title),
            "description": f"An untold chapter in {sport.lower()} history.",
            "category": cats[i % 4],
            "sport": sport,
            "duration": f"1h {10 + i % 40}m",
            "duration_seconds": (70 + i % 40) * 60,
            "year": 2015 + (i % 10),
            "rating": "TV-MA",
            "image_url": image_url(sport),
            "hero_image_url": image_url(sport, 1920),
            "is_featured": i < 2,
            "is_trending": i % 3 == 0,
            "video_type": "documentary",
            "views_count": 20000 + i * 8000,
        })

    # Shorts (not counted in 50 docs — user asked 50 videos total, include shorts in count)
    sample_reels = [
        'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
        'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
        'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
        'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4',
        'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4',
        'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerSwifties.mp4',
    ]
    for i, title in enumerate(SHORT_TITLES):
        if len(videos) >= 50:
            break
        sport = SPORTS[i % len(SPORTS)]
        videos.append({
            "title": title,
            "slug": slugify(f"short-{title}"),
            "description": f"A defining moment in {sport.lower()}.",
            "category": cats[i % 4],
            "sport": sport,
            "duration": f"{1 + i % 3}:{10 + i * 7 % 50:02d}",
            "duration_seconds": 60 + i * 25,
            "year": 2023,
            "rating": "TV-PG",
            "image_url": image_url(sport, 400),
            "hero_image_url": None,
            "video_url": sample_reels[i % len(sample_reels)],
            "is_featured": False,
            "is_trending": i % 2 == 0,
            "video_type": "short",
            "views_count": 100000 + i * 50000,
        })

    return videos[:50]
