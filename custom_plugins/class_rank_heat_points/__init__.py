''' Class ranking method: By points, favoring later heats in class '''

import logging
import RHUtils
from eventmanager import Evt
from RHRace import StartBehavior
from Results import RaceClassRankMethod

logger = logging.getLogger(__name__)

def rank_heat_points(rhapi, race_class, _args):
    heats = rhapi.db.heats_by_class(race_class.id)

    leaderboard = []
    ranked_pilots = []

    for heat in reversed(heats):
        heat_result = rhapi.db.heat_results(heat)
        if heat_result:
            heat_leaderboard = heat_result[heat_result['meta']['primary_leaderboard']]

            for line in heat_leaderboard:
                if line['pilot_id'] not in ranked_pilots:

                    leaderboard.append({
                        'pilot_id': line['pilot_id'],
                        'callsign': line['callsign'],
                        'team_name': line['team_name'],
                        'heat': heat.display_name,
                        'heat_id': heat.id,
                        'heat_points': line['points'],
                    })

                    ranked_pilots.append(line['pilot_id'])

    # determine ranking
    last_rank = None
    last_heat_points = None
    last_heat_id = None
    for i, row in enumerate(leaderboard, start=1):
        pos = i
        if last_heat_points == row['heat_points'] and last_heat_id == row['heat_id']:
            pos = last_rank
        last_rank = pos
        last_heat_points = row['heat_points']
        last_heat_id = row['heat_id']

        row['position'] = pos

    meta = {
        'rank_fields': [{
            'name': 'heat',
            'label': "Heat"
        },{
            'name': 'heat_points',
            'label': "Points"
        }]
    }

    return leaderboard, meta

def register_handlers(args):
    args['register_fn'](
        RaceClassRankMethod(
            "Last Heat Points",
            rank_heat_points,
            None,
            None
        )
    )

def initialize(rhapi):
    rhapi.events.on(Evt.CLASS_RANK_INITIALIZE, register_handlers)
