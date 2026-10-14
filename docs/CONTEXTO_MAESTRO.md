# 🏖️ SANDAM 2026 - CONTEXTO MAESTRO DEL PROYECTO

## 1. VISIÓN DEL PRODUCTO

**Nombre**: SANDAM - Sistema Inteligente de Playas de Mallorca  
**Tagline**: "La única app que necesitas para decidir a qué playa ir"  
**Valor único**: Datos reales + Predicción + Todo en una pantalla

---

## 2. DATOS IMPLEMENTADOS

### Playas (20) - Coordenadas Reales Mallorca
```
Platja de Palma (39.5345, 2.7175)
Cala Major (39.5638, 2.6272)
Portals Nous (39.5361, 2.5952)
Palmanova (39.5201, 2.5499)
Magaluf (39.5092, 2.5305)
Santa Ponça (39.4992, 2.4856)
Peguera (39.4783, 2.4527)
Cala Fornells (39.4711, 2.4397)
Camp de Mar (39.4568, 2.4186)
Port d'Andratx (39.4393, 2.3937)
Cala Conills (39.4203, 2.3784)
Cala Rajada (39.7406, 3.4652)
Cala Mesquida (39.7184, 3.4528)
Cala Agulla (39.6925, 3.4418)
Platja de Muro (39.8089, 3.2102)
Can Picafort (39.7667, 3.1497)
Cala San Vicente (39.8875, 3.0849)
Port de Pollença (39.9047, 3.0825)
Cala Millor (39.5983, 3.3737)
Cala Bona (39.5773, 3.3839)
```

---

## 3. MÓDULOS IMPLEMENTADOS

| Módulo | Archivo | Descripción |
|--------|---------|-------------|
| Distancia | `src/utils/distance.py` | Haversine entre coordenadas |
| Geoespacial | `src/utils/geopandas_processor.py` | GeoDataFrame de playas |
| Mapas | `src/utils/folium_mapper.py` | Mapas interactivos Folium |
| Gráficos | `src/utils/plotly_charts.py` | Visualizaciones Plotly |
| Predicciones | `src/utils/predictions.py` | Score Playa Ideal |
| API Playas | `src/api/beaches.py` | CRUD completo |
| API Predicciones | `src/api/predictions.py` | Endpoints de predicción |
| Integración AEMET | `src/integrations/aemet_client.py` | Cliente meteorología |
| Integración SOCIB | `src/integrations/socib_client.py` | Cliente oceanografía |
| Integración CAIB | `src/integrations/caib_uib_client.py` | Cliente datos abiertos |

---

## 4. PAIN POINTS DEL USUARIO (PRIORIDADES)

1. **Ocupación real** - No %, sino m² disponibles
2. **Predicción medusas** - Por viento/corrientes, no histórico
3. **Posidonia fresca vs seca** - Estado por satélite
4. **Viento por cala** - Micro-clima específico
5. **Sombras naturales** - Proyección acantilados
6. **Parking** - Disponibilidad real
7. **"Dónde voy ahora"** - GPS + tiempo + sol restante
8. **Alertas terral** - Insectos cuando viento tierra
9. **Todo en una pantalla** - Cero fricción

---

## 5. ALGORITMO "DÓNDE VOY AHORA"

```python
# INPUT: lat, lon del usuario + hora actual
# OUTPUT: Lista playal ordenadas por meritocracia

PARA CADA PLAYA:
  distancia = haversine(user_lat, user_lon, beach_lat, beach_lon)
  tiempo_viaje = distancia × factor_carretera
  
  sol_restante = atardecer (20:30) - hora_actual
  
  # Lógica de recomendación
  SI tiempo_viaje < (sol_restante - 60min):
    status = "recomendada"  # 🟢
  SI tiempo_viaje < sol_restante:
    status = "marginal"     # 🟡
  SI tiempo_viaje > sol_restante:
    status = "no_merece"    # 🔴
  
  # Score final incluye distancia
  score_final = beach_score × factor_distancia
  
ORDENAR por score_final (descendente)
FILTRAR: eliminar "no_merece"
```

---

## 6. PREDICCIÓN MEDUSAS (REGLAS)

```python
# Basado en: viento + corrientes + temperatura

SI viento_direccion == "NE" AND temperatura_agua > 24:
  riesgo = "ALTO"  # Viento arrastra medusas desde mar abierto

SI corrientes_desde_sur == True:
  riesgo = "ALTO"  # Corrientes traen medusas

SI viento_direccion == "SW":
  riesgo = "BAJO"  # Viento mar-tierra aleja medusas
```

---

## 7. FACTORES SCORE PLAYA IDEAL

| Factor | Peso | Descripción |
|--------|------|-------------|
| Ocupación | 30% | % espacio libre (100 - occupation) |
| Bandera | 30% | green=30, yellow=15, red=0 |
| Medusas | 20% | Sin medusas = 20 puntos |
| Calidad agua | 10% | excellent=10, good=7, poor=0 |
| Sostenibilidad | 10% | Servicios disponibles |
| Distancia | *BONUS | Factor multiplicador por cercania |

---

## 8. API KEYS CONFIGURADAS

- **AEMET**: Configurada en `.env` (rate limited)
- **SOCIB**: `fg1XJ43jxjkQ83o36VFcchho26I869v5` (acceso limitado)

---

## 9. FRONTEND REQUERIDO

- **Dashboard**: Dash mejorado con algoritmo "Dónde voy ahora"
- **Mapas**: Folium interactivo o Maplibre
- **UI**: Dark mode, score grande, filtros por distancia

---

## 10. IMPLEMENTACIÓN PRIORITARIA

### FASE 1: Backend Core
1. Algoritmo "Dónde voy ahora" con GPS
2. Añadir hora atardecer dinámico (consultar atardecer por fecha)
3. Factor distancia en score

### FASE 2: Datos Reales
4. Scraper UIB BeachCam (ocupación)
5. Predicción medusas con reglas
6. Micro-clima por cala

### FASE 3: Frontend
7. Dashboard interactivo mejorado
8. Mapa con filtros

---

## 11. ESTRUCTURA DEL PROYECTO

```
SANDAM/
├── src/
│   ├── api/
│   │   ├── beaches.py
│   │   ├── predictions.py
│   │   └── external_data.py
│   ├── utils/
│   │   ├── distance.py         # HAVERSINE ✅
│   │   ├── geopandas_processor.py  # GEOPANDAS ✅
│   │   ├── folium_mapper.py    # FOLIUM ✅
│   │   ├── plotly_charts.py    # PLOTLY ✅
│   │   └── predictions.py      # SCORE ✅
│   └── integrations/
│       ├── aemet_client.py
│       ├── socib_client.py
│       └── caib_uib_client.py
├── notebooks/
│   ├── dashboard_final.py
│   └── mapas_*.html
├── requirements.txt
└── .env
```

---

## 12. NOTAS IMPORTANTES

- Todas las coordenadas son de Mallorca real
- Haversine funciona correctamente
- Los mapas Folium están generados
- API responde en puerto 8004
- Dashboard Dash en puerto 8050

---

*Documento generado para参考 - SANDAM 2026*