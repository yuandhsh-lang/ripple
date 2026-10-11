"""Live external service evidence only; no fake rain and no Agent claim."""
import datetime,json,urllib.request
import converge as c
url='https://api.open-meteo.com/v1/forecast?latitude=31.23&longitude=121.47&hourly=weather_code,precipitation,precipitation_probability&forecast_days=7&timeformat=unixtime&timezone=GMT'
try:
    with urllib.request.urlopen(url,timeout=20) as r:raw=r.read();status=r.status
    p=c.E/'live-open-meteo-response.json';p.write_bytes(raw)
    data=json.loads(raw);h=data['hourly'];times=h['time']
    complete=all(times[i+1]-times[i]==3600 for i in range(len(times)-1)) and all(len(h[k])==len(times) for k in ['weather_code','precipitation','precipitation_probability'])
    c.save('live-weather-request.json',{'at_utc':c.now(),'classification':'LIVE_EXTERNAL_REQUEST_ONLY','command':['python','phase1/check_live_weather.py'],'url':url,'http_status':status,'requested_coordinates':[31.23,121.47],'returned_coordinates':[data['latitude'],data['longitude']],'utc_offset_seconds':data['utc_offset_seconds'],'returned_timezone':data['timezone'],'complete_hourly_intervals':complete,'time_range_epoch':[times[0],times[-1]],'response_sha256':c.sha(p),'slots_model_integration':'NOT TESTED'})
    print('LIVE Open-Meteo',status,'complete intervals',complete)
except Exception as e:
    c.save('live-weather-request.json',{'at_utc':c.now(),'classification':'LIVE_EXTERNAL_REQUEST_ONLY','url':url,'status':'BLOCKED','error':str(e)})
    print('LIVE Open-Meteo blocked',str(e))
