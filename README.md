# League of Legends for Home Assistant

Track a League of Legends summoner in Home Assistant using the official Riot Games API 

*(Note: this means you must apply for a permanent, personal-use API key from the [Riot Development Portal](https://developer.riotgames.com/))*

## Sensors

- In-game status
- Rank and LP
- Win/loss streak
- Games played this split
- Last match result
- Promotion/demotion events

Sensors reflect current values only in this release.
There's no historical trend/graphing support yet — see Limitations for why.

## Requirements

- A Riot Games API key.
Personal development keys expire every 24 hours and require manual regeneration.
That's not practical for an always-on integration, so a production key application is recommended.
You can get one via registering a personal-use project on the
[Riot Developer Portal](https://developer.riotgames.com/)
- Each tracked summoner account requires a separate config. You can probably get away with reusing your API Key.

## Installation

### HACS (recommended)

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/gothosvc/lol-ha` as an Integration
3. Install "League of Legends" from HACS
4. Restart Home Assistant

### Manual

Copy `custom_components/lol_ha` into your Home Assistant `config/custom_components/` directory and restart

## Configuration

Settings → Devices & Services → Add Integration → "League of Legends"

You'll need:

- Region
- Riot ID (`gameName#tagLine`)
- Riot API key

The integration resolves your `puuid` automatically.
You don't need to look it up yourself.

### Options

Configurable after setup via the integration's "Configure" button:

- **Idle poll interval** — how often to check whether you're in a game when you're not (default 300s, minimum 60s).
- **Queue** — which queue counts toward win streak, games played, and last match result: all queues, ranked solo/duo (default), ranked flex, ARAM, or unranked.

## Entities

| Entity | Description |
|---|---|
| `binary_sensor.in_game` | Whether you're currently in a match |
| `sensor.rank` | Current tier + division (ranked queues only) |
| `sensor.league_points` | Current LP (ranked queues only) |
| `sensor.win_streak` | Signed win/loss streak — positive for wins, negative for losses |
| `sensor.games_played` | Games tracked since setup |
| `sensor.splits_games_played` | Games played this ranked split (ranked queues only) |
| `sensor.last_match_result` | Win/loss of your most recent match, with champion/KDA attributes |
| `event.rank_change` | Fires on promotion or demotion |

## Automation example

```yaml
automation:
  - alias: "Losing streak notification"
    trigger:
      - trigger: state
        entity_id: event.<your_summoner>_rank_change
        attribute: event_type
        to: "demotion"
    action:
      - action: notify.spouse_phone
        data:
          title: "Demoted"
          message: "Don't wait up"
```

## Limitations

- No true "online/offline" presence.
Riot's public API only exposes whether you're actively in a game, not client presence
- `in_game` can lag behind the real game state by up to your idle poll interval.
Riot also doesn't report a game as active until the loading screen starts, not during champ select
- Sensors reflect current state only... no dashboard trend/graphing support yet
- `games_played` doesn't retroactively count games played while Home Assistant was offline.. `splits_games_played` does, but only for the current split
- The "unranked" queue filter only counts Normal Draft games, not Blind Pick or Quickplay

## Privacy

Your Riot API key and Riot ID are entered through the Home Assistant UI and stored only in Home Assistant's local config. These are never sent anywhere except Riot's API.

## License

[Unlicense](LICENSE) — public domain.
