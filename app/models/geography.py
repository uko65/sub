# Kigali Districts and their sectors/cells
KIGALI_DISTRICTS = {
    "Gasabo": {
        "sectors": {
            "Bumbogo": ["Bumbogo", "Gitega", "Munyiginya", "Ruhanga"],
            "Gatsata": ["Cyahafi", "Gatsata", "Karama", "Karuruma", "Rutunga"],
            "Gikomero": ["Bibare", "Bwiza", "Cyungo", "Gikomero", "Murambi"],
            "Gisozi": ["Akabuga", "Duhozanye", "Gahanga", "Gisozi", "Kinyange"],
            "Jabana": ["Gasave", "Jabana", "Nyagasambu", "Rugengabari", "Rusoro"],
            "Jali": ["Bugarama", "Cyeru", "Jali", "Musenyi", "Nyamirambo"],
            "Kacyiru": ["Kamatamu", "Kacyiru", "Kabutare", "Kiyovu", "Rugenge"],
            "Kimihurura": ["Biryogo", "Gitega", "Kimihurura", "Nyakabanda", "Rwezamenyo"],
            "Kimisagara": ["Cyahafi", "Kimisagara", "Nyabugogo", "Rugenge", "Rwampara"],
            "Kinyinya": ["Gahanga", "Kagugu", "Kinyinya", "Mulindi", "Runda"],
            "Ndera": ["Gahanga", "Kagugu", "Ndera", "Rusororo", "Shyorongi"],
            "Nduba": ["Gasogi", "Nduba", "Rusororo", "Shyorongi", "Zivu"],
            "Remera": ["Gisozi", "Remera", "Rukiri", "Rwandex", "Urugwiro"],
            "Rusororo": ["Gasogi", "Rusororo", "Shyorongi", "Zivu"],
            "Rutunga": ["Gasave", "Rugengabari", "Rutunga", "Rusoro"]
        }
    },
    "Kicukiro": {
        "sectors": {
            "Gahanga": ["Buye", "Gahanga", "Gitega", "Ruhanga", "Shyogwe"],
            "Gatenga": ["Gatenga", "Kagarama", "Kanombe", "Kinyinya"],
            "Gikondo": ["Gikondo", "Nyarugunga", "Rebero", "Rugenge"],
            "Kagarama": ["Kagarama", "Kanombe", "Kinyinya", "Niboye"],
            "Kanombe": ["Busoro", "Kagarama", "Kanombe", "Nyarugunga"],
            "Kicukiro": ["Gahanga", "Kagarama", "Kicukiro", "Niboye"],
            "Niboye": ["Gatenga", "Kagarama", "Niboye", "Nyarugunga"],
            "Nyarugunga": ["Gikondo", "Nyarugunga", "Rebero", "Rugenge"]
        }
    },
    "Nyarugenge": {
        "sectors": {
            "Gitega": ["Gitega", "Rugenge", "Rwezamenyo", "Nyakabanda"],
            "Kanyinya": ["Gasave", "Kanyinya", "Rugengabari", "Rusoro"],
            "Kigali": ["Biryogo", "Nyabugogo", "Nyamirambo", "Rugenge"],
            "Kimisagara": ["Kimisagara", "Nyabugogo", "Rugenge", "Rwampara"],
            "Mageragere": ["Kamatamu", "Mageragere", "Nyarugunga", "Rugenge"],
            "Muhima": ["Gitega", "Muhima", "Rugenge", "Rwezamenyo"],
            "Nyabugogo": ["Cyahafi", "Nyabugogo", "Rugenge", "Rwampara"],
            "Nyakabanda": ["Gitega", "Nyakabanda", "Rugenge", "Rwezamenyo"],
            "Nyamirambo": ["Biryogo", "Nyamirambo", "Rugenge", "Rwampara"],
            "Nyarugenge": ["Gitega", "Nyarugenge", "Rugenge", "Rwezamenyo"],
            "Rwezamenyo": ["Gitega", "Rugenge", "Rwezamenyo", "Nyakabanda"]
        }
    }
}

def get_kigali_districts():
    """Get list of Kigali districts"""
    return list(KIGALI_DISTRICTS.keys())

def get_sectors_by_district(district):
    """Get sectors for a specific district"""
    if district not in KIGALI_DISTRICTS:
        return []
    return list(KIGALI_DISTRICTS[district]["sectors"].keys())

def get_cells_by_sector(district, sector):
    """Get cells for a specific district and sector"""
    if district not in KIGALI_DISTRICTS:
        return []
    
    district_data = KIGALI_DISTRICTS[district]
    if sector not in district_data["sectors"]:
        return []
    
    return district_data["sectors"][sector]

def validate_location(area, location, cell=None):
    """Validate area (district), location (sector), and optional cell"""
    # Validate district
    if area not in KIGALI_DISTRICTS:
        return False, f"Invalid area. Must be one of: {get_kigali_districts()}"
    
    # Validate sector
    valid_sectors = get_sectors_by_district(area)
    if location not in valid_sectors:
        return False, f"Invalid location for {area}. Must be one of: {valid_sectors}"
    
    # Validate cell if provided
    if cell:
        valid_cells = get_cells_by_sector(area, location)
        if cell not in valid_cells:
            return False, f"Invalid cell for {area}/{location}. Must be one of: {valid_cells}"
    
    return True, "Valid location"