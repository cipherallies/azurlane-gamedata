pg = {}
dofile(arg[1]);
local json = require('json.json')
print(json.encode(pg.skill_data_display))