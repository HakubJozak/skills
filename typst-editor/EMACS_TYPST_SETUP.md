# Doom Emacs + Typst Setup Complete! 🎉

## What Was Installed

1. **typst-ts-mode** - Tree-sitter based major mode for Typst
2. **tinymist** - Modern LSP server for Typst (v0.14.10)
3. **eglot** configuration - Built-in LSP client for Emacs

## Key Bindings in Typst Files

When editing `.typ` files, use these commands:

| Key Binding | Command | Description |
|-------------|---------|-------------|
| `SPC m w` | `typst-ts-mode-watch-toggle` | Toggle auto-compile on save |
| `SPC m p` | `typst-ts-mode-preview` | Open PDF preview |
| `SPC m c` | `typst-ts-mode-compile` | Compile to PDF once |
| `SPC m C` | `typst-ts-mode-compile-and-preview` | Compile and open preview |

## LSP Features Available

With tinymist LSP running, you get:

- **Code Completion** - Auto-complete for Typst functions and syntax
- **Hover Documentation** - Hover over functions to see documentation
- **Go to Definition** - Jump to where functions/variables are defined
- **Error Checking** - Real-time syntax and type checking
- **Formatting** - Format your Typst code

## Workflow

1. **Open a Typst file**: `emacs offer.typ`
2. **Enable watch mode**: `SPC m w` - Auto-compiles on save
3. **Edit and save**: Changes compile automatically
4. **View PDF**: `SPC m p` - Opens the generated PDF

## Tree-sitter Grammar

✅ **Already Installed!** The Typst tree-sitter grammar has been compiled and installed at:
```
~/.config/emacs/.local/cache/tree-sitter/libtree-sitter-typst.so
```

The config has been updated to load it automatically via `treesit-extra-load-path`.

## Testing It Out

Try opening your offer:

```bash
emacs ~/.config/emacs/offer/offer.typ
```

Then:
1. Press `SPC m w` to enable watch mode
2. Make a small edit and save
3. Press `SPC m p` to view the PDF

## Troubleshooting

**LSP not starting?**
- Check tinymist is in PATH: `which tinymist`
- Restart Emacs: `SPC q r`

**Tree-sitter grammar missing?**
- Run: `M-x typst-ts-mc-install-grammar`

**Preview not working?**
- Make sure you have a PDF viewer installed
- Check the compilation succeeded: `SPC m c`

## Files Modified

- `~/.config/doom/packages.el` - Added typst-ts-mode package
- `~/.config/doom/config.el` - Added Typst configuration
- `~/.cargo/bin/tinymist` - Installed LSP server

## Next Steps

To apply changes, restart Emacs or reload configuration:
- Restart: `SPC q r`
- Reload: `SPC h r r`

Enjoy writing Typst in Doom Emacs! 🚀

## Resources

- [Typst Documentation](https://typst.app/docs)
- [typst-ts-mode Wiki](https://codeberg.org/meow_king/typst-ts-mode/wiki)
- [Tinymist LSP Docs](https://myriad-dreamin.github.io/tinymist/)
