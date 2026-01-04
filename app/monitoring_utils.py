from prometheus_client import (
    Counter,
    Histogram,
    Gauge
)

# Track translation requests by language pair and status
translation_requests_total = Counter(
    name='translation_requests_total',
    documentation='Total translation requests by language pair and status',
    labelnames=['translation_pair', 'status']
)

# Track total translations contained within a single request
translation_texts_histogram = Histogram(
    name='translation_texts_distribution',
    documentation='Distribution of texts within a single request by translation pair',
    labelnames=['translation_pair'],
    buckets=[1, 2, 5, 10, 20, 50]
)

# Track request latencies for predict endpoint by translation pair
predict_request_latency_histogram = Histogram(
    name='predict_request_duration_seconds',
    documentation=(
        'Distribution of request latencies for '
        'successful predict endpoint requests'
    ),
    labelnames=['translation_pair'],
    buckets=[0.1, 0.2, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Track total number of loaded models in memory
loaded_models_gauge = Gauge(
    name='loaded_translation_models_total',
    documentation='Total number of translation models currently loaded in memory'
)
