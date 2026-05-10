from db.models.PlayerStatsProcessing import PlayerStatsProcessing

class PlayerStatsProcessingRepository:
    def __init__(self, db):
        self.db = db

    def is_processed(self, player_id: int, game_id: int, season: int, sport_key: str) -> bool:
        return self.db.query(PlayerStatsProcessing).filter_by(
            player_id=player_id,
            game_id=game_id,
            season=season,
            sport_key=sport_key
        ).first() is not None

    def mark_processed(self, player_id: int, game_id: int, season: int, sport_key: str):
        record = PlayerStatsProcessing(
            player_id=player_id,
            game_id=game_id,
            season=season,
            sport_key=sport_key
        )
        self.db.add(record)
        self.db.commit()