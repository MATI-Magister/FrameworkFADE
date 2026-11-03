"""Component classifications from explicit, versioned bands; unknown is not zero."""
import math


def validate_reuse_bands(bands):
    if not isinstance(bands, list) or len(bands) != 4:
        raise ValueError('Se requieren cuatro bandas de reutilización.')
    if [b.get('label') for b in bands if isinstance(b, dict)] != ['R1', 'R2', 'R3', 'R4']:
        raise ValueError('Las bandas deben estar ordenadas R1, R2, R3, R4.')
    previous = None
    for band in bands:
        for key in ('minimum', 'maximum'):
            v = band.get(key)
            if type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 100:
                raise ValueError('Límites de reutilización entre 0 y 100 %.')
        if band['minimum'] >= band['maximum']:
            raise ValueError('Banda de reutilización vacía o invertida.')
        if any(type(band.get(k)) is not bool for k in ('include_minimum', 'include_maximum')):
            raise ValueError('Indicar inclusión de límites con booleanos.')
        if previous is not None:
            if previous['maximum'] != band['minimum'] or previous['include_maximum'] == band['include_minimum']:
                raise ValueError('Bandas de reutilización con hueco o superposición.')
        previous = band
    if bands[0]['minimum'] != 0 or not bands[0]['include_minimum'] or bands[-1]['maximum'] != 100 or not bands[-1]['include_maximum']:
        raise ValueError('Las bandas deben cubrir desde 0 hasta 100 %, incluidos.')


def classify_reuse(percentage, bands):
    validate_reuse_bands(bands)
    if percentage is None: return None
    if type(percentage) not in (int, float) or not math.isfinite(percentage) or not 0 <= percentage <= 100:
        raise ValueError('Porcentaje de reutilización: número entre 0 y 100 o null.')
    for band in bands:
        lower = percentage >= band['minimum'] if band['include_minimum'] else percentage > band['minimum']
        upper = percentage <= band['maximum'] if band['include_maximum'] else percentage < band['maximum']
        if lower and upper: return band['label']
    raise ValueError('Porcentaje sin banda de reutilización.')
