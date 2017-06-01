 select a.datetime, a.lat, a.lon, a.var as tair, b.var as tsoil, c.var as tsurf
 from microclim_tair as a
 inner join microclim_tsoil as b 
 	on a.datetime=b.datetime 
 	and a.lat = b.lat 
 	and a.lon = b.lon
 inner join microclim_tsurf as c
 	on a.datetime = c.datetime
 	and a.lat = c.lat
 	and a.lon = c.lon