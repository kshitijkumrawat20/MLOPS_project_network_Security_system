// Background service worker
console.log('Phishing Detector: Background service worker started');

// Initialize storage and context menu
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    sitesChecked: 0,
    threatsBlocked: 0,
    autoCheck: false
  });
  
  // Create context menu (check if API is available)
  if (chrome.contextMenus) {
    chrome.contextMenus.create({
      id: 'checkLink',
      title: 'Check this link for phishing',
      contexts: ['link']
    });
  }
  
  console.log('Extension installed successfully');
});

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkPage') {
    // Handle page check request
    console.log('Checking page:', request.url);
    sendResponse({ status: 'checking' });
  }
  
  return true;
});

// Show notification
function showNotification(title, message, isWarning = false) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: isWarning ? 'icons/icon128.png' : 'icons/icon128.png',
    title: title,
    message: message,
    priority: isWarning ? 2 : 1
  });
}

// Listen for tab updates (optional - for auto-checking)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    chrome.storage.local.get(['autoCheck'], (result) => {
      if (result.autoCheck) {
        // Auto-check the page
        console.log('Auto-checking:', tab.url);
      }
    });
  }
});

// Context menu click handler
if (chrome.contextMenus) {
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'checkLink') {
      console.log('Checking link:', info.linkUrl);
      showNotification('Phishing Check', 'Checking link...', false);
      // You can implement link checking logic here
    }
  });
}
