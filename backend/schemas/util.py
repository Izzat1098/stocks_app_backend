from ..routes.reference_data import COUNTRIES, SECTORS

countries_upper = [country.upper() for country in COUNTRIES]
sectors_upper = [sector.upper() for sector in SECTORS]

def valid_country(country_name: str) -> bool:
    if country_name.upper() in countries_upper:
        return country_name
    else:
        raise ValueError(f'Country name not in the valid countries list.')

def valid_sector(sector_name: str) -> bool:
    if sector_name.upper() in sectors_upper:
        return sector_name
    else:
        raise ValueError(f'Sector name not in the valid sectors list.')


def validate_country_required(value: str) -> str:
    """Reusable country validator for required fields"""
    if not value:
        raise ValueError('Country name is required.')
    return valid_country(value).title()


def validate_country_optional(value: str) -> str:
    """Reusable country validator for optional fields"""
    if not value:
        return value
    return valid_country(value).title()


def validate_sector_optional(value: str) -> str:
    """Reusable sector validator for optional fields"""
    if not value:
        return value
    return valid_sector(value).title()