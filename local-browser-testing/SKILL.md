---
name: local-browser-testing
description: Test web features locally during development using browser automation. Use when verifying UI changes, testing form interactions, checking responsive design, validating JavaScript behavior, or confirming that new features work as expected in the browser. Supports Chrome and Playwright MCP servers for browser automation.
---

# Local Browser Testing

## Overview

Test web application features locally during development by automating browser interactions. This skill helps verify that UI changes work correctly, form submissions behave as expected, and JavaScript functionality operates properly.

## Testing Workflow

### 1. Navigate to the Page

The development server should already be running at `http://localhost:3001`.

Use Playwright MCP to navigate:

```
mcp__playwright__browser_navigate with url: http://localhost:3001/[path]
```

Example: `http://localhost:3001/admin/ftp_logs/dolby`

### 2. Login if Required

If the page requires authentication, login first:

- Email: `admin@example.com`
- Password: `heslo123`

Navigate to login page, fill credentials, and submit before accessing protected pages.

### 3. Take a Snapshot

Always take a snapshot first to see the page structure:

```
mcp__playwright__browser_snapshot
```

Snapshots show the accessibility tree with element refs that can be used for interactions.

### 4. Interact with Elements

Use the snapshot to identify elements by their `ref`, then interact:

- `mcp__playwright__browser_click` - Click elements
- `mcp__playwright__browser_type` - Type into fields
- `mcp__playwright__browser_select_option` - Select dropdown options
- `mcp__playwright__browser_fill_form` - Fill multiple fields at once

### 5. Verify Behavior

After interactions, verify the expected behavior:

- Take another snapshot to see DOM changes
- Check console messages: `mcp__playwright__browser_console_messages`
- Check network requests: `mcp__playwright__browser_network_requests`
- Verify URL changes for navigation/history updates
- Take screenshots: `mcp__playwright__browser_take_screenshot`

### 6. Test Multiple Scenarios

For comprehensive testing, test multiple scenarios:

- Different input values
- Edge cases (empty inputs, special characters)
- Browser back/forward navigation
- Responsive design at different viewport sizes

## Common Testing Patterns

### Testing Form Submissions

1. Navigate to page
2. Take snapshot
3. Fill form fields
4. Submit form (click button or trigger auto-submit)
5. Verify response (new snapshot, URL change, console messages)

### Testing Dropdowns with Auto-Submit

1. Navigate to page
2. Take snapshot to see current selected value
3. Change dropdown value
4. Verify form auto-submits
5. Check URL contains new query parameter
6. Verify filtered results appear

### Testing Browser History

1. Perform action that should update history
2. Check URL has changed
3. Use browser back: `mcp__playwright__browser_navigate_back`
4. Verify page state reverts correctly

### Testing Responsive Design

1. Resize browser: `mcp__playwright__browser_resize`
2. Common sizes: 1920x1080 (desktop), 768x1024 (tablet), 375x667 (mobile)
3. Take screenshots at each size
4. Verify layout adapts correctly

## Troubleshooting

**Server not responding:**
- Server runs on port 3001 (not 3000)
- Check server is actually running
- Review server logs for errors

**Element not found:**
- Take fresh snapshot (DOM may have changed)
- Verify element is visible (not hidden by CSS)
- Check for dynamic content loading delays

**Form not submitting:**
- Check console for JavaScript errors
- Verify Stimulus controller is registered
- Confirm data attributes are correct

**Browser automation errors:**
- Ensure Playwright MCP server is connected
- Try refreshing the page
- Check browser console for errors

## Quick Reference

**Portal URL:** `http://localhost:3001`
**Login credentials:** `admin@example.com` / `heslo123`
**Browser tool:** Playwright MCP (`mcp__playwright__*`)
