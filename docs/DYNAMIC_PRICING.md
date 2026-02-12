# Dynamic Pricing (Future Enhancement)

## Current Implementation

Prices are hardcoded in `src/selladomx/config.py`:

```python
CREDIT_PRICE_MXN = 2
CREDIT_PRICE_DISPLAY = f"${CREDIT_PRICE_MXN} MXN"
```

**Pros:**
- Simple, no API calls needed
- Works offline
- Fast UI rendering

**Cons:**
- Requires rebuild when prices change
- Can become outdated if users don't update

## Option 1: Fetch from API (Recommended for Scale)

Add to `src/selladomx/api/client.py`:

```python
def get_pricing(self) -> dict:
    """Get current pricing from API.

    Returns:
        dict: {
            "credit_price_mxn": 2,
            "credit_price_usd": 0.12,
            "bulk_discounts": [...]
        }
    """
    return self._request("GET", "/api/v1/pricing")
```

Update `config.py`:

```python
# Default pricing (fallback if API fails)
DEFAULT_CREDIT_PRICE_MXN = 2
DEFAULT_CREDIT_PRICE_DISPLAY = f"${DEFAULT_CREDIT_PRICE_MXN} MXN"
```

Cache pricing in `SettingsManager`:

```python
def get_cached_pricing(self) -> dict:
    """Get cached pricing (refreshed every 24h)."""
    cached = self.settings.value("pricing/data")
    last_update = self.settings.value("pricing/last_update")

    # Refresh if stale
    if not cached or is_stale(last_update):
        return self._fetch_and_cache_pricing()

    return cached
```

**Pros:**
- Always up-to-date
- Can show promotions/discounts
- Support multiple currencies

**Cons:**
- Requires internet connection
- Extra API call on startup
- Need fallback for offline mode

## Option 2: Bundled Pricing File

Create `assets/pricing.json`:

```json
{
  "version": "2024-01-15",
  "credit_price_mxn": 2,
  "credit_price_usd": 0.12,
  "last_updated": "2024-01-15T00:00:00Z"
}
```

Update via deployment/auto-updater:

```python
def load_pricing():
    pricing_path = get_assets_path() / "pricing.json"
    with open(pricing_path) as f:
        return json.load(f)
```

**Pros:**
- Works offline
- Can be updated without full rebuild
- Simple to implement

**Cons:**
- Still requires app update
- No real-time pricing

## Option 3: Hybrid (Best of Both)

Default to bundled pricing, fetch from API in background:

```python
class PricingManager:
    def __init__(self):
        # Load bundled pricing as default
        self.pricing = load_bundled_pricing()

        # Try to fetch latest in background
        self._refresh_async()

    def _refresh_async(self):
        """Fetch pricing from API without blocking UI."""
        worker = QThread()
        worker.finished.connect(self._on_pricing_updated)
        worker.start()

    def get_price_display(self) -> str:
        return f"${self.pricing['credit_price_mxn']} MXN"
```

**Pros:**
- Always works (bundled fallback)
- Fresh pricing when online
- Doesn't block startup

**Cons:**
- Most complex to implement

## Recommendation

**For MVP/Early Stage:** Keep hardcoded (current approach)
- Simple and reliable
- Easy to update manually
- No infrastructure needed

**For Growth/Scale:** Implement Option 3 (Hybrid)
- Update `config.py` only when shipping new versions
- Add API pricing endpoint
- Cache in QSettings with 24h TTL
- Show pricing in dialogs from cache

## Migration Path

1. Start with hardcoded (current) ✅
2. Add `/api/v1/pricing` endpoint (backend)
3. Implement caching in `SettingsManager`
4. Update UI to use cached pricing
5. Add background refresh on app start
6. Keep `config.py` as ultimate fallback

This way you can update prices instantly via API, but app still works if API is down.
