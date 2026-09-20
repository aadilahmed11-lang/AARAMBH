from math import radians, sin, cos, sqrt, atan2


def distance_km(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return 9999
    r = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def rank_partners(profile, partners, availability, scheme_type="business", max_distance_km=50.0, max_npa_percent=5.0, max_overdue_percent=5.0):
    out = []
    for p in partners:
        a = availability.get(p.id)
        if not p.active or not a or not a.available or a.capacity <= 0:
            continue
        supported = {x.strip().lower() for x in (p.supported_scheme_types or "business,education").split(",")}
        if scheme_type.lower() not in supported:
            continue
        # Route only to partners that are active, available, within the requested radius,
        # and below configurable prototype risk thresholds.
        d = distance_km(profile.latitude, profile.longitude, p.latitude, p.longitude)
        if d > max_distance_km:
            continue
        if (p.npa_percent or 0) > max_npa_percent or (p.overdue_percent or 0) > max_overdue_percent:
            continue
        distance_score = max(0, 100 - min(d, 100))
        availability_score = min(100, a.capacity * 5)
        quality_score = min(100, max(0, (p.rating or 0) * 20))
        utilization_score = max(0, 100 - min(100, p.fund_utilization_percent or 0))
        score = distance_score * .35 + availability_score * .25 + quality_score * .20 + utilization_score * .20
        out.append({"partner": p, "distance_km": round(d, 2), "score": round(score, 2), "capacity": a.capacity,
                    "fund_utilization_percent": p.fund_utilization_percent, "npa_percent": p.npa_percent,
                    "rating": p.rating, "supported": True})
    return sorted(out, key=lambda x: x["score"], reverse=True)
