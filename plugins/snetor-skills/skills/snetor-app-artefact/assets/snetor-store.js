/* snetor-store:begin — paste as is; at deployment only the SNETOR_MODE line changes. */
// "demo": the page runs alone (a file, a Claude artifact), state stays in this browser.
// "server": the page is deployed on the Snetor platform, state is shared and versioned.
const SNETOR_MODE = "demo";
const snetorStore = (() => {
  const memory = {};
  const local = {
    get(key) {
      try { return JSON.parse(localStorage.getItem("snetor:" + key)) ?? memory[key] ?? null; }
      catch { return memory[key] ?? null; }
    },
    set(key, entry) {
      memory[key] = entry;
      try { localStorage.setItem("snetor:" + key, JSON.stringify(entry)); } catch { /* sandboxed */ }
    },
  };
  async function call(url, init) {
    const r = await fetch(url, init);
    const body = await r.json().catch(() => ({}));
    return { status: r.status, body };
  }
  // -> { utilisateur, nom, grade }, grade in "admin" | "writer" | "reader" | "aucun"
  async function me() {
    if (SNETOR_MODE !== "server") return { utilisateur: "demo", nom: "Mode démo", grade: "admin" };
    const { status, body } = await call("/api/moi");
    if (status !== 200) throw new Error("identity unavailable (" + status + ")");
    return body;
  }
  // -> { valeur, version }; version 0 means the key was never written.
  async function load(key) {
    if (SNETOR_MODE !== "server") return local.get(key) || { valeur: null, version: 0 };
    const { status, body } = await call("/api/etat/" + key);
    if (status !== 200) throw new Error("state unavailable (" + status + ")");
    return body;
  }
  // Pass the version you loaded. -> { ok: true, version }
  //   | { ok: false, conflict: { valeur, version, maj_par } }  someone saved in between: show who
  //   | { ok: false, forbidden: "<what to ask for>" }          read-only user
  async function save(key, valeur, version) {
    if (SNETOR_MODE !== "server") {
      const current = local.get(key) || { valeur: null, version: 0 };
      if (current.version !== version) return { ok: false, conflict: { ...current, maj_par: "another tab" } };
      local.set(key, { valeur, version: version + 1 });
      return { ok: true, version: version + 1 };
    }
    const { status, body } = await call("/api/etat/" + key, {
      method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ valeur, version }),
    });
    if (status === 200) return { ok: true, version: body.version };
    if (status === 409) return { ok: false, conflict: body };
    if (status === 403) return { ok: false, forbidden: body.detail || body.erreur };
    throw new Error("save failed (" + status + ")");
  }
  return { me, load, save };
})();
/* snetor-store:end */
