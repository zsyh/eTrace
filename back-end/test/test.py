data = {"node":"1","nearby":[{"mac":"2","rssi":3}]}
nearby_process = []
for nearby in data['nearby']:
    nearby["mac"] = "5"

print data