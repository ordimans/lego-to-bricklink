# LEGO to BrickLink Converter

[🇫🇷 Version française](README.fr.md)

Convert **LEGO Element IDs** (from LEGO instruction manuals) to **BrickLink-compatible XML** for importing a Wanted List.

Useful when you have an incomplete LEGO set and want to order missing parts on BrickLink.

## Features

- Converts LEGO Element IDs to BrickLink Part Numbers
- Automatically retrieves correct colors via BrickLink API
- Auto-aggregates duplicates (quantities are summed)
- Generates XML ready for BrickLink import
- No external dependencies (Python standard library only)

## Prerequisites

- Python 3.6+
- BrickLink API keys (free)

## Installation

```bash
git clone https://github.com/ordimans/lego-to-bricklink.git
cd lego-to-bricklink
```

## Configuration

### Get BrickLink API Keys

1. Log in to [BrickLink.com](https://www.bricklink.com)
2. Go to **My BrickLink > API** or directly: https://www.bricklink.com/v2/api/register_consumer.page
3. Create a new "Consumer Key"
4. Save the 4 keys provided

### Set Environment Variables

Copy the example file and fill in your keys:

```bash
cp .env.example .env
nano .env  # or your preferred editor
```

Then load the variables:

```bash
source .env
```

Or export them directly:

```bash
export BRICKLINK_CONSUMER_KEY=your_consumer_key
export BRICKLINK_CONSUMER_SECRET=your_consumer_secret
export BRICKLINK_TOKEN=your_token
export BRICKLINK_TOKEN_SECRET=your_token_secret
```

## Usage

### CSV File Format

Create a CSV file with Element IDs and quantities (semicolon separator):

```csv
element_id;quantity
4211221;1
4585493;2
4211412;4
```

Element IDs can be found in LEGO manuals, next to each part in the inventory list.

### Run the Conversion

```bash
python3 lego_to_bricklink.py input.csv output.xml
```

### Example

```bash
$ python3 lego_to_bricklink.py missing_parts.csv wanted_list.xml

Reading missing_parts.csv...
Found 40 unique element IDs

Querying BrickLink API...
----------------------------------------------------------------------
Element ID   Part No      Color    Qty    Status
----------------------------------------------------------------------
302223       3022         7        1      OK
306226       3062         11       1      OK
4211221      3660         88       1      OK
...
----------------------------------------------------------------------
Success: 40 | Errors: 0

XML saved to: wanted_list.xml
Total parts: 40
Total pieces: 61
```

### Import to BrickLink

1. Go to [BrickLink.com](https://www.bricklink.com)
2. **Want > Upload** or directly: https://www.bricklink.com/v2/wanted/upload.page
3. Select your XML file
4. Import!

## Project Structure

```
lego-to-bricklink/
├── lego_to_bricklink.py   # Main script
├── example_parts.csv      # Example CSV file
├── .env.example           # Environment variables template
├── .gitignore
├── README.md              # English documentation
└── README.fr.md           # French documentation
```

## How to Find Element IDs

Element IDs are the 6-7 digit numbers found:

- In **LEGO instruction manuals** (parts list at the end)
- On **LEGO parts bags**
- On the LEGO website in set inventories

Example in a LEGO manual:
```
Part: Slope, Inverted 45 2 x 2
Element ID: 4211221
```

## BrickLink API

This script uses the `/item_mapping/{element_id}` endpoint of the BrickLink API to convert LEGO Element IDs to:
- **Part Number** BrickLink (e.g., `3660`)
- **Color ID** BrickLink (e.g., `88` = Reddish Brown)

API Documentation: https://www.bricklink.com/v3/api.page

## License

MIT License - Do whatever you want with it!

## Contributing

PRs are welcome! If you find a bug or want to add a feature:

1. Fork the repo
2. Create a branch (`git checkout -b feature/my-feature`)
3. Commit (`git commit -m 'Add my feature'`)
4. Push (`git push origin feature/my-feature`)
5. Open a PR
