# Waveger Billboard API

A REST API service that powers the Waveger frontend with Billboard music charts data, featuring built-in Redis caching for improved performance and Apple Music integration.

## 🌐 Live API

The API is deployed and accessible at:

```
https://waveger-api.onrender.com
```

Example API call:

```
https://waveger-api.onrender.com/billboard_api.php?id=hot-100
```

## 📋 Overview

This service works as the backend API for the Waveger music application, providing seamless access to Billboard charts data via RapidAPI. It implements Redis caching to improve performance and reduce API calls for frequently accessed chart data. Additionally, it enriches the chart data with Apple Music information, including song previews and high-quality artwork.

## ✨ Features

- Access to Billboard music charts data (Hot-100, Billboard 200, etc.)
- Historical data access by specifying a week parameter
- Apple Music integration:
  - Song previews and high-resolution artwork
  - Direct links to Apple Music
  - Efficient parallel processing of music data
  - Automatic JWT token management
- Smart caching strategy:
  - Current charts checked for updates every Tuesday
  - Hourly rechecking on Tuesdays until new data appears
  - Fallback to cached data during API outages
  - Current charts cached for 1 week
  - Historical charts cached permanently
  - Apple Music search results cached for 24 hours
- Option to force-refresh data anytime
- Robust error handling:
  - Smart detection and management of API rate limits
  - Automatic fallback to cached data during API downtime
  - Clear informative error messages
  - 10-second timeout prevention for hanging requests

## 🛠️ Technologies Used

- **Backend**: Flask (Python) with application factory pattern
- **Caching**: Redis via Flask-Caching
- **Data Sources**:
  - Billboard Charts API on RapidAPI
  - Apple Music API
- **Authentication**: PyJWT for Apple Music API authentication
- **Concurrency**: ThreadPoolExecutor for parallel API requests
- **Deployment**: Render
- **Testing**: Pytest with freezegun for time-dependent tests

## 🏗️ Project Structure

```
backend/
  ├── app.py                # Application entry point with app factory
  ├── cache_extension.py    # Shared cache instance
  ├── requirements.txt      # Python dependencies
  ├── blueprints/
  │   └── billboard_api.py  # Billboard API and Apple Music integration
  └── tests/
      ├── conftest.py       # Pytest configuration and fixtures
      └── test_billboard_api.py  # Tests for the Billboard API
```

## 🔑 Environment Variables

The API requires the following environment variables:

| Variable               | Description                                              |
| ---------------------- | -------------------------------------------------------- |
| `RAPID_API_KEY`        | API key for Billboard Charts API on RapidAPI             |
| `REDIS_URL`            | URL for Redis cache instance                             |
| `APPLE_MUSIC_KEY_ID`   | Key ID from Apple Developer account                      |
| `APPLE_MUSIC_TEAM_ID`  | Team ID from Apple Developer account                     |
| `APPLE_MUSIC_AUTH_KEY` | Private key from Apple Developer account for JWT signing |

## 🧪 Testing

The API includes a comprehensive test suite built with pytest. The tests cover:

- API response handling for different chart types
- Caching behavior for both current and historical charts
- Tuesday refresh logic for chart updates
- Error handling and fallback strategies
- Rate limiting detection and management

To run the tests:

```cd /backend
python -m pytest
```

The test suite uses:

- **pytest**: For test framework and assertions
- **unittest.mock**: For mocking external API requests
- **freezegun**: For testing time-dependent logic like Tuesday updates

## 📚 API Documentation

### Get Chart Data

Retrieves data for a specified Billboard chart, optionally enriched with Apple Music data.

**Endpoint:** `GET /billboard_api.php`

**Query Parameters:**

| Parameter     | Required | Default   | Description                                                                                                                                                                                        |
| ------------- | -------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`          | No       | `hot-100` | The Billboard chart ID to retrieve data for                                                                                                                                                        |
| `week`        | No       | None      | A specific date to retrieve historical chart data (format: YYYY-MM-DD)                                                                                                                             |
| `refresh`     | No       | `false`   | Force refresh the cache for current charts (`true` or `false`). Note: Current charts automatically refresh on Tuesdays regardless of this parameter. Historical data is always cached permanently. |
| `apple_music` | No       | `true`    | Include Apple Music data with song previews and artwork (`true` or `false`).                                                                                                                       |

**Example Requests:**

- Get current Hot 100 chart:

```
GET https://waveger-api.onrender.com/billboard_api.php?id=hot-100
```

- Get Billboard 200 chart for a specific week:

```
GET https://waveger-api.onrender.com/billboard_api.php?id=billboard-200&week=2023-01-14
```

- Force refresh of cached chart data:

```
GET https://waveger-api.onrender.com/billboard_api.php?id=hot-100&refresh=true
```

- Get chart data without Apple Music integration:

```
GET https://waveger-api.onrender.com/billboard_api.php?id=hot-100&apple_music=false
```

**Response Format:**

```json
{
  "chart": {
    "name": "Hot 100",
    "date": "2023-04-29"
  },
  "entries": [
    {
      "position": 1,
      "title": "Last Night",
      "artist": "Morgan Wallen",
      "image": "https://charts-static.billboard.com/img/2023/01/morgan-wallen-nlt-last-night-mfj-180x180.jpg",
      "last_week": 1,
      "peak_position": 1,
      "weeks_on_chart": 16,
      "apple_music": {
        "id": "1665616144",
        "url": "https://music.apple.com/us/album/last-night/1665616095?i=1665616144",
        "preview_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview116/v4/ec/b4/34/ecb434d0-3bbd-9af9-1c6c-23a270d2257e/mzaf_7541350728059895426.plus.aac.p.m4a",
        "artwork_url": "https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/41/b0/00/41b000b2-1fb4-07c4-bf0f-5b66b525d089/196589559066.jpg/1000x1000bb.jpg"
      }
    }
    // More entries...
  ],
  "cached": true
}
```

During API issues, responses may include an additional field:

```json
{
  "chart": {
    /* chart data */
  },
  "entries": [
    /* chart entries */
  ],
  "cached": true,
  "note": "API rate limit exceeded, serving cached data"
}
```

**Response Fields:**

- `chart`: Information about the chart
  - `name`: The name of the chart
  - `date`: The date of the chart data
- `entries`: Array of chart entries
  - `position`: Current position on the chart
  - `title`: Song or album title
  - `artist`: Artist name
  - `image`: Cover art image URL
  - `last_week`: Position on the chart in the previous week
  - `peak_position`: Highest position achieved on the chart
  - `weeks_on_chart`: Number of weeks the entry has been on the chart
  - `apple_music`: (If requested) Apple Music data for the song
    - `id`: Apple Music song ID
    - `url`: Link to the song on Apple Music
    - `preview_url`: URL for audio preview
    - `artwork_url`: High-resolution artwork URL
- `cached`: Boolean indicating whether the response was served from cache
- `note`: (Optional) Explanation when serving cached data due to API issues

**Note:** The exact fields returned may vary depending on the Billboard API response.

## 🎵 Apple Music Integration

The API integrates with Apple Music to provide additional data for songs in the chart:

### Features

- **Song Previews**: 30-second high-quality audio previews for each song
- **High-Resolution Artwork**: Full-sized album artwork (1000x1000)
- **Direct Links**: Official Apple Music song URLs
- **Efficient Processing**: Uses parallel processing to minimize response time
- **Smart Caching**: Apple Music data is cached separately to prevent redundant API calls

### Implementation Details

- **Authentication**: Uses JWT authentication with Apple-issued credentials
- **Token Management**: Automatically handles token generation and renewal (12-hour validity)
- **Parallel Processing**: Uses ThreadPoolExecutor to process multiple songs simultaneously
- **Search Optimization**: Uses both song title and artist name for accurate matching
- **Separate Caching**: Apple Music search results are cached for 24 hours to reduce API load

## 📊 Available Charts

The API supports the following Billboard charts:

| Chart ID                        | Title                          |
| ------------------------------- | ------------------------------ |
| `hot-100`                       | Billboard Hot 100™             |
| `billboard-200`                 | Billboard 200™                 |
| `artist-100`                    | Billboard Artist 100           |
| `emerging-artists`              | Emerging Artists               |
| `streaming-songs`               | Streaming Songs                |
| `radio-songs`                   | Radio Songs                    |
| `digital-song-sales`            | Digital Song Sales             |
| `summer-songs`                  | Songs of the Summer            |
| `top-album-sales`               | Top Album Sales                |
| `top-streaming-albums`          | Top Streaming Albums           |
| `independent-albums`            | Independent Albums             |
| `vinyl-albums`                  | Vinyl Albums                   |
| `indie-store-album-sales`       | Indie Store Album Sales        |
| `billboard-u-s-afrobeats-songs` | Billboard U.S. Afrobeats Songs |

Additional charts may be available through the API. The `id` parameter in your API request should match the chart ID from this list.

## 🔍 Troubleshooting

If you encounter issues with the API:

1. **API Unavailable**: The service will automatically fall back to cached data if the Billboard API is experiencing downtime. Look for the `note` field in the response for details.

2. **Rate Limiting**: If you receive responses with a note about rate limiting, this means the upstream Billboard API has temporarily limited our requests. The system will automatically:

   - Serve cached data during the rate-limited period
   - Implement a 5-minute cooldown before trying the API again
   - Resume normal operations once the rate limit period expires

3. **Missing or Incomplete Data**: Billboard occasionally updates their chart structure, which may affect response formats.

4. **Missing Apple Music Data**: Not all songs may have matches in Apple Music. The API will still return Billboard data even if Apple Music data is missing.

5. **Error Response Codes**:
   - `503`: Service Unavailable - Indicates the Billboard API is unavailable or rate limited
   - `500`: Internal Server Error - Unexpected errors in processing
   - `504`: Gateway Timeout - Request to Billboard API timed out

For any persistent issues, please report them to the API maintainer.
