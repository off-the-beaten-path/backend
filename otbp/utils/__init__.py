from geopy.distance import vincenty


def geodistance(a_lat, a_lng, b_lat, b_lng):
    return vincenty((a_lat, a_lng), (b_lat, b_lng)).meters
