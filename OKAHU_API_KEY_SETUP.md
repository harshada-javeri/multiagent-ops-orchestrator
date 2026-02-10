# Where to Add Okahu API Key

## Option 1: Environment Variable (Recommended)

```bash
# In your terminal
export OKAHU_API_KEY="okahu_your_api_key_here"
export MONOCLE_EXPORTER="okahu"

# Run your application
python predict.py '[ERROR] test FAILED'
```

## Option 2: .env File (Persistent)

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your key:
```bash
# Open in your editor
nano .env
# or
vim .env
# or
code .env
```

3. Update these lines:
```env
OKAHU_API_KEY=okahu_your_actual_key_here
MONOCLE_EXPORTER=okahu
```

4. Run your application (automatically loads .env):
```bash
python predict.py '[ERROR] test FAILED'
```

## Option 3: Docker Environment

```bash
docker run -e OKAHU_API_KEY="your-key" -e MONOCLE_EXPORTER="okahu" \
  -p 9696:9696 qaops-orchestrator
```

## Get Your Okahu API Key

1. Visit: https://app.okahu.ai/signup
2. Create account and verify email
3. Go to: **Settings** → **API Keys**
4. Click **Create New API Key**
5. Copy the key (starts with `okahu_`)

## Verify Setup

```bash
# Check if key is set
echo $OKAHU_API_KEY

# Should output: okahu_xxxxx...
```

## Test Tracing

```bash
# With Okahu export
export OKAHU_API_KEY="your-key"
export MONOCLE_EXPORTER="okahu"
python predict.py '[ERROR] test FAILED'

# View traces at: https://app.okahu.ai/traces
```

## File Locations

- **Environment variables**: Set in terminal or `.bashrc`/`.zshrc`
- **.env file**: `/path/to/multiagent-ops-orchestrator/.env`
- **Example file**: `.env.example` (template, don't edit directly)