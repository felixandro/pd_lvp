import requests

def get_google_directions(origin, destination, mode):
    """
    origin, destination: (lat, lng) tuples
    mode: 'driving' or 'transit'
    Devuelve diccionario con tiempos (segundos) y distancias (metros).
    - Para 'driving': una sola etapa (drive).
    - Para 'transit': access, travel, egress.
    """
    if mode not in ('driving', 'transit'):
        raise ValueError("mode must be 'driving' or 'transit'")

    data = single_request(origin, destination, mode)

    status = data.get('status')
    if status != 'OK':
        return {'error': status, 'details': data.get('error_message')}

    route = data['routes'][0]
    leg = route['legs'][0]

    if mode == 'driving':

        return process_driving_leg(leg)

    elif mode == 'transit':
        return process_transit_leg(leg)

def single_request(origin, destination, mode):
    
    url = 'https://maps.googleapis.com/maps/api/directions/json'

    if mode == 'driving':
    
        params = {
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'mode': mode,
            'key': "AIzaSyAKqyYtw4VH_3LEo0_c1gSv2yfS2PsFxPQ",
            'language': 'es'
        }

    elif mode == 'transit':
        params = {
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'mode': mode,
            'transit_mode': 'bus',
            'key': "AIzaSyAKqyYtw4VH_3LEo0_c1gSv2yfS2PsFxPQ",
            'language': 'es'
        }

    resp = requests.get(url, params=params)
    data = resp.json()

    return data

def process_driving_leg(leg):
    distance = leg.get('distance', {}).get('value', 0)
    duration = leg.get('duration', {}).get('value', 0)
    return {
        'dv_liv': round(distance/1000,3), #km
        'tv_liv': round(duration/60,2), #min
    }

def process_transit_leg(leg):
    steps = leg.get('steps', [])
    transit_indices = [i for i, s in enumerate(steps) if s.get('travel_mode', '').upper() == 'TRANSIT']
    if not transit_indices:
        walk_distance = sum(s.get('distance', {}).get('value', 0) for s in steps)
        walk_duration = sum(s.get('duration', {}).get('value', 0) for s in steps)
        return {
            'dca_txb': round(0.05* walk_distance/1000,3), #km
            'tca_txb': round(0.05* walk_distance/1000,3) / 5 * 60, #min
            'dv_txb' : round(0.90* walk_distance/1000,3), #km
            'tv_txb' : round(0.90* walk_distance/1000,3) / 20 * 60, #min
            'dce_txb': round(0.05* walk_distance/1000,3), #km
            'tce_txb': round(0.05* walk_distance/1000,3) / 5 * 60} #min
     
    first_transit_idx = transit_indices[0]
    last_transit_idx = transit_indices[-1]
    access_steps = steps[:first_transit_idx]
    travel_steps = steps[first_transit_idx:last_transit_idx + 1]
    egress_steps = steps[last_transit_idx + 1:]

    access_distance = sum(s.get('distance', {}).get('value', 0) for s in access_steps)
    access_duration = sum(s.get('duration', {}).get('value', 0) for s in access_steps)
    access_travel_mode = [s.get('travel_mode', '').upper() for s in access_steps]
    travel_distance = sum(s.get('distance', {}).get('value', 0) for s in travel_steps)
    travel_duration = sum(s.get('duration', {}).get('value', 0) for s in travel_steps)
    travel_travel_mode = [s.get('travel_mode', '').upper() for s in travel_steps]
    egress_distance = sum(s.get('distance', {}).get('value', 0) for s in egress_steps)
    egress_duration = sum(s.get('duration', {}).get('value', 0) for s in egress_steps)
    egress_travel_mode = [s.get('travel_mode', '').upper() for s in egress_steps]

    print("Access travel modes:", access_travel_mode)
    print("Travel travel modes:", travel_travel_mode)
    print("Egress travel modes:", egress_travel_mode)

    assert all(mode == 'WALKING' for mode in access_travel_mode), "Access segment contains non-walking modes"
    assert all(mode == 'TRANSIT' for mode in travel_travel_mode), "Travel segment contains non-transit modes"
    assert all(mode == 'WALKING' for mode in egress_travel_mode), "Egress segment contains non-walking modes"

    return {
        'dca_txb': round(access_distance/1000,3), #km
        'tca_txb': round(access_duration/60,2), #min
        'dv_txb' : round(travel_distance/1000,3), #km
        'tv_txb' : round(travel_duration/60,2), #min
        'dce_txb': round(egress_distance/1000,3), #km
        'tce_txb': round(egress_duration/60,2)} #min

