# OSM Alarm Handler

OSM alarm handler rules map is stored in `/etc/oah-map.json`. Example:
```
{
        "/default/alarm": {
                "handler": "BaseActionHandler"
        }
        "/app1/alarm": {
                "handler": "VcaActionHandler",
                "params": {
                    "vca_host": "osm",
                    "vca_model": "model1",
                    "vca_unit": "unit1",
                    "vca_action": "reboot"
                }

        }
}
```
