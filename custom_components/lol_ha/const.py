from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "lol_ha"
PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.EVENT]

CONF_GAME_NAME = "game_name"
CONF_TAG_LINE = "tag_line"
CONF_PLATFORM_REGION = "platform_region"
CONF_API_KEY = "api_key"
CONF_PUUID = "puuid"
CONF_IDLE_INTERVAL = "idle_interval"
CONF_QUEUE_FILTER = "queue_filter"

DEFAULT_IDLE_INTERVAL = timedelta(seconds=300)
MIN_IDLE_INTERVAL = timedelta(seconds=60)
ACTIVE_INTERVAL = timedelta(seconds=60)

QUEUE_FILTER_ALL = "all"
QUEUE_FILTER_RANKED_SOLO = "ranked_solo"
QUEUE_FILTER_RANKED_FLEX = "ranked_flex"
QUEUE_FILTER_ARAM = "aram"
QUEUE_FILTER_UNRANKED = "unranked"
QUEUE_FILTERS = [
    QUEUE_FILTER_ALL,
    QUEUE_FILTER_RANKED_SOLO,
    QUEUE_FILTER_RANKED_FLEX,
    QUEUE_FILTER_ARAM,
    QUEUE_FILTER_UNRANKED,
]
DEFAULT_QUEUE_FILTER = QUEUE_FILTER_RANKED_SOLO

# MATCH-V5's `queue` param takes exactly one queue id, so a filter that
# spans multiple real queues can't be expressed server-side in one call.
# ponytail: "unranked" is represented by Normal Draft (400) only — Blind
# Pick/Quickplay games won't be counted. Add client-side multi-id filtering
# (fetch unfiltered, discard non-matches) if that gap matters.
QUEUE_FILTER_MATCH_ID = {
    QUEUE_FILTER_ALL: None,
    QUEUE_FILTER_RANKED_SOLO: 420,
    QUEUE_FILTER_RANKED_FLEX: 440,
    QUEUE_FILTER_ARAM: 450,
    QUEUE_FILTER_UNRANKED: 400,
}

# LEAGUE-V4 only has entries for the two ranked queues — None means no
# rank/promotion tracking applies for this filter, and the rank/LP sensors
# stay unavailable.
QUEUE_FILTER_LEAGUE_TYPE = {
    QUEUE_FILTER_ALL: None,
    QUEUE_FILTER_RANKED_SOLO: "RANKED_SOLO_5x5",
    QUEUE_FILTER_RANKED_FLEX: "RANKED_FLEX_SR",
    QUEUE_FILTER_ARAM: None,
    QUEUE_FILTER_UNRANKED: None,
}

# Riot occasionally reassigns platforms between regional routing clusters
# (e.g. OC1 moved from AMERICAS to SEA in 2023) — verify against
# https://developer.riotgames.com/docs/lol#routing-values before changing.
PLATFORM_TO_REGION = {
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "kr": "asia",
    "jp1": "asia",
    "eun1": "europe",
    "euw1": "europe",
    "tr1": "europe",
    "ru": "europe",
    "oc1": "sea",
    "ph2": "sea",
    "sg2": "sea",
    "th2": "sea",
    "tw2": "sea",
    "vn2": "sea",
}
