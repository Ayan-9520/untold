import { cloneDocument } from './document';

/** Undo/redo stack — engine-only, no React dependency. */
export class HistoryStack {
  constructor(limit = 50) {
    this.limit = limit;
    this.past = [];
    this.future = [];
  }

  push(state) {
    this.past.push(cloneDocument(state));
    if (this.past.length > this.limit) this.past.shift();
    this.future = [];
  }

  undo(current) {
    if (!this.past.length) return null;
    this.future.push(cloneDocument(current));
    return this.past.pop();
  }

  redo(current) {
    if (!this.future.length) return null;
    this.past.push(cloneDocument(current));
    return this.future.pop();
  }

  canUndo() {
    return this.past.length > 0;
  }

  canRedo() {
    return this.future.length > 0;
  }

  clear() {
    this.past = [];
    this.future = [];
  }
}
