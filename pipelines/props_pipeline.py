from interfaces.hit_rate_event_queue_repository_interface import HitRateEventQueueRepositoryInterface
from interfaces.props_pipeline_interface import PropsPipelineInterface
from repositories.props_repository import PropsRepository
import logging
from interfaces.betting_data_api_interface import BettingDataAPIInterface
from db.models.hit_rate_event_queue import HitRateEventQueue
from interfaces.odds_api_prop_history_interface import OddsAPIPropsHistoryInterface
from db.models.odds_api_props_history import OddsAPIPropHistory
from datetime import datetime
from interfaces.teams_repository_interface import TeamsRepositoryInterface
from interfaces.players_repository_interface import PlayersRepositoryInterface


logger = logging.getLogger(__name__)

class PropsPipeline(PropsPipelineInterface):
    """
    Pipeline for fetching player props for a specific date from the balldontlie API
    and storing them in the database.
    """
    def __init__(self, db: PropsRepository, api: BettingDataAPIInterface, hit_rate_event_queue_repo: HitRateEventQueueRepositoryInterface, odds_api_prop_history_repo: OddsAPIPropsHistoryInterface, teams_repository: TeamsRepositoryInterface, players_repository: PlayersRepositoryInterface):
        self.db = db
        self.api = api
        self.hit_rate_event_queue_repo = hit_rate_event_queue_repo
        self.odds_api_prop_history_repo = odds_api_prop_history_repo
        self.teams_repository = teams_repository
        self.players_repository = players_repository

    def get_props(self, hours_ahead: int, sport: str, markets: str):
        """
        Fetch props for the given date from the Betting Data API and store them in the database.
        Args:
            hours_ahead (int): The number of hours ahead to look for events.
            sport (str): The sport key (e.g., 'basketball_nba').
            markets (str): The market key (e.g., 'player_points').
        """

        logger.info(f"Fetching events for sport: {sport} with cutoff time of {hours_ahead} hours ahead.")
        events = self.api.get_events(sport=sport, hours_ahead=hours_ahead)
        logger.info(f"Fetched {len(events)} events. Fetching props for these events.")
        props = self.api.get_props_based_on_events(sport=sport, events=events, markets=markets)

        # Filter out props where any bookmaker is not in the allowed list
        filtered_props = []
        for prop in props:
            include = set(["draftkings", "fanduel", "betmgm", "fanatics"])
            filtered_bookmakers = [bm for bm in prop.bookmakers if bm.key in include]
            if filtered_bookmakers:
                prop.bookmakers = filtered_bookmakers
                filtered_props.append(prop)
        props = filtered_props


        """
        For each prop, we want to try to match it to a player in our database. We can do this by looking at the outcome description and trying to extract a player name, then matching that player name to a player in our database who plays for one of the teams in the event. This is not perfect and may not match every prop to a player, but it should allow us to link many props to players in our database which will be important for calculating hit rates and other stats later on when we want to analyze how well our model is doing at predicting prop outcomes.
        """

        # Build team name to ID mapping once and reuse it throughout this run.
        team_name_to_id = self._build_team_name_to_id_map(sport)

        for prop in props:
            for bookmaker in prop.bookmakers:
                for market in bookmaker.markets:
                    for outcome in market.outcomes:
                        player_id = self._find_player_id_for_prop(
                            outcome.description, prop.home_team, prop.away_team, prop.sport_key,
                            self.players_repository, team_name_to_id
                        )
                        
                        if player_id is not None:
                            outcome.player_id = player_id
                        else:
                            outcome.player_id = None  # or log/flag as unmatched

        self.detect_and_produce_hit_rate_events(props, team_name_to_id)

        logger.info(f"Fetched props for {len(props)} events. Storing in database.")
        self.db.save_props(props)
        logger.info("Props stored in database successfully.")


    def detect_and_produce_hit_rate_events(self, props, team_name_to_id=None):
        """
        Detect changes in prop prices and produce hit rate events for any changes detected.
        Args:
            props (list): List of prop objects to check for price changes.
        """
        for prop in props:
            # Reuse the map from get_props when provided; fallback only for direct calls/tests.
            current_team_map = team_name_to_id
            if current_team_map is None:
                current_team_map = self._build_team_name_to_id_map(prop.sport_key)

            home_team_id, away_team_id = self._find_home_away_team_ids_for_prop(
                prop.home_team,
                prop.away_team,
                current_team_map,
            )
            for bookermakers in prop.bookmakers:
                for market in bookermakers.markets:
                    for outcome in market.outcomes:
                        existing = self.db.get_props_by_composite_key(
                            event_id=prop.id,
                            bookmaker=bookermakers.key,
                            market_key=market.key,
                            outcome_name=outcome.name,
                            outcome_description=outcome.description
                        )
                        resolved_player_id = getattr(outcome, 'player_id', None)
                        if resolved_player_id is None and existing is not None:
                            resolved_player_id = getattr(existing, 'player_id', None)
                        resolved_player_team_id = self._find_player_team_id_for_prop(
                            resolved_player_id,
                            existing.sport_key if existing else prop.sport_key
                        )
                        # If there is an existing prop and the outcome point has changed, produce a hit rate event
                        if existing:
                            point_changed = existing.outcome_point != outcome.point
                            price_changed = existing.outcome_price != outcome.price
                            if point_changed:
                                # We need to trigger recalculation and produce an event for the hit rate queue
                                # We need to also store the old and new point and price in the odds_api_props_history table for historical tracking
                                event = HitRateEventQueue(
                                    event_id=existing.event_id,
                                    bookmaker=existing.bookmaker.lower(),
                                    market_key=existing.market_key.lower(),
                                    outcome_name=existing.outcome_name.lower(),
                                    outcome_point=outcome.point,
                                    outcome_description=existing.outcome_description.lower(),
                                    commence_time=existing.commence_time,
                                    sport_key=existing.sport_key.lower(),
                                    home_team=existing.home_team.lower(),
                                    away_team=existing.away_team.lower(),
                                    market_last_update=existing.market_last_update,
                                    outcome_price=outcome.price,
                                    created_at=datetime.utcnow(),
                                    status='pending',
                                    event_type='PropUpdate',
                                    player_id=resolved_player_id,
                                    player_team_id=resolved_player_team_id,
                                    home_team_id=home_team_id,
                                    away_team_id=away_team_id,
                                )
                                self.hit_rate_event_queue_repo.produce_event(event)
                                self.odds_api_prop_history_repo.insert_props_history(
                                    OddsAPIPropHistory(
                                        event_id=existing.event_id,
                                        bookmaker=existing.bookmaker.lower(),
                                        market_key=existing.market_key.lower(),
                                        outcome_name=existing.outcome_name.lower(),
                                        old_point=existing.outcome_point,
                                        new_point=outcome.point,
                                        old_price=existing.outcome_price,
                                        new_price=outcome.price,
                                        outcome_description=existing.outcome_description.lower(),
                                        change_time=datetime.fromisoformat(market.last_update.replace('Z', '+00:00')),
                                        commence_time=existing.commence_time,
                                        sport_key=existing.sport_key.lower(),
                                        home_team=existing.home_team.lower(),
                                        away_team=existing.away_team.lower(),
                                        change_type='PointChange',
                                        player_id=resolved_player_id
                                    )
                                )


                            if price_changed and not point_changed:
                                # If only the price changed, we still want to track this in the odds_api_props_history table but we may not want to trigger a hit rate event since the point didn't change
                                self.odds_api_prop_history_repo.insert_props_history(
                                    OddsAPIPropHistory(
                                        event_id=existing.event_id,
                                        bookmaker=existing.bookmaker.lower(),
                                        market_key=existing.market_key.lower(),
                                        outcome_name=existing.outcome_name.lower(),
                                        old_point=existing.outcome_point,
                                        new_point=existing.outcome_point,
                                        old_price=existing.outcome_price,
                                        new_price=outcome.price,
                                        outcome_description=existing.outcome_description.lower(),
                                        change_time=datetime.fromisoformat(market.last_update.replace('Z', '+00:00')),
                                        commence_time=existing.commence_time,
                                        sport_key=existing.sport_key.lower(),
                                        home_team=existing.home_team.lower(),
                                        away_team=existing.away_team.lower(),
                                        change_type='PriceChange',
                                        player_id=resolved_player_id
                                    )
                                )

                        if not existing:
                            # If there is no existing prop, we need to produce an event to trigger calculation for this new prop and also insert a record into the odds_api_props_history table to track the initial creation of this prop
                            event = HitRateEventQueue(
                                event_id=prop.id,
                                bookmaker=bookermakers.key.lower(),
                                market_key=market.key.lower(),
                                outcome_name=outcome.name.lower(),
                                outcome_point=outcome.point,
                                outcome_description=outcome.description.lower(),
                                commence_time=prop.commence_time,
                                sport_key=prop.sport_key.lower(),
                                home_team=prop.home_team.lower(),
                                away_team=prop.away_team.lower(),
                                market_last_update=market.last_update,
                                outcome_price=outcome.price,
                                created_at=datetime.utcnow(),
                                status='pending',
                                event_type='NewProp',
                                player_id=resolved_player_id,
                                player_team_id=resolved_player_team_id,
                                home_team_id=home_team_id,
                                away_team_id=away_team_id,
                            )

                            self.hit_rate_event_queue_repo.produce_event(event)

    def _find_player_id_for_prop(self, outcome_description, home_team, away_team, sport, players_repository, team_name_to_id):
        """
        Try to find the player_id for a given prop outcome by name and team.
        Returns player_id if found, else None.
        """
        if not outcome_description:
            return None
        # Normalize and split name
        name = outcome_description.strip().lower()
        logging.info("Name: %s", name)
        parts = name.split()
        if len(parts) < 2:
            return None
        first, last = parts[0], parts[-1]
        # Query for all players with this name in the sport
        candidates = players_repository.get_player_by_name(first, last, sport)
        logging.info("Found %d candidates for player name '%s %s'", len(candidates), first, last)
        # Map team names to IDs for comparison
        home_team_id = self._resolve_team_id(home_team, team_name_to_id)
        away_team_id = self._resolve_team_id(away_team, team_name_to_id)
        for player in candidates:
            logging.info("Checking player %s with team_id %s", player.id, player.team_id)
            if player.team_id == home_team_id or player.team_id == away_team_id:
                return player.id
        return None
    
    def _find_player_team_id_for_prop(self, player_id: int, sport_key: str):
        if player_id is None or self.players_repository is None or not sport_key:
            return None

        try:
            player = self.players_repository.get_player_by_id(player_id, sport_key)
            if player is None:
                return None
            return getattr(player, 'team_id', None)
        except Exception as exc:
            logger.error("Error resolving team_id for player_id=%s sport_key=%s: %s", player_id, sport_key, exc)
            return None

    def _build_team_name_to_id_map(self, sport_key: str):
        if self.teams_repository is None or not sport_key:
            return {}

        try:
            teams = self.teams_repository.get_teams(sport_key)
            team_name_to_id = {}
            for team in teams:
                for alias in [getattr(team, 'name', None), getattr(team, 'nickname', None)]:
                    normalized = self._normalize_team_name(alias)
                    if normalized and normalized not in team_name_to_id:
                        team_name_to_id[normalized] = team.id
            return team_name_to_id
        except Exception as exc:
            logger.error("Error building team map for sport_key=%s: %s", sport_key, exc)
            return {}

    def _find_home_away_team_ids_for_prop(self, home_team: str, away_team: str, team_name_to_id: dict):
        home_team_id = self._resolve_team_id(home_team, team_name_to_id)
        away_team_id = self._resolve_team_id(away_team, team_name_to_id)
        logger.info("Resolved home team '%s' to ID %s", home_team, home_team_id)
        logger.info("Resolved away team '%s' to ID %s", away_team, away_team_id)
        return home_team_id, away_team_id

    def _resolve_team_id(self, team_name: str, team_name_to_id: dict):
        normalized = self._normalize_team_name(team_name)
        if not normalized or not team_name_to_id:
            return None

        exact = team_name_to_id.get(normalized)
        if exact is not None:
            return exact

        # Fallback for naming differences like "Athletics" vs "Oakland Athletics".
        for key, team_id in team_name_to_id.items():
            if key.endswith(f" {normalized}") or normalized.endswith(f" {key}"):
                return team_id
        return None

    def _normalize_team_name(self, value: str):
        if not value:
            return None
        normalized = value.strip().lower().replace('.', '').replace('-', ' ')
        return ' '.join(normalized.split())



