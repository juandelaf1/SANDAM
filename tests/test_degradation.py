'''Tests for User Story 3 - degradation on source failure (T020).

Verifican que ante un fallo de fuente no se inventan datos.
'''

import pytest


@pytest.mark.asyncio
async def test_predictions_unavailable_without_inventing(client, sample_beach):
    '''Las rutas sin metodo declaran indisponibilidad (no inventan).'''
    for path in ("/forecast", "/shade"):
        response = await client.get(
            "/api/v1/predictions{}/Platja de Palma".format(path)
        )
        body = response.json()
        assert body["status"] == "insufficient_data"
        assert "forecast" not in body or body.get("forecast") is None