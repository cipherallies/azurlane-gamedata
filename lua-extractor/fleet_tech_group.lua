pg = {}
dofile(arg[1]);
local json = require('json.json')
print(json.encode(pg.fleet_tech_group))