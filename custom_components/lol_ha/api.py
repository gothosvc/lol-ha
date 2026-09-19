from __future__ import annotations

from urllib.parse import quote

from aiohttp import ClientSession

from .const import PLATFORM_TO_REGION


class RiotApiError(Exception):
    """Raised on a non-2xx, non-404 response from the Riot API."""


class RiotApiAuthError(RiotApiError):
    """Raised when the API key is missing/invalid (401/403)."""


class RiotApiClient:
    def __init__(self, session: ClientSession, api_key: str, platform: str) -> None:
        self._session = session
        self._api_key = api_key
        self.platform = platform
        self.region = PLATFORM_TO_REGION[platform]

    async def _get(self, host: str, path: str, params: dict | None = None) -> dict | None:
        url = f"https://{host}.api.riotgames.com{path}"
        headers = {"X-Riot-Token": self._api_key}
        async with self._session.get(url, headers=headers, params=params) as resp:
            if resp.status == 404:
                return None
            if resp.status in (401, 403):
                raise RiotApiAuthError(f"Riot API {resp.status} for {path}")
            if resp.status != 200:
                raise RiotApiError(f"Riot API {resp.status} for {path}")
            return await resp.json()

    async def get_account_by_riot_id(self, game_name: str, tag_line: str) -> dict | None:
        path = f"/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
        return await self._get(self.region, path)

    async def get_league_entries(self, puuid: str) -> list | None:
        return await self._get(self.platform, f"/lol/league/v4/entries/by-puuid/{puuid}")

    async def get_active_game(self, puuid: str) -> dict | None:
        return await self._get(self.platform, f"/lol/spectator/v5/active-games/by-summoner/{puuid}")

    async def get_match_ids(self, puuid: str, count: int = 1, queue: int | None = None) -> list | None:
        params = {"count": count}
        if queue is not None:
            params["queue"] = queue
        return await self._get(self.region, f"/lol/match/v5/matches/by-puuid/{puuid}/ids", params=params)

    async def get_match(self, match_id: str) -> dict | None:
        return await self._get(self.region, f"/lol/match/v5/matches/{match_id}")
