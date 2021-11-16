class Mappings:
    mapping_closed = {
                0:{'direction':'upleft',    'cent': 0, 'target':1},
                1:{'direction':'downright', 'cent': 0, 'target':0},
                2:{'direction': 'downleft', 'cent': 0, 'target':3},
                3:{'direction':'upright',   'cent': 0, 'target':2},

                4:{'direction':'upleft',    'cent': 2, 'target':5},
                5:{'direction':'downright', 'cent': 2, 'target':4},
                6:{'direction': 'downleft', 'cent': 2, 'target':7},
                7:{'direction':'upright',   'cent': 2, 'target':6},
    }

    mapping_open = {
                5:{'direction':'downleft',  'cent': 1, 'target':0},
                0:{'direction':'upright',   'cent': 1, 'target':5},
                7:{'direction':'upleft',    'cent': 1, 'target':2},
                2:{'direction':'downright', 'cent': 1, 'target':7},

                1:{'direction': 'downright', 'cent': 0, 'target':1},
                3:{'direction': 'upright', 'cent': 0, 'target':3},
                4:{'direction': 'upleft', 'cent': 2, 'target':4},
                6:{'direction': 'downleft', 'cent': 2, 'target':6},
    }

    mapping_half_open = {
                5:{'direction':'downleft',  'cent': 1, 'target':0},
                0:{'direction':'upright',   'cent': 1, 'target':5},

                7:{'direction':'upleft',  'cent': 1, 'target':7},
                2:{'direction':'downright',  'cent': 1, 'target':2},
                1:{'direction': 'downright', 'cent': 0, 'target':1},
                3:{'direction': 'upright', 'cent': 0, 'target':3},
                4:{'direction': 'upleft', 'cent': 2, 'target':4},
                6:{'direction': 'downleft', 'cent': 2, 'target':6},
    }

class KnotType:
    move2 = [Mappings.mapping_open]
    move4 = [Mappings.mapping_open, Mappings.mapping_closed, Mappings.mapping_open]
    move0 = [Mappings.mapping_open, Mappings.mapping_open]
    move1 = [Mappings.mapping_half_open]
    move3 = [Mappings.mapping_open, Mappings.mapping_closed, Mappings.mapping_half_open]
    startknot = []
