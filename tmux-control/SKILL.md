---
name: tmux-control
description: Control tmux sessions to monitor and manage background processes. Use when you need to check server logs, restart Rails/Sidekiq, view process output in other tmux panes/windows, or manage long-running development services.
allowed-tools:
  - Bash
---

# Tmux Session Control

Control tmux sessions to monitor background processes, check logs, and restart services like Rails server or Sidekiq.

## When to Use This Skill

- Check output/logs in another tmux pane or window (server errors, Sidekiq jobs)
- Restart development services (Rails server, Sidekiq, webpack)
- Send commands to background processes
- Monitor long-running tasks in other panes

## Essential Commands

### List Sessions and Windows

```bash
# List all sessions
tmux list-sessions

# List windows in current session
tmux list-windows

# List all panes in current window
tmux list-panes

# List panes across all windows with details
tmux list-panes -a -F "#{session_name}:#{window_index}.#{pane_index} #{window_name} #{pane_current_command}"
```

### Capture Pane Output

```bash
# Capture last N lines from a specific pane (most useful!)
# Format: session:window.pane or just window.pane for current session
tmux capture-pane -t <target> -p -S -50

# Examples:
tmux capture-pane -t 0:1.0 -p -S -100   # Last 100 lines from window 1, pane 0
tmux capture-pane -t server -p -S -50    # Last 50 lines from window named "server"
tmux capture-pane -t :1 -p -S -30        # Last 30 lines from window index 1

# Capture entire scrollback
tmux capture-pane -t <target> -p -S -
```

### Send Commands to Panes

```bash
# Send keys to a pane (simulates typing)
tmux send-keys -t <target> "command here" Enter

# Examples:
tmux send-keys -t server "bundle exec rails server" Enter
tmux send-keys -t sidekiq "bundle exec sidekiq" Enter

# Send Ctrl+C to stop a process
tmux send-keys -t <target> C-c

# Restart a service (stop then start)
tmux send-keys -t server C-c && sleep 1 && tmux send-keys -t server "bin/rails server" Enter
```

### Target Format Reference

Targets can be specified as:
- `session:window.pane` - Full path
- `:window.pane` - Current session
- `window.pane` - Current session
- `window` or `:window` - First pane of window
- `.pane` - Pane in current window

Windows can be referenced by:
- Index: `0`, `1`, `2`
- Name: `server`, `sidekiq`, `console`

## Workflow: Restart a Service

1. First, discover panes to find the target:
   ```bash
   tmux list-panes -a -F "#{session_name}:#{window_index}.#{pane_index} #{window_name} #{pane_current_command}"
   ```

2. Look for the process (e.g., `puma` for Rails server, `sidekiq` for Sidekiq)

3. Stop and restart:
   ```bash
   tmux send-keys -t TARGET C-c
   sleep 2
   tmux send-keys -t TARGET "bin/rails server" Enter
   ```

4. Verify:
   ```bash
   tmux capture-pane -t TARGET -p -S -20
   ```

### Check for Errors

```bash
tmux capture-pane -t TARGET -p -S -500 | grep -i -E "(error|exception|failed)"
```

## Tips

1. **Find your panes first**: Always run `tmux list-panes -a -F "..."` to identify targets
2. **Use window names**: Name your windows (`tmux rename-window server`) for easier targeting
3. **Capture enough lines**: Use `-S -100` or more to get sufficient context
4. **Wait after Ctrl+C**: Add `sleep 1-2` between stopping and starting services
5. **Check if process is running**: Capture pane and look for prompt vs running process
