# Phishing Detector Browser Extension

ML-powered phishing detection extension for Chrome/Edge browsers.

## Features

- 🔍 **Real-time Detection**: Check websites as you browse
- 🛡️ **Manual URL Check**: Test any URL before visiting
- 📊 **Statistics**: Track sites checked and threats blocked
- ⚠️ **Visual Warnings**: Clear alerts for dangerous sites
- 🎯 **ML-Powered**: Uses trained model from API

## Installation

### Chrome/Edge:

1. Open browser and go to `chrome://extensions/` (or `edge://extensions/`)
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `browser-extension` folder
5. Extension will appear in your toolbar!

## Usage

### Automatic Check:
1. Click the extension icon on any website
2. See instant safety status of current site

### Manual Check:
1. Click extension icon
2. Enter any URL in "Check Any URL" field
3. Click "Check URL" button
4. Get instant results

### Context Menu:
- Right-click any link
- Select "Check this link for phishing"

## API Configuration

The extension connects to: `https://kshitijk20-nss.hf.space`

To change API URL:
1. Edit `popup.js`
2. Update `API_URL` constant
3. Reload extension

## Features Extracted

The extension automatically extracts 30 URL features:
- IP address detection
- URL length analysis
- SSL/HTTPS verification
- Subdomain analysis
- Suspicious patterns (@ symbol, redirects)
- Domain characteristics
- And 20+ more security indicators

## Statistics

The extension tracks:
- **Sites Checked**: Total websites analyzed
- **Threats Blocked**: Phishing sites detected

## Development

### File Structure:
```
browser-extension/
├── manifest.json      # Extension configuration
├── popup.html         # Extension popup UI
├── popup.js           # Popup logic
├── popup.css          # Popup styling
├── content.js         # Page content script
├── background.js      # Background service worker
└── icons/            # Extension icons
```

### To Test Changes:
1. Make your changes
2. Go to `chrome://extensions/`
3. Click reload button on the extension
4. Test the extension

## Privacy

- No data collection
- No tracking
- All checks go through your API
- Local statistics only

## Troubleshooting

**Extension not working:**
- Check if API is running: https://kshitijk20-nss.hf.space
- Check browser console for errors
- Reload extension

**False positives:**
- Model is trained on specific dataset
- Can be improved with more training data

**API errors:**
- Ensure HF Space is awake (not sleeping)
- Check network connection
- Verify API URL is correct

## Future Improvements

- [ ] Add settings page
- [ ] Enable/disable auto-check
- [ ] Whitelist trusted sites
- [ ] Export statistics
- [ ] Multi-language support
- [ ] Firefox version

## Support

For issues or questions:
- GitHub: Your repository
- API: https://kshitijk20-nss.hf.space/docs

## License

MIT License - Feel free to modify and distribute!
