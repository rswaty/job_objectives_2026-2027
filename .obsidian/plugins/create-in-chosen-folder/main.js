"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/main.ts
var main_exports = {};
__export(main_exports, {
  default: () => CreateInChosenFolderPlugin
});
module.exports = __toCommonJS(main_exports);

// node_modules/monkey-around/dist/index.mjs
function around(obj, factories) {
  const removers = Object.keys(factories).map((key) => around1(obj, key, factories[key]));
  return removers.length === 1 ? removers[0] : function() {
    removers.forEach((r) => r());
  };
}
function around1(obj, method, createWrapper) {
  const inherited = obj[method], hadOwn = obj.hasOwnProperty(method), original = hadOwn ? inherited : function() {
    return Object.getPrototypeOf(obj)[method].apply(this, arguments);
  };
  let current = createWrapper(original);
  if (inherited)
    Object.setPrototypeOf(current, inherited);
  Object.setPrototypeOf(wrapper, current);
  obj[method] = wrapper;
  return remove;
  function wrapper(...args) {
    if (current === original && obj[method] === wrapper)
      remove();
    return current.apply(this, args);
  }
  function remove() {
    if (obj[method] === wrapper) {
      if (hadOwn)
        obj[method] = original;
      else
        delete obj[method];
    }
    if (current === original)
      return;
    current = original;
    Object.setPrototypeOf(wrapper, inherited || Function);
  }
}

// src/main.ts
var import_obsidian = require("obsidian");
var DEFAULT_SETTINGS = {
  recentCount: 5
};
var NEW_FOLDER_PREFIX = "\0new:";
var FolderPickerModal = class extends import_obsidian.SuggestModal {
  constructor(app, noteName, recentCount, onPick) {
    super(app);
    this.recentCount = recentCount;
    this.onPick = onPick;
    this.chosen = false;
    this.recent = /* @__PURE__ */ new Set();
    this.setPlaceholder(`Choose a folder for "${noteName}" (type a new path to create it)`);
    this.setInstructions([
      { command: "\u2191\u2193", purpose: "navigate" },
      { command: "\u21B5", purpose: "create note here" },
      { command: "esc", purpose: "cancel" }
    ]);
  }
  getSuggestions(query) {
    const q = query.trim().toLowerCase();
    const allFolders = this.app.vault.getAllFolders(true);
    const lastCreated = /* @__PURE__ */ new Map();
    for (const folder of allFolders) {
      let newest = 0;
      for (const child of folder.children) {
        if (child instanceof import_obsidian.TFile) newest = Math.max(newest, child.stat.ctime);
      }
      if (newest > 0) lastCreated.set(folder.path, newest);
    }
    const recent = [...lastCreated.entries()].sort((a, b) => b[1] - a[1]).slice(0, this.recentCount).map(([path]) => path);
    this.recent = new Set(recent);
    const alphabetical = allFolders.map((f) => f.path).filter((p) => !this.recent.has(p)).sort((a, b) => a.localeCompare(b));
    const folders = [...recent, ...alphabetical];
    const matches = folders.filter((p) => p.toLowerCase().includes(q));
    const typed = (0, import_obsidian.normalizePath)(query.trim());
    if (query.trim() && !folders.some((p) => p.toLowerCase() === typed.toLowerCase())) {
      matches.push(NEW_FOLDER_PREFIX + typed);
    }
    return matches;
  }
  renderSuggestion(value, el) {
    if (value.startsWith(NEW_FOLDER_PREFIX)) {
      el.setText(`\u2795 Create folder "${value.slice(NEW_FOLDER_PREFIX.length)}"`);
    } else {
      el.setText(value === "/" ? "/ (vault root)" : value);
      if (this.recent.has(value)) {
        el.createSpan({ text: "recent", cls: "create-in-chosen-folder-recent" });
      }
    }
  }
  onChooseSuggestion(value) {
    this.chosen = true;
    this.onPick(value);
  }
  onClose() {
    super.onClose();
    window.setTimeout(() => {
      if (!this.chosen) this.onPick(null);
    }, 0);
  }
};
var CreateInChosenFolderPlugin = class extends import_obsidian.Plugin {
  constructor() {
    super(...arguments);
    this.settings = { ...DEFAULT_SETTINGS };
  }
  async onload() {
    await this.loadSettings();
    this.addSettingTab(new CreateInChosenFolderSettingTab(this.app, this));
    const promptAndCreate = (linkpath) => this.promptAndCreate(linkpath);
    const metadataCache = this.app.metadataCache;
    this.register(
      around(this.app.workspace, {
        openLinkText(original) {
          return async function(linktext, sourcePath, newLeaf, openViewState) {
            const linkpath = (0, import_obsidian.getLinkpath)(linktext);
            const exists = metadataCache.getFirstLinkpathDest(linkpath, sourcePath);
            if (exists || !linkpath) {
              return original.call(this, linktext, sourcePath, newLeaf, openViewState);
            }
            const created = await promptAndCreate(linkpath);
            if (!created) return;
            const subpath = linktext.slice(linkpath.length);
            return original.call(this, created + subpath, sourcePath, newLeaf, openViewState);
          };
        }
      })
    );
  }
  async loadSettings() {
    const data = await this.loadData();
    this.settings = { ...DEFAULT_SETTINGS, ...data };
  }
  async saveSettings() {
    await this.saveData(this.settings);
  }
  pickFolder(noteName) {
    return new Promise((resolve) => new FolderPickerModal(this.app, noteName, this.settings.recentCount, resolve).open());
  }
  /** Returns the created file's path, or null if cancelled. */
  async promptAndCreate(linkpath) {
    var _a;
    const baseName = (_a = linkpath.split("/").pop()) != null ? _a : linkpath;
    const choice = await this.pickFolder(baseName);
    if (choice === null) return null;
    let folder = choice.startsWith(NEW_FOLDER_PREFIX) ? choice.slice(NEW_FOLDER_PREFIX.length) : choice;
    folder = folder === "/" ? "" : (0, import_obsidian.normalizePath)(folder);
    try {
      if (folder && !this.app.vault.getFolderByPath(folder)) {
        await this.app.vault.createFolder(folder);
      }
      const fileName = baseName.endsWith(".md") ? baseName : `${baseName}.md`;
      const path = (0, import_obsidian.normalizePath)(folder ? `${folder}/${fileName}` : fileName);
      const file = await this.app.vault.create(path, "");
      return file.path;
    } catch (e) {
      new import_obsidian.Notice(`Could not create note: ${e instanceof Error ? e.message : e}`);
      return null;
    }
  }
};
var RECENT_NAME = "Number of recent folders";
var RECENT_DESC = "How many folders with the most recently created notes to show at the top of the picker. Set to 0 to disable.";
var CreateInChosenFolderSettingTab = class extends import_obsidian.PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }
  getSettingDefinitions() {
    return [
      {
        name: RECENT_NAME,
        desc: RECENT_DESC,
        control: { type: "slider", key: "recentCount", min: 0, max: 20, step: 1, defaultValue: DEFAULT_SETTINGS.recentCount }
      }
    ];
  }
  display() {
    const { containerEl } = this;
    containerEl.empty();
    new import_obsidian.Setting(containerEl).setName(RECENT_NAME).setDesc(RECENT_DESC).addSlider(
      (slider) => slider.setLimits(0, 20, 1).setValue(this.plugin.settings.recentCount).onChange(async (value) => {
        this.plugin.settings.recentCount = value;
        await this.plugin.saveSettings();
      })
    );
  }
};
