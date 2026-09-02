
// Stimulus wrapper. Mounts the overlay into this element on every Turbo visit;
// re-anchors notes after frames/morphs swap the elements they point at.
// data-sticky-notes-key-value overrides the default key (location.pathname).
// Lives outside controllers/ so production never pins or loads it; the partial
// imports this module, which registers itself.
import { application } from "__APP_IMPORT__"

const REFRESH_EVENTS = ["turbo:frame-render", "turbo:morph"]

class StickyNotesController extends Controller {
  static values = { key: String }

  connect() {
    KZStickyNotes.mount({ key: this.keyValue || undefined, root: this.element })
    this.refresh = () => KZStickyNotes.refresh()
    this.teardown = () => KZStickyNotes.unmount()
    REFRESH_EVENTS.forEach((ev) => document.addEventListener(ev, this.refresh))
    document.addEventListener("turbo:before-cache", this.teardown)   // no outlines in the snapshot
  }

  disconnect() {
    REFRESH_EVENTS.forEach((ev) => document.removeEventListener(ev, this.refresh))
    document.removeEventListener("turbo:before-cache", this.teardown)
    KZStickyNotes.unmount()
  }
}

application.register("sticky-notes", StickyNotesController)
