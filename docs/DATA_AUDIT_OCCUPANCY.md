# Auditoría de datos heredados (solo lectura, 2026-10-21)

- Base de datos local: inaccesible (ConnectionRefusedError). No se consultó producción.
- Schema actual: `current_occupation` Integer anulable (DB), default Python 0 (ORM), Pydantic 0..100.
- Seed (20 pares): ocupación entre 20 y 92, media ~54.5; max_capacity 1500-20000. NO son observaciones.
- Defaults: current_occupation=0, jellyfish_present=False, sargasso_level=0, posidonia_present=False.
- data_status: modelo por defecto unavailable; BeachCreate usa live; seed fuerza live (línea 536).
- Conclusión: ningún registro puede clasificarse como observación real en código versionado.
