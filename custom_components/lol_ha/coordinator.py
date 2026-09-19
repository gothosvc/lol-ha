from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RiotApiClient, RiotApiError
from .const import ACTIVE_INTERVAL, DOMAIN, QUEUE_FILTER_LEAGUE_TYPE, QUEUE_FILTER_MATCH_ID
from .helpers import apply_streak, compare_rank

_LOGGER = logging.getLogger(__name__)

COLD_START_MATCH_LOOKBACK = 20
GAMES_PLAYED_STORE_VERSION = 1


class LolDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        client: RiotApiClient,
        puuid: str,
        idle_interval: timedelta,
        queue_filter: str,
        entry_id: str,
    ) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=idle_interval)
        self.client = client
        self.puuid = puuid
        self._idle_interval = idle_interval
        self._match_queue_id = QUEUE_FILTER_MATCH_ID[queue_filter]
        self._league_queue_type = QUEUE_FILTER_LEAGUE_TYPE[queue_filter]
        self._games_played_store = Store(hass, GAMES_PLAYED_STORE_VERSION, f"{DOMAIN}_{entry_id}_games_played")
        self._was_in_game = False
        self._win_streak = 0
        self._games_played = 0
        self._last_processed_match_id: str | None = None
        self._last_rank: tuple[str, str | None] | None = None
        self._cold_started = False

    async def _async_update_data(self) -> dict:
        try:
            active_game = await self.client.get_active_game(self.puuid)
        except RiotApiError as err:
            raise UpdateFailed(str(err)) from err

        in_game = active_game is not None
        self.update_interval = ACTIVE_INTERVAL if in_game else self._idle_interval

        data = dict(self.data or {"rank": None, "last_match": None})
        data["in_game"] = in_game
        data["rank_change"] = None

        try:
            if not self._cold_started:
                await self._cold_start(data)
                self._cold_started = True
            elif self._was_in_game and not in_game:
                await self._refresh_post_game(data)
        except RiotApiError as err:
            raise UpdateFailed(str(err)) from err

        self._was_in_game = in_game
        data["win_streak"] = self._win_streak
        data["games_played"] = self._games_played
        return data

    async def _refresh_rank(self, data: dict) -> dict | None:
        if self._league_queue_type is None:
            return None
        entry = _find_league_entry(await self.client.get_league_entries(self.puuid), self._league_queue_type)
        if entry:
            data["rank"] = entry
        return entry

    async def _cold_start(self, data: dict) -> None:
        entry = await self._refresh_rank(data)
        if entry:
            self._last_rank = (entry["tier"], entry.get("rank"))

        match_ids = (
            await self.client.get_match_ids(self.puuid, count=COLD_START_MATCH_LOOKBACK, queue=self._match_queue_id)
            or []
        )

        stored = await self._games_played_store.async_load()
        if stored is not None:
            self._games_played = stored["games_played"]
        else:
            self._games_played = len(match_ids)
            await self._games_played_store.async_save({"games_played": self._games_played})

        streak = 0
        first_result: bool | None = None
        for match_id in match_ids:
            match = await self.client.get_match(match_id)
            if match is None:
                break
            won = _participant_won(match, self.puuid)
            if first_result is None:
                first_result = won
                streak = 1 if won else -1
                data["last_match"] = _summarize_match(match, self.puuid)
                self._last_processed_match_id = match_id
            elif won == first_result:
                streak += 1 if won else -1
            else:
                break
        self._win_streak = streak

    async def _refresh_post_game(self, data: dict) -> None:
        entry = await self._refresh_rank(data)
        if entry:
            new_rank = (entry["tier"], entry.get("rank"))
            if self._last_rank is not None:
                direction = compare_rank(self._last_rank, new_rank)
                if direction:
                    data["rank_change"] = {
                        "direction": direction,
                        "old_tier": self._last_rank[0],
                        "new_tier": new_rank[0],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
            self._last_rank = new_rank

        match_ids = await self.client.get_match_ids(self.puuid, count=1, queue=self._match_queue_id) or []
        if match_ids and match_ids[0] != self._last_processed_match_id:
            match = await self.client.get_match(match_ids[0])
            if match is not None:
                won = _participant_won(match, self.puuid)
                self._win_streak = apply_streak(self._win_streak, won)
                self._games_played += 1
                await self._games_played_store.async_save({"games_played": self._games_played})
                data["last_match"] = _summarize_match(match, self.puuid)
                self._last_processed_match_id = match_ids[0]


def _find_league_entry(entries: list | None, queue_type: str) -> dict | None:
    if not entries:
        return None
    return next((e for e in entries if e.get("queueType") == queue_type), None)


def _participant_won(match: dict, puuid: str) -> bool:
    participant = next(p for p in match["info"]["participants"] if p["puuid"] == puuid)
    return participant["win"]


def _summarize_match(match: dict, puuid: str) -> dict:
    participant = next(p for p in match["info"]["participants"] if p["puuid"] == puuid)
    return {
        "win": participant["win"],
        "champion": participant["championName"],
        "kills": participant["kills"],
        "deaths": participant["deaths"],
        "assists": participant["assists"],
        "queue_id": match["info"]["queueId"],
    }
