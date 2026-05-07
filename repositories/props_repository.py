from interfaces.props_repository_interface import PropsRepositoryInterface
from db.models.odds_api_prop import OddsAPIProp
from sqlalchemy import func
import logging
from dateutil import parser
import datetime

logger = logging.getLogger(__name__)

class PropsRepository(PropsRepositoryInterface):
    @staticmethod
    def _parse_datetime(dt):
        """
        Convert ISO8601 string (with or without 'Z') or datetime to datetime object.
        Returns None if input is None.
        """
        import datetime
        if dt is None:
            return None
        if isinstance(dt, datetime.datetime):
            return dt
        if isinstance(dt, str):
            # Handle 'Z' for UTC
            if dt.endswith('Z'):
                dt = dt[:-1] + '+00:00'
            try:
                return datetime.datetime.fromisoformat(dt)
            except Exception:
                return parser.parse(dt)
        raise ValueError(f"Cannot parse datetime from {dt!r}")

    @staticmethod
    def _flatten_oddsapi_props(props):
        """
        Flattens a list of OddsAPIProp Pydantic objects (nested) into flat dicts for DB insertion.
        Ensures all DateTime fields are Python datetime objects.
        Args:
            props (list[OddsAPIProp]): List of OddsAPIProp Pydantic objects.
        Returns:
            list[dict]: List of flat dicts for DB model.
        """
        flat_props = []
        for prop in props:
            for bookmaker in prop.bookmakers:
                for market in bookmaker.markets:
                    for outcome in market.outcomes:
                        flat_props.append({
                            'event_id': prop.id,
                            'bookmaker': bookmaker.key,
                            'market_key': market.key,
                            'market_last_update': PropsRepository._parse_datetime(market.last_update),
                            'outcome_name': outcome.name,
                            'outcome_point': outcome.point,
                            'outcome_description': outcome.description or '',
                            'outcome_price': outcome.price,
                            'commence_time': PropsRepository._parse_datetime(prop.commence_time),
                            'sport_key': prop.sport_key,
                            'sport_title': prop.sport_title,
                            'home_team': prop.home_team,
                            'away_team': prop.away_team,
                        })
        return flat_props

    def __init__(self, db):
        self.db = db

    def save_props(self, props):
        """
        Save a list of OddsAPIProp Pydantic objects or flat dicts to the database. Uses upsert (merge) for idempotency.
        Accepts both nested (API) and flat (test) formats.
        Ensures all DateTime fields are Python datetime objects.
        Args:
            props (list): List of OddsAPIProp Pydantic objects or flat dicts to save.
        """
        flat_props = []
        for item in props:
            # If it's a dict with 'bookmakers', treat as nested OddsAPIProp dict
            if isinstance(item, dict) and 'bookmakers' in item:
                from schemas.OddsAPIResponses import OddsAPIProp as OddsAPIPropSchema
                prop_obj = OddsAPIPropSchema(**item)
                flat_props.extend(self._flatten_oddsapi_props([prop_obj]))
            # If it's a dict with 'event_id', treat as already flat
            elif isinstance(item, dict) and 'event_id' in item:
                # Parse all DateTime fields in the flat dict
                item = dict(item)  # Copy to avoid mutating input
                for dt_field in ('commence_time', 'market_last_update'):
                    if dt_field in item:
                        item[dt_field] = PropsRepository._parse_datetime(item[dt_field])
                flat_props.append(item)
            # If it's a Pydantic OddsAPIProp object
            elif hasattr(item, 'bookmakers'):
                flat_props.extend(self._flatten_oddsapi_props([item]))
            else:
                logger.error(f"Unrecognized prop format: {item}")
        for prop_data in flat_props:
            prop = OddsAPIProp(**prop_data)
            self.db.merge(prop)  # Upsert: insert or update by composite PK
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving props: {e}")
            self.db.rollback()
            raise
    def get_props_by_hours_ahead(self, hours_ahead: int):
        """
        Retrieve props from the database for a specific number of hours ahead.
        Args:
            hours_ahead (int): The number of hours ahead for which to retrieve props.
        Returns:
            list: List of props for the given number of hours ahead.
        """
        now = datetime.datetime.utcnow()
        future = now + datetime.timedelta(hours=hours_ahead)
        return self.db.query(OddsAPIProp).filter(
            OddsAPIProp.commence_time >= now,
            OddsAPIProp.commence_time <= future
        ).all()